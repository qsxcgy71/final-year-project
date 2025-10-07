"""Run MFA evaluation on FF++ c23 using local LLaVA model (with progress/resume support)."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from PIL import Image

from llava_quant import build as load_llava
from llava_quant import infer as llava_infer


@dataclass
class Question:
    qid: str
    category: str
    text_en: str
    text_zh: str

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Question":
        return cls(
            qid=data["id"],
            category=data["category"],
            text_en=data["question_en"],
            text_zh=data["question_zh"],
        )


@dataclass
class Counts:
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0
    yes_fake: int = 0
    yes_real: int = 0
    total_fake: int = 0
    total_real: int = 0

    def to_dict(self, ba: float) -> Dict[str, float | int]:
        return {
            "tp": self.tp,
            "tn": self.tn,
            "fp": self.fp,
            "fn": self.fn,
            "balanced_accuracy": round(ba, 4),
            "yes_rate_fake": round(self.yes_fake / self.total_fake, 4) if self.total_fake else 0.0,
            "yes_rate_real": round(self.yes_real / self.total_real, 4) if self.total_real else 0.0,
        }


@dataclass
class VideoQuestionStat:
    yes: int
    total: int
    prediction: bool

    def to_dict(self) -> Dict[str, int | bool]:
        return {"yes": self.yes, "total": self.total, "prediction": self.prediction}


@dataclass
class VideoRecord:
    video_key: str
    video_id: str
    label: int
    method: str
    split: str
    questions: Dict[str, VideoQuestionStat]

    def to_json(self) -> str:
        payload = {
            "video_key": self.video_key,
            "video_id": self.video_id,
            "label": self.label,
            "method": self.method,
            "split": self.split,
            "questions": {qid: stat.to_dict() for qid, stat in self.questions.items()},
        }
        return json.dumps(payload, ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> "VideoRecord":
        data = json.loads(line)
        questions = {
            qid: VideoQuestionStat(
                yes=stats.get("yes", 0),
                total=stats.get("total", 0),
                prediction=bool(stats.get("prediction", False)),
            )
            for qid, stats in data.get("questions", {}).items()
        }
        return cls(
            video_key=data["video_key"],
            video_id=data.get("video_id", data["video_key"]),
            label=int(data.get("label", 0)),
            method=data.get("method", ""),
            split=data.get("split", ""),
            questions=questions,
        )


def load_metadata(project_root: Path, split: str) -> List[Dict[str, str]]:
    metadata_path = project_root / "data" / "splits" / "ffpp_c23_split.json"
    with metadata_path.open("r", encoding="utf-8") as f:
        entries = json.load(f)
    return [e for e in entries if e["split"] == split]


def load_questions(path: Path) -> List[Question]:
    with path.open("r", encoding="utf-8-sig") as f:  # tolerate BOM
        data = json.load(f)
    return [Question.from_dict(item) for item in data]


def pick_frames(base_dir: Path, max_frames: int) -> List[Path]:
    frames = sorted(base_dir.glob("frame_*.jpg"))
    return frames[:max_frames]


def parse_yes_no(answer: str) -> Optional[bool]:
    text = answer.strip().lower()
    if not text:
        return None
    first = text.split()[0]
    if first in {"yes", "y", "yeah"}:
        return True
    if first in {"no", "n", "nope"}:
        return False

    # Chinese handling
    if text.startswith("是") or text.startswith("对"):
        return True
    if text.startswith("否") or text.startswith("不"):
        return False
    return None


def aggregate_answers(
    frames: List[Path],
    processor,
    model,
    device,
    question: Question,
    max_new_tokens: int,
) -> Tuple[int, int]:
    yes_count = 0
    total = 0
    for frame_path in frames:
        image = Image.open(frame_path).convert("RGB")
        answer = llava_infer(processor, model, device, image, question.text_en, max_new_tokens)
        verdict = parse_yes_no(answer)
        if verdict is None:
            continue
        total += 1
        if verdict:
            yes_count += 1
    return yes_count, total


def balanced_accuracy(tp: int, tn: int, fp: int, fn: int) -> float:
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return 0.5 * (sensitivity + specificity)


def load_progress(path: Path) -> Dict[str, VideoRecord]:
    if not path.exists():
        return {}
    progress: Dict[str, VideoRecord] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = VideoRecord.from_json(line)
            progress[record.video_key] = record
    return progress


def compute_results(records: Iterable[VideoRecord], questions: List[Question]) -> List[Dict[str, object]]:
    counts: Dict[str, Counts] = defaultdict(Counts)
    for record in records:
        label = int(record.label)
        for question in questions:
            stats = record.questions.get(question.qid)
            if not stats or stats.total == 0:
                continue
            prediction = bool(stats.prediction)
            c = counts[question.qid]
            if label == 1:
                c.total_fake += 1
                if prediction:
                    c.tp += 1
                    c.yes_fake += 1
                else:
                    c.fn += 1
            else:
                c.total_real += 1
                if prediction:
                    c.fp += 1
                    c.yes_real += 1
                else:
                    c.tn += 1

    results = []
    for question in questions:
        c = counts.get(question.qid, Counts())
        ba = balanced_accuracy(c.tp, c.tn, c.fp, c.fn)
        results.append(
            {
                "id": question.qid,
                "category": question.category,
                "question_en": question.text_en,
                "question_zh": question.text_zh,
                **c.to_dict(ba),
            }
        )

    results.sort(key=lambda x: x["balanced_accuracy"], reverse=True)
    return results


def resolve_path(base: Path, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run MFA with LLaVA on FF++ c23 faces")
    parser.add_argument("--split", choices=["train", "val", "test"], default="val")
    parser.add_argument("--model-dir", required=True, help="Path to local LLaVA model directory")
    parser.add_argument("--quant", choices=["none", "4bit", "8bit"], default="4bit")
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--frames-per-video", type=int, default=4)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--questions", default="config/mfa_questions.json")
    parser.add_argument("--output", default=None, help="Optional output prefix for reports")
    parser.add_argument(
        "--progress-log",
        default=None,
        help="Optional progress log (jsonl). Defaults to mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl",
    )
    parser.add_argument("--progress-interval", type=int, default=20, help="Print progress every N new videos")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]

    entries = load_metadata(project_root, args.split)
    if args.limit:
        entries = entries[: args.limit]

    questions = load_questions(project_root / args.questions)

    progress_default = f"mfa/ffpp_c23/mfa_ffpp_{args.split}_progress.jsonl"
    progress_path = resolve_path(project_root, args.progress_log or progress_default)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_records = load_progress(progress_path)
    processed_keys = set(progress_records.keys())

    total_entries = len(entries)
    already_done = len(processed_keys)
    if already_done:
        print(f"[MFA] found {already_done} previously processed videos in {progress_path}")

    processor, model, device = load_llava(args.model_dir, args.quant, args.max_new_tokens, force_cpu=False)

    new_processed = 0
    skipped_existing = 0
    skipped_missing = 0

    for idx, entry in enumerate(entries, 1):
        video_key = entry["path"]
        if video_key in processed_keys:
            skipped_existing += 1
            continue

        faces_dir = (
            project_root
            / "data"
            / "processed"
            / "ffpp_c23"
            / "faces_224"
            / entry["split"]
            / ("real" if entry["label"] == 0 else "fake")
            / entry["method"]
            / entry["video_id"]
        )
        if not faces_dir.exists():
            skipped_missing += 1
            continue
        frames = pick_frames(faces_dir, args.frames_per_video)
        if not frames:
            skipped_missing += 1
            continue

        label = int(entry["label"])
        question_stats: Dict[str, VideoQuestionStat] = {}
        for question in questions:
            yes_count, total = aggregate_answers(frames, processor, model, device, question, args.max_new_tokens)
            if total == 0:
                continue
            prediction = yes_count >= (total / 2)
            question_stats[question.qid] = VideoQuestionStat(yes=yes_count, total=total, prediction=prediction)

        # Even if no question had total>0 we still store record to avoid reprocessing next time
        record = VideoRecord(
            video_key=video_key,
            video_id=str(entry["video_id"]),
            label=label,
            method=str(entry["method"]),
            split=str(entry["split"]),
            questions=question_stats,
        )
        with progress_path.open("a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")
        progress_records[video_key] = record
        processed_keys.add(video_key)
        new_processed += 1

        if args.progress_interval and new_processed % args.progress_interval == 0:
            cumulative = len(progress_records)
            print(
                f"[MFA] processed new {new_processed}/{total_entries - skipped_existing} videos "
                f"(cumulative {cumulative}/{total_entries})"
            )

    results = compute_results(progress_records.values(), questions)

    output_prefix = resolve_path(project_root, args.output) if args.output else project_root / "mfa" / "ffpp_c23" / f"mfa_ffpp_{args.split}"
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    json_path = output_prefix.with_suffix(".json")
    csv_path = output_prefix.with_suffix(".csv")

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        headers = [
            "id",
            "category",
            "question_en",
            "question_zh",
            "balanced_accuracy",
            "tp",
            "tn",
            "fp",
            "fn",
            "yes_rate_fake",
            "yes_rate_real",
        ]
        f.write(",".join(headers) + "\n")
        for row in results:
            values = [str(row[h]) for h in headers]
            f.write(",".join(values) + "\n")

    print(
        f"Processed videos this run: {new_processed}, skipped existing: {skipped_existing}, "
        f"skipped missing: {skipped_missing}"
    )
    print(f"Total processed records in log: {len(progress_records)}")
    print(f"Results written to {json_path} and {csv_path}")
    print(f"Progress log saved at {progress_path}")


if __name__ == "__main__":
    main()
