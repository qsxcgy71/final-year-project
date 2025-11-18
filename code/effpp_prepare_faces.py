"""Generate unified face crops for EFF++ using detector-based pipeline."""
from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from PIL import Image

ORIGINAL_METHOD = "original"
DEFAULT_DETECTOR = "retinaface"
CUDA_LIBRARY_MODULE_SUBDIRS = [
    ("nvidia.cublas", "bin"),
    ("nvidia.cuda_runtime", "bin"),
    ("nvidia.cuda_runtime", "lib"),
    ("nvidia.cudnn", "bin"),
    ("nvidia.cufft", "bin"),
    ("nvidia.curand", "bin"),
    ("nvidia.cusolver", "bin"),
    ("nvidia.cusparse", "bin"),
    ("nvidia.nvtx", "bin"),
    ("nvidia.nvjitlink", "bin"),
]


def add_cuda_library_paths() -> List[str]:
    """Ensure CUDA dependent DLLs (cublas/cudnn) are discoverable for onnxruntime."""
    from importlib.util import find_spec

    added: List[str] = []
    for module_name, subdir in CUDA_LIBRARY_MODULE_SUBDIRS:
        spec = find_spec(module_name)
        if spec is None:
            continue
        search_paths = []
        if spec.origin:
            search_paths.append(Path(spec.origin).resolve().parent)
        if getattr(spec, 'submodule_search_locations', None):
            search_paths.extend(Path(p).resolve() for p in spec.submodule_search_locations)
        for base_path in search_paths:
            candidate = base_path / subdir
            if candidate.is_dir():
                try:
                    os.add_dll_directory(str(candidate))
                    added.append(str(candidate))
                except OSError:
                    pass
    return added


class RetinaFaceDetector:
    """Thin wrapper around insightface RetinaFace detector."""

    def __init__(
        self,
        force_cpu: bool = True,
        allow_cpu_fallback: bool = False,
        det_size: Tuple[int, int] = (640, 640),
    ) -> None:
        try:
            from insightface.app import FaceAnalysis  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "insightface is required for RetinaFace detection. Install with `pip install insightface`."
            ) from exc

        added_paths: List[str] = []
        if not force_cpu:
            added_paths = add_cuda_library_paths()
            if added_paths:
                print(f"[retinaface] injected CUDA dll directories: {added_paths}", flush=True)

        providers = ["CPUExecutionProvider"] if force_cpu else ["CUDAExecutionProvider", "CPUExecutionProvider"]

        def initialise(providers_list: List[str]) -> FaceAnalysis:
            return FaceAnalysis(name="buffalo_l", providers=providers_list)

        try:
            self.app = initialise(providers)
        except Exception as exc:
            if force_cpu or allow_cpu_fallback:
                if not force_cpu:
                    print(
                        "[retinaface] warning: CUDA provider initialisation failed; falling back to CPU.",
                        flush=True,
                    )
                self.app = initialise(["CPUExecutionProvider"])
                force_cpu = True
            else:
                raise RuntimeError(
                    "Failed to initialise RetinaFace with CUDAExecutionProvider. "
                    "Verify CUDA runtime libraries (cublas/cudnn) are installed."
                ) from exc

        active_providers = getattr(self.app, "providers", providers or [])
        print(f"[retinaface] initialised with providers: {active_providers}", flush=True)
        using_gpu = not force_cpu and "CUDAExecutionProvider" in active_providers
        if not using_gpu:
            if force_cpu:
                print("[retinaface] running on CPU by request.", flush=True)
            elif allow_cpu_fallback:
                print("[retinaface] warning: CUDAExecutionProvider unavailable; using CPU fallback.", flush=True)
            else:
                raise RuntimeError(
                    "CUDAExecutionProvider unavailable. Aborting instead of falling back to CPU. "
                    "Check that cublasLt64_12.dll and cudnn*.dll are reachable."
                )
        ctx_id = -1 if not using_gpu else 0
        self.app.prepare(ctx_id=ctx_id, det_size=det_size)
        self.using_gpu = using_gpu

    def detect(self, image_bgr: np.ndarray) -> Tuple[List[float], float] | None:
        faces = self.app.get(image_bgr)
        if not faces:
            return None
        best = max(faces, key=lambda item: getattr(item, "det_score", 0.0))
        bbox = [float(v) for v in best.bbox]
        score = float(getattr(best, "det_score", 0.0))
        return bbox, score


DETECTORS = {
    "retinaface": RetinaFaceDetector,
}


@dataclass
class CropResult:
    saved: int = 0
    missing_face: int = 0
    skipped_existing: int = 0

    def to_json(self) -> Dict[str, int]:
        return {
            "saved": self.saved,
            "missing_face": self.missing_face,
            "skipped_existing": self.skipped_existing,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare detector-based EFF++ crops.")
    parser.add_argument("--pairs-root", type=Path, default=Path("data/effpp_cache/pairs"), help="Pair manifest root.")
    parser.add_argument("--out-root", type=Path, default=Path("data/effpp_cache/crops"), help="Output crop root.")
    parser.add_argument("--detector", choices=list(DETECTORS.keys()), default=DEFAULT_DETECTOR, help="Detector backend.")
    parser.add_argument("--expand", type=float, default=0.25, help="Bounding-box expansion ratio on each side.")
    parser.add_argument("--seed", type=int, default=42, help="Shuffle seed for identity order.")
    parser.add_argument("--identities", nargs="*", help="Optional list of identities to process.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Limit number of identities.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing crops if present.")
    parser.add_argument("--splits", nargs="*", default=None, help="Optional split filter (train/val/test).")
    parser.add_argument("--force-cpu", action="store_true", help="Force CPU inference for detector (default).")
    parser.add_argument(
        "--allow-cpu-fallback",
        action="store_true",
        help="If CUDA initialisation fails, continue on CPU instead of aborting.",
    )
    return parser.parse_args()


def load_detector(name: str, force_cpu: bool, allow_cpu_fallback: bool) -> RetinaFaceDetector:
    detector_cls = DETECTORS[name]
    detector = detector_cls(force_cpu=force_cpu, allow_cpu_fallback=allow_cpu_fallback)
    return detector


def expand_bbox(
    bbox: List[float],
    expand_ratio: float,
    width: int,
    height: int,
) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1
    cx = x1 + w / 2.0
    cy = y1 + h / 2.0
    new_w = w * (1.0 + 2.0 * expand_ratio)
    new_h = h * (1.0 + 2.0 * expand_ratio)
    new_x1 = max(0, int(round(cx - new_w / 2.0)))
    new_y1 = max(0, int(round(cy - new_h / 2.0)))
    new_x2 = min(width, int(round(cx + new_w / 2.0)))
    new_y2 = min(height, int(round(cy + new_h / 2.0)))
    return new_x1, new_y1, new_x2, new_y2


def collect_pair_files(pairs_root: Path, split_filter: Optional[List[str]]) -> Dict[str, List[Tuple[str, str, Path]]]:
    identity_map: Dict[str, List[Tuple[str, str, Path]]] = defaultdict(list)
    for pair_file in sorted(pairs_root.glob("*/*/*.pairs.json")):
        method_dir = pair_file.parent
        split_dir = method_dir.parent
        split = split_dir.name
        method = method_dir.name
        identity = pair_file.stem
        if split_filter and split not in split_filter:
            continue
        identity_map[identity].append((split, method, pair_file))
    return identity_map


def load_pair_manifest(pair_file: Path) -> Dict[str, object]:
    with pair_file.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def detect_face(
    detector: RetinaFaceDetector,
    cache: Dict[Path, Tuple[List[float], float] | None],
    image_path: Path,
) -> Tuple[List[float], float] | None:
    if image_path in cache:
        return cache[image_path]
    if not image_path.exists():
        cache[image_path] = None
        return None
    image = Image.open(image_path).convert("RGB")
    image_bgr = np.array(image)[:, :, ::-1]
    result = detector.detect(image_bgr)
    cache[image_path] = result
    return result


def crop_and_save(
    detector: RetinaFaceDetector,
    cache: Dict[Path, Tuple[List[float], float] | None],
    project_root: Path,
    image_path: Path,
    out_dir: Path,
    rank: int,
    expand_ratio: float,
    meta_payload: Dict[str, object],
    overwrite: bool,
) -> Dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    image_out = out_dir / f"frame_{rank:04d}.jpg"
    meta_out = out_dir / f"frame_{rank:04d}.json"
    if image_out.exists() and meta_out.exists() and not overwrite:
        return {"status": "skipped_existing"}

    detection = detect_face(detector, cache, image_path)
    if detection is None:
        return {"status": "missing_face"}
    bbox, score = detection

    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    x1, y1, x2, y2 = expand_bbox(bbox, expand_ratio, width, height)
    if x1 >= x2 or y1 >= y2:
        return {"status": "invalid_bbox"}
    crop = image.crop((x1, y1, x2, y2))
    crop.save(image_out, quality=95)

    meta = {
        **meta_payload,
        "source_image": image_path.relative_to(project_root).as_posix(),
        "bbox": [float(v) for v in bbox],
        "expanded_bbox": [x1, y1, x2, y2],
        "detector_score": detection[1],
    }
    meta_out.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "saved"}


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    detector = load_detector(args.detector, force_cpu=args.force_cpu, allow_cpu_fallback=args.allow_cpu_fallback)

    identity_map = collect_pair_files(args.pairs_root, args.splits)
    identities = sorted(identity_map.keys())
    if args.identities:
        identities = [identity for identity in identities if identity in set(args.identities)]
    rng = random.Random(args.seed)
    rng.shuffle(identities)
    if args.identity_limit is not None:
        identities = identities[: args.identity_limit]

    detection_cache: Dict[Path, Tuple[List[float], float] | None] = {}
    summary: Dict[str, Dict[str, Dict[str, object]]] = defaultdict(lambda: defaultdict(dict))
    real_summary: Dict[str, CropResult] = defaultdict(CropResult)
    processed_real_keys: set[Tuple[str, str, int]] = set()

    total_pairs = 0
    for identity in identities:
        for split, method, pair_file in identity_map[identity]:
            data = load_pair_manifest(pair_file)
            pairs_list: List[Dict[str, object]] = list(data.get("pairs", []))
            real_split = str(data.get("real_split", split))
            method_result = CropResult()
            for pair in pairs_list:
                rank = int(pair["pair_index"])
                real_path = project_root / pair["real_frame"]
                target_path = project_root / pair["target_frame"]

                real_out_dir = args.out_root / real_split / identity / ORIGINAL_METHOD
                real_meta = {
                    "identity": identity,
                    "method": ORIGINAL_METHOD,
                    "split": real_split,
                    "pair_index": rank,
                    "detector": args.detector,
                    "expand_ratio": args.expand,
                }
                real_key = (real_split, identity, rank)
                if real_key not in processed_real_keys or args.overwrite:
                    status = crop_and_save(
                        detector,
                        detection_cache,
                        project_root,
                        real_path,
                        real_out_dir,
                        rank,
                        args.expand,
                        real_meta,
                        overwrite=args.overwrite,
                    )
                    if status["status"] == "saved":
                        real_summary[identity].saved += 1
                        processed_real_keys.add(real_key)
                    elif status["status"] == "missing_face":
                        real_summary[identity].missing_face += 1
                    elif status["status"] == "skipped_existing":
                        real_summary[identity].skipped_existing += 1

                target_out_dir = args.out_root / split / identity / method
                target_meta = {
                    "identity": identity,
                    "method": method,
                    "split": split,
                    "pair_index": rank,
                    "detector": args.detector,
                    "expand_ratio": args.expand,
                }
                status = crop_and_save(
                    detector,
                    detection_cache,
                    project_root,
                    target_path,
                    target_out_dir,
                    rank,
                    args.expand,
                    target_meta,
                    overwrite=args.overwrite,
                )
                if status["status"] == "saved":
                    method_result.saved += 1
                elif status["status"] == "missing_face":
                    method_result.missing_face += 1
                elif status["status"] == "skipped_existing":
                    method_result.skipped_existing += 1
                total_pairs += 1

            summary[identity][method] = {
                "split": split,
                "pairs": len(pairs_list),
                "result": method_result.to_json(),
            }
        # logging per identity to support resume if interrupted
        identity_summary = summary.get(identity, {})
        total_pairs_identity = sum(item.get("pairs", 0) for item in identity_summary.values())
        total_saved_identity = sum(item["result"].get("saved", 0) for item in identity_summary.values())
        total_missing_identity = sum(item["result"].get("missing_face", 0) for item in identity_summary.values())
        total_skipped_identity = sum(item["result"].get("skipped_existing", 0) for item in identity_summary.values())
        print(
            f"[progress] identity={identity} methods={len(identity_summary)} pairs={total_pairs_identity} "
            f"saved={total_saved_identity} missing={total_missing_identity} skipped={total_skipped_identity}",
            flush=True,
        )

    args.out_root.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_root / "summary.json"
    details_serializable = {identity: dict(method_map) for identity, method_map in summary.items()}
    summary_payload = {
        "detector": args.detector,
        "expand_ratio": args.expand,
        "identities": len(identities),
        "pairs_processed": total_pairs,
        "details": details_serializable,
        "real_summary": {identity: result.to_json() for identity, result in real_summary.items()},
    }
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "identities": len(identities),
                "pairs_processed": total_pairs,
                "detector": args.detector,
                "expand": args.expand,
                "out_root": args.out_root.as_posix(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()


