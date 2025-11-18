"""Generate a concise QA panel for EFF++ alignment and annotations."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

METHOD_ORDER = ["original", "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]


def load_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_identities(annotations_root: Path, split: str) -> List[str]:
    split_root = annotations_root / split / "original"
    if not split_root.exists():
        return []
    return sorted([dir_.name for dir_ in split_root.iterdir() if dir_.is_dir()])


def sample_identities(
    annotations_root: Path,
    frame_index_root: Path,
    split: str,
    n_identities: int,
    rng: random.Random,
) -> List[str]:
    identities = collect_identities(annotations_root, split)
    rng.shuffle(identities)
    selected: List[str] = []
    for identity in identities:
        frame_index_path = frame_index_root / split / f"{identity}.json"
        if frame_index_path.exists():
            selected.append(identity)
        if len(selected) >= n_identities:
            break
    return selected


def gather_rows(
    project_root: Path,
    annotations_root: Path,
    split: str,
    identity: str,
    frames_per_identity: int,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for method in METHOD_ORDER:
        method_dir = annotations_root / split / method / identity
        if not method_dir.exists():
            continue
        annotations = sorted(method_dir.glob("frame_*.ann.json"))
        for ann_path in annotations[:frames_per_identity]:
            ann = load_json(ann_path)
            pair = ann.get("pair", {})
            real_rel = ""
            target_rel = ""
            if pair.get("real_frame_path"):
                real_candidate = (project_root / pair["real_frame_path"]).resolve()
                try:
                    real_rel = real_candidate.relative_to(project_root).as_posix()
                except ValueError:
                    real_rel = real_candidate.as_posix()
            if pair.get("target_frame_path"):
                target_candidate = (project_root / pair["target_frame_path"]).resolve()
                try:
                    target_rel = target_candidate.relative_to(project_root).as_posix()
                except ValueError:
                    target_rel = target_candidate.as_posix()
            rows.append(
                {
                    "rank": int(pair.get("frame_rank", ann_path.stem.split("_")[1])),
                    "method": method,
                    "answer": ann.get("a", ""),
                    "technique_summary": ann.get("technique_summary", ""),
                    "real_frame": real_rel,
                    "target_frame": target_rel,
                }
            )
    rows.sort(key=lambda item: (item["rank"], METHOD_ORDER.index(item["method"]) if item["method"] in METHOD_ORDER else 99))
    return rows


def write_report(
    output_path: Path,
    project_root: Path,
    annotations_root: Path,
    frame_index_root: Path,
    splits: List[str],
    n_identities: int,
    frames_per_identity: int,
    seed: int,
) -> None:
    rng = random.Random(seed)
    lines: List[str] = []
    lines.append("# EFF++ Alignment QA Panel")
    lines.append("")
    lines.append(f"- Seed: {seed}")
    lines.append(f"- Frames per identity: {frames_per_identity}")
    lines.append(f"- Methods: {', '.join(METHOD_ORDER)}")
    lines.append("")

    for split in splits:
        selected = sample_identities(annotations_root, frame_index_root, split, n_identities, rng)
        if not selected:
            lines.append(f"## Split `{split}` — no eligible identities found")
            lines.append("")
            continue
        lines.append(f"## Split `{split}`")
        lines.append("")
        for identity in selected:
            frame_index_path = frame_index_root / split / f"{identity}.json"
            record = load_json(frame_index_path)
            frame_count = len(record.get("frame_indices", []))
            lines.append(f"### Identity `{identity}`")
            lines.append(f"- Frame indices: {frame_count}")
            method_presence = []
            for method in METHOD_ORDER:
                status = "✓" if method in record.get("videos", {}) else "✗"
                method_presence.append(f"{method}:{status}")
            lines.append(f"- Methods: {' | '.join(method_presence)}")
            rows = gather_rows(project_root, annotations_root, split, identity, frames_per_identity)
            if not rows:
                lines.append("  - No annotation rows available.")
                lines.append("")
                continue
            lines.append("")
            lines.append("| Rank | Method | Answer | Technique | Real Frame | Target Frame |")
            lines.append("| --- | --- | --- | --- | --- | --- |")
            for row in rows:
                lines.append(
                    f"| {row['rank']} | {row['method']} | {row['answer']} | {row['technique_summary']} | "
                    f"{row['real_frame']} | {row['target_frame']} |"
                )
            lines.append("")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a markdown QA panel for EFF++ alignment.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--annotations-dir", type=Path, default=Path("data/effpp_ann"))
    parser.add_argument("--frame-indices-dir", type=Path, default=Path("data/effpp_cache/frame_indices"))
    parser.add_argument("--output", type=Path, default=Path("reports/effpp_alignment_report.md"))
    parser.add_argument("--splits", nargs="+", default=["train", "val", "test"])
    parser.add_argument("--n-identities", type=int, default=5)
    parser.add_argument("--frames-per-identity", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    annotations_root = (project_root / args.annotations_dir).resolve()
    frame_index_root = (project_root / args.frame_indices_dir).resolve()
    output_path = (project_root / args.output).resolve()
    write_report(
        output_path=output_path,
        project_root=project_root,
        annotations_root=annotations_root,
        frame_index_root=frame_index_root,
        splits=args.splits,
        n_identities=args.n_identities,
        frames_per_identity=args.frames_per_identity,
        seed=args.seed,
    )
    print(f"Wrote QA panel to {output_path}")


if __name__ == "__main__":
    main()
