"""Metadata generation utilities for MFA experiments."""
from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class VideoEntry:
    video_id: str
    relpath: str
    label: int
    method: str
    compression: str = "c23"
    split: str = "unspecified"

    def to_dict(self) -> Dict[str, str]:
        return {
            "video_id": self.video_id,
            "path": self.relpath,
            "label": self.label,
            "method": self.method,
            "compression": self.compression,
            "split": self.split,
        }


CORE_METHODS = ["Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]
EXTRA_METHODS = ["FaceShifter", "DeepFakeDetection"]


def gather_videos(base: Path, subdir: str, label: int, method: str) -> List[VideoEntry]:
    entries: List[VideoEntry] = []
    target_dir = base / subdir
    if not target_dir.exists():
        return entries

    for video_path in sorted(target_dir.rglob("*.mp4")):
        video_id = video_path.stem
        relpath = str(video_path.relative_to(base.parent))
        entries.append(VideoEntry(video_id=video_id, relpath=relpath, label=label, method=method))
    return entries


def stratified_split(entries: Iterable[VideoEntry], train_ratio=0.8, val_ratio=0.1, seed: int = 42) -> List[VideoEntry]:
    grouped: Dict[str, List[VideoEntry]] = defaultdict(list)
    for item in entries:
        grouped[item.method].append(item)

    rng = random.Random(seed)
    split_entries: List[VideoEntry] = []

    for method, items in grouped.items():
        rng.shuffle(items)
        n = len(items)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        n_test = n - n_train - n_val

        if n_train == 0 and n > 0:
            n_train = 1
            n_test = n - n_train - n_val
        if n_val == 0 and n - n_train > 1:
            n_val = 1
            n_test = n - n_train - n_val
        if n_test < 0:
            n_test = 0

        train_items = items[:n_train]
        val_items = items[n_train:n_train + n_val]
        test_items = items[n_train + n_val:]

        for item in train_items:
            item.split = "train"
        for item in val_items:
            item.split = "val"
        for item in test_items:
            item.split = "test"

        split_entries.extend(items)
    return split_entries


def build_ffpp_metadata(project_root: Path) -> List[VideoEntry]:
    data_root = project_root / "data" / "ffpp_c23"
    if not data_root.exists():
        raise FileNotFoundError(f"FF++ c23 dataset not found at {data_root}")

    entries: List[VideoEntry] = []

    # Real videos
    entries.extend(gather_videos(data_root, "original", label=0, method="real"))

    # Core fake methods
    for method in CORE_METHODS:
        entries.extend(gather_videos(data_root, method, label=1, method=method))

    # Extra methods stored as split=extra for later analysis
    for method in EXTRA_METHODS:
        extras = gather_videos(data_root, method, label=1, method=method)
        for item in extras:
            item.split = "extra"
        entries.extend(extras)

    core_entries = [e for e in entries if e.method in CORE_METHODS + ["real"]]
    split_entries = stratified_split(core_entries)

    # Merge split assignments back
    assignment = {(e.video_id, e.method): e.split for e in split_entries}
    for entry in entries:
        key = (entry.video_id, entry.method)
        if key in assignment:
            entry.split = assignment[key]
        elif entry.split == "unspecified":
            entry.split = "extra"

    return entries


def summarize(entries: Iterable[VideoEntry]) -> Dict[str, Dict[str, int]]:
    summary: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for entry in entries:
        summary[entry.split][entry.method] += 1
    return summary


def write_json(entries: List[VideoEntry], output_path: Path) -> None:
    data = [entry.to_dict() for entry in entries]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_csv(entries: List[VideoEntry], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["video_id", "path", "label", "method", "compression", "split"])
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry.to_dict())


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    entries = build_ffpp_metadata(project_root)

    summary = summarize(entries)
    print("FF++ c23 video counts (by split/method):")
    for split, methods in sorted(summary.items()):
        total = sum(methods.values())
        method_counts = ", ".join(f"{method}={count}" for method, count in sorted(methods.items()))
        print(f"  {split}: {total} ({method_counts})")

    write_json(entries, project_root / "metadata" / "ffpp_c23_split.json")
    write_csv(entries, project_root / "metadata" / "ffpp_c23_split.csv")
    print("Metadata written to metadata/ffpp_c23_split.json and .csv")


if __name__ == "__main__":
    main()
