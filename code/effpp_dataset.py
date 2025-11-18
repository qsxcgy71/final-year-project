"""
EFF++ frame-level dataset utilities.

Provides:
- EffppFrameSample dataclass describing a single frame pair.
- EffppFrameDataset (PyTorch-style Dataset) for loading annotations + image paths.
- CLI helpers to preview dataset statistics.

Assumes annotations reside under `data/effpp_ann/<split>/<method>/<identity>/frame_xxxx.ann.json`
and that the annotation `pair.target_frame_path` field points to the cropped image.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

try:
    from PIL import Image  # type: ignore
except ImportError:  # pragma: no cover
    Image = None  # type: ignore

try:
    import torch
    from torch.utils.data import Dataset  # type: ignore
except (ImportError, OSError):  # pragma: no cover
    torch = None  # type: ignore
    Dataset = object  # type: ignore


SUPPORTED_METHODS = ["original", "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]


@dataclass
class EffppFrameSample:
    """Container for a single EFF++ frame annotation."""

    split: str
    method: str
    identity: str
    frame_rank: int
    frame_index: int
    annotation_path: Path
    image_path: Path
    annotation: Dict[str, object]

    def as_dict(self) -> Dict[str, object]:
        return {
            "split": self.split,
            "method": self.method,
            "identity": self.identity,
            "frame_rank": self.frame_rank,
            "frame_index": self.frame_index,
            "annotation_path": str(self.annotation_path),
            "image_path": str(self.image_path),
            "annotation": self.annotation,
        }


def _iter_annotation_files(base_dir: Path, split: str) -> Iterator[Path]:
    split_dir = base_dir / split
    if not split_dir.exists():
        return iter([])
    for method_dir in sorted(split_dir.iterdir()):
        if not method_dir.is_dir():
            continue
        for identity_dir in sorted(method_dir.iterdir()):
            if not identity_dir.is_dir():
                continue
            yield from sorted(identity_dir.glob("frame_*.ann.json"))


def load_annotation(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class EffppFrameDataset(Dataset):  # type: ignore[misc]
    """Torch-style dataset wrapping EFF++ annotation files."""

    def __init__(
        self,
        project_root: Path,
        split: str = "train",
        methods: Optional[Iterable[str]] = None,
        identities: Optional[Iterable[str]] = None,
        load_image: bool = False,
    ) -> None:
        if split not in {"train", "val", "test"}:
            raise ValueError(f"Unsupported split: {split}")
        self.project_root = project_root
        self.split = split
        self.base_dir = project_root / "data" / "effpp_ann"
        if not self.base_dir.exists():
            raise FileNotFoundError(f"EFF++ annotations not found at {self.base_dir}")
        self.methods = set(methods) if methods else set(SUPPORTED_METHODS)
        self.identities = set(identities) if identities else None
        self.load_image = load_image
        if load_image and Image is None:
            raise ImportError("Pillow (PIL) is required when load_image=True")

        self.samples: List[EffppFrameSample] = []
        for ann_path in _iter_annotation_files(self.base_dir, split):
            parts = ann_path.relative_to(self.base_dir).parts
            raw_method, identity, filename = parts[1], parts[2], parts[3]
            method = "original" if raw_method == "real" else raw_method
            if method not in self.methods:
                continue
            if self.identities is not None and identity not in self.identities:
                continue

            annotation = load_annotation(ann_path)
            pair = annotation.get("pair", {})
            frame_rank = int(pair.get("frame_rank", filename.split("_")[1].split(".")[0]))
            frame_index = int(pair.get("frame_index", -1))
            image_rel = pair.get("target_frame_path")
            if not image_rel:
                continue
            image_path = (self.project_root / image_rel).resolve()
            self.samples.append(
                EffppFrameSample(
                    split=split,
                    method=method,
                    identity=identity,
                    frame_rank=frame_rank,
                    frame_index=frame_index,
                    annotation_path=ann_path,
                    image_path=image_path,
                    annotation=annotation,
                )
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, object]:
        sample = self.samples[index]
        result = sample.as_dict()
        if self.load_image:
            image = Image.open(sample.image_path).convert("RGB")
            result["image"] = image
        return result


def summarize_dataset(dataset: EffppFrameDataset) -> Dict[str, object]:
    totals: Dict[str, int] = {}
    for sample in dataset.samples:
        key = f"{sample.split}/{sample.method}"
        totals[key] = totals.get(key, 0) + 1
    identities = {sample.identity for sample in dataset.samples}
    return {
        "split": dataset.split,
        "num_samples": len(dataset),
        "num_identities": len(identities),
        "counts_by_split_method": totals,
    }


def _main() -> None:
    import argparse
    import json as json_module

    parser = argparse.ArgumentParser(description="Preview EFF++ frame dataset.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--split", choices=["train", "val", "test"], default="train")
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--identities", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=5, help="Number of samples to preview")
    parser.add_argument("--show-image", action="store_true", help="Attempt to load images (requires PIL)")

    args = parser.parse_args()
    dataset = EffppFrameDataset(
        project_root=args.project_root,
        split=args.split,
        methods=args.methods,
        identities=args.identities,
        load_image=args.show_image,
    )
    summary = summarize_dataset(dataset)
    print(json_module.dumps(summary, ensure_ascii=False, indent=2))
    for idx, sample in enumerate(dataset.samples[: args.limit]):
        payload = sample.as_dict()
        if args.show_image and Image is not None:
            payload["image_size"] = Image.open(sample.image_path).size
        print(json_module.dumps(payload, ensure_ascii=False, indent=2))
        print("-" * 40)


if __name__ == "__main__":
    _main()
