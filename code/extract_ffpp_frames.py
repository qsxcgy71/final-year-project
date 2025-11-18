"""Frame extraction and face cropping for FF++ dataset using RetinaFace."""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
import torch

try:
    from insightface.app import FaceAnalysis
except ImportError as exc:  # pragma: no cover - runtime guard
    raise ImportError(
        "insightface is required for RetinaFace extraction. Please install insightface (pip install insightface)."
    ) from exc


@dataclass
class ExtractionConfig:
    fps: float = 2.0
    max_frames: int = 16
    face_size: int = 224
    face_margin: float = 1.2
    det_size: int = 640
    save_raw: bool = True
    output_root: Path = Path("data/processed/ffpp_c23")


class RetinaFaceExtractor:
    def __init__(self, config: ExtractionConfig) -> None:
        self.config = config
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if torch.cuda.is_available() else ["CPUExecutionProvider"]
        ctx_id = 0 if torch.cuda.is_available() else -1
        self.analyzer = FaceAnalysis(name="buffalo_l", providers=providers)
        self.analyzer.prepare(ctx_id=ctx_id, det_size=(config.det_size, config.det_size))

    def _extract_face(self, frame_bgr: np.ndarray) -> Optional[np.ndarray]:
        faces = self.analyzer.get(frame_bgr[:, :, ::-1])  # convert to RGB
        if not faces:
            return None
        face = max(faces, key=lambda f: f.det_score)
        x1, y1, x2, y2 = face.bbox.astype(int)

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        size = max(x2 - x1, y2 - y1) * self.config.face_margin
        size = int(size)

        h, w, _ = frame_bgr.shape
        left = max(0, int(cx - size / 2))
        top = max(0, int(cy - size / 2))
        right = min(w, left + size)
        bottom = min(h, top + size)

        crop = frame_bgr[top:bottom, left:right]
        if crop.size == 0:
            return None
        crop = cv2.resize(crop, (self.config.face_size, self.config.face_size), interpolation=cv2.INTER_LINEAR)
        return crop

    def process_video(self, video_path: Path, faces_dir: Path, raw_dir: Optional[Path] = None) -> Dict[str, int | str]:
        faces_dir.mkdir(parents=True, exist_ok=True)
        if raw_dir is not None:
            raw_dir.mkdir(parents=True, exist_ok=True)

        capture = cv2.VideoCapture(str(video_path))
        if not capture.isOpened():
            return {"status": "failed", "reason": "cannot_open", "faces": 0, "raw": 0}

        source_fps = capture.get(cv2.CAP_PROP_FPS)
        if math.isnan(source_fps) or source_fps <= 0:
            source_fps = 25.0
        frame_interval = max(int(round(source_fps / self.config.fps)), 1)

        frame_index = -1
        saved_faces = 0
        saved_raw = 0
        start_time = time.time()

        while saved_faces < self.config.max_frames:
            ret, frame = capture.read()
            frame_index += 1
            if not ret:
                break

            if frame_index % frame_interval != 0:
                continue

            if raw_dir is not None:
                raw_name = raw_dir / f"frame_{saved_raw:04d}.jpg"
                cv2.imwrite(str(raw_name), frame)
                saved_raw += 1

            face_crop = self._extract_face(frame)
            if face_crop is None:
                continue

            face_name = faces_dir / f"frame_{saved_faces:04d}.jpg"
            cv2.imwrite(str(face_name), face_crop)
            saved_faces += 1

        capture.release()
        status = "ok" if saved_faces > 0 else "no_face"
        return {
            "status": status,
            "faces": saved_faces,
            "raw": saved_raw,
            "duration_sec": round(time.time() - start_time, 2),
        }


def load_metadata(metadata_path: Path, split: str, include_extra: bool = False) -> List[Dict[str, str]]:
    with metadata_path.open("r", encoding="utf-8") as f:
        entries = json.load(f)
    result: List[Dict[str, str]] = []
    for entry in entries:
        if entry["split"] == split:
            result.append(entry)
        elif include_extra and entry["split"] == "extra":
            result.append(entry)
    return result


def label_name(label: int) -> str:
    return "real" if label == 0 else "fake"


def prepare_output_dirs(base: Path) -> None:
    (base / "faces_224").mkdir(parents=True, exist_ok=True)
    (base / "raw_frames").mkdir(parents=True, exist_ok=True)


def process_ffpp_split(
    project_root: Path,
    split: str,
    limit: Optional[int] = None,
    include_extra: bool = False,
) -> None:
    metadata_path = project_root / "metadata" / "ffpp_c23_split.json"
    entries = load_metadata(metadata_path, split, include_extra=include_extra)
    if limit:
        entries = entries[:limit]

    config = ExtractionConfig(output_root=project_root / "data" / "processed" / "ffpp_c23")
    prepare_output_dirs(config.output_root)
    extractor = RetinaFaceExtractor(config)

    summary: List[Dict[str, object]] = []

    for idx, entry in enumerate(entries, 1):
        video_rel = Path(entry["path"])
        video_path = project_root / 'data' / video_rel
        label = label_name(int(entry["label"]))
        method = entry["method"]
        split_name = entry["split"]
        video_id = entry["video_id"]

        faces_dir = config.output_root / "faces_224" / split_name / label / method / video_id
        raw_dir = config.output_root / "raw_frames" / split_name / label / method / video_id if config.save_raw else None

        result = extractor.process_video(video_path, faces_dir, raw_dir)
        result.update(
            {
                "video_id": video_id,
                "method": method,
                "label": label,
                "split": split_name,
                "video_path": str(video_rel),
                "faces_dir": str(faces_dir),
            }
        )
        summary.append(result)

        if idx % 20 == 0:
            print(f"Processed {idx}/{len(entries)} videos - last status: {result['status']} (faces={result['faces']})")

    output_json = config.output_root / f"summary_{split}.json"
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Summary written to {output_json}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract frames and faces for FF++ c23 dataset.")
    parser.add_argument("--split", choices=["train", "val", "test", "extra"], default="val")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on number of videos to process")
    parser.add_argument("--include-extra", action="store_true", help="Include extra methods (FaceShifter, DeepFakeDetection)")

    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    process_ffpp_split(project_root, args.split, args.limit, args.include_extra)
