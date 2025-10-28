"""Generate face crops aligned across identities for EFF++ annotations."""
from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import cv2
import numpy as np

try:
    from insightface.app import FaceAnalysis
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "insightface is required. Install via `pip install insightface`."
    ) from exc


@dataclass
class CropResult:
    image: np.ndarray
    bbox: Tuple[int, int, int, int]
    det_score: float


class FaceCropper:
    """Thin wrapper around RetinaFace detection."""

    def __init__(self, det_size: int = 640, face_size: int = 224) -> None:
        self.det_size = det_size
        self.face_size = face_size
        try:
            import onnxruntime as ort

            available = ort.get_available_providers()
        except Exception:
            available = ["CPUExecutionProvider"]
        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if "CUDAExecutionProvider" in available
            else ["CPUExecutionProvider"]
        )
        ctx_id = 0 if "CUDAExecutionProvider" in providers else -1
        self.analyzer = FaceAnalysis(name="buffalo_l", providers=providers)
        self.analyzer.prepare(ctx_id=ctx_id, det_size=(det_size, det_size))

    def crop(self, frame_bgr: np.ndarray, margin_ratio: float) -> CropResult | None:
        faces = self.analyzer.get(frame_bgr[:, :, ::-1])  # convert to RGB for detector
        if not faces:
            return None
        face = max(faces, key=lambda item: item.det_score)
        x1, y1, x2, y2 = face.bbox.astype(int)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        base_size = max(x2 - x1, y2 - y1)
        scale = 1.0 + margin_ratio
        size = int(math.ceil(base_size * scale))
        h, w, _ = frame_bgr.shape
        left = max(0, int(cx - size / 2))
        top = max(0, int(cy - size / 2))
        right = min(w, left + size)
        bottom = min(h, top + size)
        crop = frame_bgr[top:bottom, left:right]
        if crop.size == 0:
            return None
        crop_resized = cv2.resize(crop, (self.face_size, self.face_size), interpolation=cv2.INTER_LINEAR)
        bbox = (int(left), int(top), int(right), int(bottom))
        return CropResult(image=crop_resized, bbox=bbox, det_score=float(face.det_score))


class MarginPlanner:
    def __init__(self, low: float, high: float, seed: int = 2025, fixed: float | None = None) -> None:
        self.low = low
        self.high = high
        self.fixed = fixed
        self.rng = random.Random(seed)
        self.cache: Dict[Tuple[str, int], float] = {}

    def margin(self, identity: str, frame_rank: int) -> float:
        if self.fixed is not None:
            return self.fixed
        key = (identity, frame_rank)
        if key not in self.cache:
            self.cache[key] = self.rng.uniform(self.low, self.high)
        return self.cache[key]


def load_identity_record(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_frame(capture: cv2.VideoCapture, frame_index: int) -> np.ndarray | None:
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    success, frame = capture.read()
    if not success:
        return None
    return frame


def process_video(
    project_root: Path,
    cropper: FaceCropper,
    margin_planner: MarginPlanner,
    identity: str,
    record: Dict[str, object],
    method: str,
    max_frames: int | None,
    output_root: Path,
) -> Dict[str, object]:
    video_info = record["videos"][method]
    video_rel = video_info["path"].replace("\\", "/")
    video_path = project_root / "data" / video_rel
    split = video_info["split"]
    frame_indices = record["frame_indices"]
    output_dir = output_root / split / identity / method
    output_dir.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return {"status": "failed", "reason": "open_error", "frames": 0}
    processed = 0
    failures: List[int] = []
    for rank, frame_index in enumerate(frame_indices):
        if max_frames is not None and rank >= max_frames:
            break
        frame = read_frame(capture, frame_index)
        if frame is None:
            failures.append(frame_index)
            continue
        margin_ratio = margin_planner.margin(identity, rank)
        result = cropper.crop(frame, margin_ratio)
        if result is None:
            failures.append(frame_index)
            continue
        frame_name = f"frame_{rank:04d}.jpg"
        meta_name = f"frame_{rank:04d}.json"
        cv2.imwrite(str(output_dir / frame_name), result.image)
        metadata = {
            "identity": identity,
            "method": method,
            "split": split,
            "frame_rank": rank,
            "frame_index": frame_index,
            "margin_ratio": margin_ratio,
            "bbox": list(result.bbox),
            "det_score": result.det_score,
            "video_id": video_info["video_id"],
            "video_path": video_rel,
        }
        (output_dir / meta_name).write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        processed += 1
    capture.release()
    return {
        "status": "ok" if processed else "empty",
        "processed": processed,
        "failures": failures,
        "output_dir": str(output_dir),
    }


def run_pipeline(args: argparse.Namespace) -> None:
    project_root = Path(__file__).resolve().parents[1]
    record_dir = project_root / args.frame_indices_dir
    output_root = project_root / args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    identity_files = sorted(record_dir.glob("*.json"))
    identity_map = {path.stem: path for path in identity_files if path.name not in {"manifest.json", "summary.json"}}

    target_identities = args.identities or sorted(identity_map.keys())
    if args.identity_limit is not None:
        target_identities = target_identities[: args.identity_limit]

    fixed_margin = args.fixed_margin if args.mode == "eval" else None
    margin_planner = MarginPlanner(
        low=args.random_margin_low,
        high=args.random_margin_high,
        seed=args.seed,
        fixed=fixed_margin,
    )
    cropper = FaceCropper(det_size=args.det_size, face_size=args.face_size)

    summary = {}
    for identity in target_identities:
        record_path = identity_map.get(identity)
        if not record_path:
            continue
        data = load_identity_record(record_path)
        results = {}
        for method in ["real", "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]:
            outcome = process_video(
                project_root=project_root,
                cropper=cropper,
                margin_planner=margin_planner,
                identity=identity,
                record=data,
                method=method,
                max_frames=args.max_frames,
                output_root=output_root,
            )
            results[method] = outcome
        summary[identity] = results
        print(f"Identity {identity}: {results['real']['processed']} frames for real")
    (output_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate aligned face crops for EFF++ annotations.")
    parser.add_argument("--frame-indices-dir", default="data/effpp_cache/frame_indices", help="Directory with identity alignment JSON files.")
    parser.add_argument("--output-dir", default="data/effpp_cache/crops", help="Directory to store cropped faces and metadata.")
    parser.add_argument("--identities", nargs="*", help="Optional list of identities to process.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Optional limit on number of identities.")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit number of frames per identity.")
    parser.add_argument("--mode", choices=["train", "eval"], default="train", help="Crop mode: train=random margins, eval=fixed.")
    parser.add_argument("--random-margin-low", type=float, default=0.04, help="Lower bound for random margin ratio.")
    parser.add_argument("--random-margin-high", type=float, default=0.20, help="Upper bound for random margin ratio.")
    parser.add_argument("--fixed-margin", type=float, default=0.125, help="Fixed margin ratio when mode=eval.")
    parser.add_argument("--det-size", type=int, default=640, help="Detector input size.")
    parser.add_argument("--face-size", type=int, default=224, help="Output face size.")
    parser.add_argument("--seed", type=int, default=2025, help="RNG seed.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()
