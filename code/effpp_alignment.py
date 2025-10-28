"""Build identity-level frame alignment for EFF++ annotations."""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

CORE_METHODS = ["Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]
REAL_METHOD = "real"


@dataclass
class VideoInfo:
    video_id: str
    path: str
    split: str
    frame_count: int


@dataclass
class IdentityRecord:
    identity: str
    videos: Dict[str, VideoInfo]
    min_length: int
    frame_indices: List[int]
    split_consistent: bool
    split_histogram: Dict[str, int]

    def to_json(self) -> Dict[str, object]:
        return {
            "identity": self.identity,
            "min_length": self.min_length,
            "frame_indices": self.frame_indices,
            "split_consistent": self.split_consistent,
            "split_histogram": self.split_histogram,
            "videos": {
                method: {
                    "video_id": info.video_id,
                    "path": info.path,
                    "split": info.split,
                    "frame_count": info.frame_count,
                }
                for method, info in self.videos.items()
            },
        }


def load_split_metadata(project_root: Path) -> List[Dict[str, object]]:
    metadata_path = project_root / "data" / "splits" / "ffpp_c23_split.json"
    with metadata_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_frame_counts(project_root: Path) -> Dict[str, Dict[str, int]]:
    csv_root = project_root / "data" / "ffpp_c23" / "csv"
    mapping: Dict[str, Dict[str, int]] = {}
    for method in CORE_METHODS + [REAL_METHOD]:
        filename = "original.csv" if method == REAL_METHOD else f"{method}.csv"
        path = csv_root / filename
        table: Dict[str, int] = {}
        with path.open("r", encoding="utf-8") as handle:
            header = handle.readline().strip().split(",")
            try:
                idx_file = header.index("File Path")
                idx_frames = header.index("Frame Count")
            except ValueError as exc:
                raise RuntimeError(f"Missing columns in {filename}") from exc
            for line in handle:
                parts = line.strip().split(",")
                if len(parts) <= max(idx_file, idx_frames):
                    continue
                file_path = parts[idx_file]
                frame_count = parts[idx_frames]
                if not frame_count.isdigit():
                    continue
                stem = Path(file_path).stem
                table[stem] = int(frame_count)
        mapping[method] = table
    return mapping


def compute_frame_indices(length: int, target_k: int) -> List[int]:
    if length <= 0:
        return []
    if target_k <= 0:
        return []
    if target_k >= length:
        return list(range(length))
    if target_k == 1:
        return [0]
    step = (length - 1) / (target_k - 1)
    result: List[int] = []
    for idx in range(target_k):
        position = int(round(idx * step))
        if result and position <= result[-1]:
            position = min(result[-1] + 1, length - 1)
        result.append(position)
    return result


def build_identity_records(
    project_root: Path,
    entries: List[Dict[str, object]],
    frame_counts: Dict[str, Dict[str, int]],
    target_k: int,
    require_consistent: bool,
    identity_limit: int | None,
    seed: int,
) -> Tuple[List[IdentityRecord], Dict[str, int]]:
    grouped: Dict[str, Dict[str, Dict[str, object]]] = {}
    for entry in entries:
        method = str(entry["method"])
        if method not in CORE_METHODS and method != REAL_METHOD:
            continue
        video_id = str(entry["video_id"])
        if method == REAL_METHOD:
            identity = video_id
        else:
            identity = video_id.split("_")[0]
        grouped.setdefault(identity, {}).setdefault(method, {})
        grouped[identity][method] = {
            "video_id": video_id,
            "path": str(entry["path"]),
            "split": str(entry["split"]),
        }

    rng = random.Random(seed)
    identities = sorted(grouped.keys())
    if identity_limit is not None:
        identities = identities[: identity_limit]

    records: List[IdentityRecord] = []
    split_histogram: Dict[str, int] = {}

    for identity in identities:
        methods = grouped[identity]
        if REAL_METHOD not in methods:
            continue
        if any(method not in methods for method in CORE_METHODS):
            continue
        videos: Dict[str, VideoInfo] = {}
        splits = []
        min_length = math.inf
        for method in [REAL_METHOD] + CORE_METHODS:
            info = methods[method]
            video_id = info["video_id"]
            split = info["split"]
            path = info["path"]
            frame_count = frame_counts.get(method, {}).get(video_id)
            if frame_count is None:
                continue
            videos[method] = VideoInfo(
                video_id=video_id,
                path=path,
                split=split,
                frame_count=frame_count,
            )
            splits.append(split)
            min_length = min(min_length, frame_count)
        if len(videos) != 1 + len(CORE_METHODS):
            continue
        if not math.isfinite(min_length) or min_length <= 0:
            continue
        split_consistent = len(set(splits)) == 1
        if require_consistent and not split_consistent:
            continue
        min_length = int(min_length)
        frame_indices = compute_frame_indices(min_length, target_k)
        record = IdentityRecord(
            identity=identity,
            videos=videos,
            min_length=min_length,
            frame_indices=frame_indices,
            split_consistent=split_consistent,
            split_histogram={split: splits.count(split) for split in set(splits)},
        )
        records.append(record)
        key = "same_split" if split_consistent else "cross_split"
        split_histogram[key] = split_histogram.get(key, 0) + 1
    rng.shuffle(records)
    return records, split_histogram


def write_outputs(records: List[IdentityRecord], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for record in records:
        identity_path = output_dir / f"{record.identity}.json"
        identity_path.write_text(json.dumps(record.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")
        manifest.append(
            {
                "identity": record.identity,
                "min_length": record.min_length,
                "frame_count": len(record.frame_indices),
                "split_consistent": record.split_consistent,
            }
        )
    summary_path = output_dir / "manifest.json"
    summary_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build identity-aligned frame indices for EFF++ annotations.")
    parser.add_argument("--k", type=int, default=128, help="Target number of aligned frames per identity.")
    parser.add_argument("--output-dir", default="data/effpp_cache/frame_indices", help="Output directory for alignment JSON files.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Optional limit on number of identities to process.")
    parser.add_argument("--require-consistent", action="store_true", help="Only keep identities whose videos share the same split.")
    parser.add_argument("--seed", type=int, default=2025, help="Seed used to shuffle output order.")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]

    entries = load_split_metadata(project_root)
    frame_counts = load_frame_counts(project_root)

    records, histogram = build_identity_records(
        project_root=project_root,
        entries=entries,
        frame_counts=frame_counts,
        target_k=args.k,
        require_consistent=args.require_consistent,
        identity_limit=args.identity_limit,
        seed=args.seed,
    )
    output_dir = project_root / args.output_dir
    write_outputs(records, output_dir)

    stats_path = output_dir / "summary.json"
    stats_payload = {
        "total_records": len(records),
        "histogram": histogram,
        "k": args.k,
    }
    stats_path.write_text(json.dumps(stats_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} identity alignment files to {output_dir}")
    print(json.dumps(stats_payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
