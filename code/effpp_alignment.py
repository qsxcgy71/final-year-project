"""Build split-aware frame alignments and pair manifests for EFF++."""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

CACHE_ROOT = Path("data/effpp_cache")
CORE_METHODS = ["Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]
ORIGINAL_METHOD = "original"
ALL_METHODS = [ORIGINAL_METHOD, *CORE_METHODS]


@dataclass
class VideoInfo:
    video_id: str
    path: str
    split: str
    frame_count: int

    def to_json(self) -> Dict[str, object]:
        return {
            "video_id": self.video_id,
            "path": self.path.replace("\\", "/"),
            "split": self.split,
            "frame_count": self.frame_count,
        }


@dataclass
class IdentityRecord:
    identity: str
    frame_indices: List[int]
    min_length: int
    videos: Dict[str, VideoInfo]

    @property
    def primary_split(self) -> str:
        return self.videos[ORIGINAL_METHOD].split

    def to_json(self) -> Dict[str, object]:
        return {
            "identity": self.identity,
            "primary_split": self.primary_split,
            "min_length": self.min_length,
            "frame_indices": self.frame_indices,
            "videos": {method: info.to_json() for method, info in self.videos.items()},
        }


def load_split_metadata(project_root: Path) -> List[Dict[str, object]]:
    metadata_path = project_root / "data" / "splits" / "ffpp_c23_split.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing split metadata: {metadata_path}")
    with metadata_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_frame_counts(project_root: Path) -> Dict[str, Dict[str, int]]:
    csv_root = project_root / "data" / "ffpp_c23" / "csv"
    mapping: Dict[str, Dict[str, int]] = {}
    for method in CORE_METHODS + [ORIGINAL_METHOD]:
        filename = "original.csv" if method == ORIGINAL_METHOD else f"{method}.csv"
        path = csv_root / filename
        table: Dict[str, int] = {}
        with path.open("r", encoding="utf-8") as handle:
            header = handle.readline().strip().split(",")
            try:
                idx_file = header.index("File Path")
                idx_frames = header.index("Frame Count")
            except ValueError as exc:
                raise RuntimeError(f"Missing required columns in {filename}") from exc
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
    if length <= 0 or target_k <= 0:
        return []
    if target_k >= length:
        return list(range(length))
    if target_k == 1:
        return [0]
    step = (length - 1) / float(target_k - 1)
    indices: List[int] = []
    for rank in range(target_k):
        position = int(round(rank * step))
        if indices and position <= indices[-1]:
            position = min(indices[-1] + 1, length - 1)
        indices.append(position)
    return indices


def normalise_method(raw_method: str) -> str:
    if raw_method.lower() == "real":
        return ORIGINAL_METHOD
    return raw_method


def identity_from_video(method: str, video_id: str) -> str:
    if method == ORIGINAL_METHOD:
        return video_id
    return video_id.split("_")[0]


def build_identity_records(
    entries: Iterable[Dict[str, object]],
    frame_counts: Dict[str, Dict[str, int]],
    k: int,
    splits: List[str],
    identity_limit: int | None,
    seed: int,
) -> Tuple[List[IdentityRecord], Dict[str, int]]:
    grouped: Dict[str, Dict[str, Dict[str, object]]] = {}
    for entry in entries:
        method = normalise_method(str(entry["method"]))
        if method not in ALL_METHODS:
            continue
        video_id = str(entry["video_id"])
        identity = identity_from_video(method, video_id)
        grouped.setdefault(identity, {})[method] = {
            "video_id": video_id,
            "path": str(entry["path"]),
            "split": str(entry["split"]),
        }

    identities = sorted(grouped.keys())
    if identity_limit is not None:
        identities = identities[: identity_limit]

    rng = random.Random(seed)
    records: List[IdentityRecord] = []
    histogram: Dict[str, int] = defaultdict(int)

    for identity in identities:
        methods = grouped[identity]
        if any(method not in methods for method in ALL_METHODS):
            continue

        videos: Dict[str, VideoInfo] = {}
        min_length = math.inf
        for method in ALL_METHODS:
            video_meta = methods[method]
            video_id = video_meta["video_id"]
            split = video_meta["split"]
            counts_map = frame_counts.get(method, {})
            frame_count = counts_map.get(video_id)
            if frame_count is None:
                break
            videos[method] = VideoInfo(
                video_id=video_id,
                path=video_meta["path"],
                split=split,
                frame_count=frame_count,
            )
            min_length = min(min_length, frame_count)
        else:
            if not math.isfinite(min_length) or min_length <= 0:
                continue
            frame_indices = compute_frame_indices(int(min_length), k)
            primary_split = videos[ORIGINAL_METHOD].split
            if splits and primary_split not in splits:
                continue
            record = IdentityRecord(
                identity=identity,
                frame_indices=frame_indices,
                min_length=int(min_length),
                videos=videos,
            )
            records.append(record)
            histogram[primary_split] += 1
            continue
        # break executed -> missing frame count, skip identity
        continue

    rng.shuffle(records)
    return records, histogram


def raw_frame_root(project_root: Path, split: str) -> Path:
    return project_root / "data" / "processed" / "ffpp_c23" / "raw_frames" / split


def frame_directory(project_root: Path, method: str, info: VideoInfo) -> Path:
    root = raw_frame_root(project_root, info.split)
    if method == ORIGINAL_METHOD:
        return root / "real" / "real" / info.video_id
    return root / "fake" / method / info.video_id


def build_pair_payload(
    project_root: Path,
    record: IdentityRecord,
    method: str,
) -> Dict[str, object]:
    real_info = record.videos[ORIGINAL_METHOD]
    target_info = record.videos[method]
    real_dir = frame_directory(project_root, ORIGINAL_METHOD, real_info)
    target_dir = frame_directory(project_root, method, target_info)

    pairs: List[Dict[str, object]] = []
    missing_real = 0
    missing_target = 0
    for rank, frame_index in enumerate(record.frame_indices):
        real_frame = real_dir / f"frame_{frame_index:04d}.jpg"
        target_frame = target_dir / f"frame_{frame_index:04d}.jpg"
        if not real_frame.exists():
            missing_real += 1
            continue
        if not target_frame.exists():
            missing_target += 1
            continue
        real_frame_rel = real_frame.relative_to(project_root).as_posix()
        target_frame_rel = target_frame.relative_to(project_root).as_posix()
        pairs.append(
            {
                "pair_index": rank,
                "frame_index": frame_index,
                "real_frame": real_frame_rel,
                "target_frame": target_frame_rel,
            }
        )

    payload = {
        "identity": record.identity,
        "method": method,
        "target_split": target_info.split,
        "real_split": real_info.split,
        "real_video_id": real_info.video_id,
        "target_video_id": target_info.video_id,
        "pairs": pairs,
        "expected_pairs": len(record.frame_indices),
        "missing_real": missing_real,
        "missing_target": missing_target,
    }
    return payload


def write_outputs(
    project_root: Path,
    records: List[IdentityRecord],
    cache_root: Path,
    force: bool,
    k: int,
    histogram: Dict[str, int],
) -> None:
    frame_root = cache_root / "frame_indices"
    pair_root = cache_root / "pairs"

    if force:
        shutil.rmtree(frame_root, ignore_errors=True)
        shutil.rmtree(pair_root, ignore_errors=True)

    frame_root.mkdir(parents=True, exist_ok=True)
    pair_root.mkdir(parents=True, exist_ok=True)

    split_manifests: Dict[str, List[Dict[str, object]]] = defaultdict(list)

    for record in records:
        split = record.primary_split
        split_dir = frame_root / split
        split_dir.mkdir(parents=True, exist_ok=True)
        frame_path = split_dir / f"{record.identity}.json"
        frame_path.write_text(json.dumps(record.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")
        split_manifests[split].append(
            {
                "identity": record.identity,
                "frame_count": len(record.frame_indices),
                "min_length": record.min_length,
            }
        )

        # Pair manifests per method
        for method, info in record.videos.items():
            method_split = info.split
            method_dir = pair_root / method_split / method
            method_dir.mkdir(parents=True, exist_ok=True)
            pair_path = method_dir / f"{record.identity}.pairs.json"
            payload = build_pair_payload(project_root, record, method)
            pair_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write manifests per split
    for split, manifest in split_manifests.items():
        manifest_path = frame_root / split / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "total_identities": len(records),
        "k": k,
        "histogram": histogram,
        "splits": {
            split: {"identities": len(manifest), "frame_total": sum(item["frame_count"] for item in manifest)}
            for split, manifest in split_manifests.items()
        },
    }
    (frame_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build frame alignment and pair manifests for EFF++.")
    parser.add_argument("--splits", nargs="+", default=["train", "val", "test"], help="Target splits to include.")
    parser.add_argument("--k", type=int, default=128, help="Target number of aligned frames per identity.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for identity shuffling.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Optional limit on processed identities.")
    parser.add_argument("--cache-root", type=Path, default=CACHE_ROOT, help="EFF++ cache root storing outputs.")
    parser.add_argument("--force", action="store_true", help="Remove existing outputs before writing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]

    entries = load_split_metadata(project_root)
    frame_counts = load_frame_counts(project_root)

    records, histogram = build_identity_records(
        entries=entries,
        frame_counts=frame_counts,
        k=args.k,
        splits=args.splits,
        identity_limit=args.identity_limit,
        seed=args.seed,
    )

    write_outputs(
        project_root=project_root,
        records=records,
        cache_root=args.cache_root,
        force=args.force,
        k=args.k,
        histogram=histogram,
    )

    print(
        json.dumps(
            {
                "identities": len(records),
                "splits": histogram,
                "k": args.k,
                "cache_root": str(args.cache_root),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
