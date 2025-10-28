"""Reuse pre-extracted FF++ face crops for EFF++ pipeline."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict, List

TECHNIQUE_ORDER = ["real", "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]


def load_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_source_dir(project_root: Path, record: Dict[str, object], method: str) -> Path:
    video = record["videos"][method]
    split = video["split"]
    video_id = video["video_id"]
    if method == "real":
        return project_root / "data" / "processed" / "ffpp_c23" / "faces_224" / split / "real" / "real" / video_id
    return project_root / "data" / "processed" / "ffpp_c23" / "faces_224" / split / "fake" / method / video_id


def prepare_identity(
    project_root: Path,
    identity: str,
    record: Dict[str, object],
    output_root: Path,
    max_frames: int | None,
) -> Dict[str, object]:
    frame_indices: List[int] = record.get("frame_indices", [])
    out_summary: Dict[str, object] = {}
    for method in TECHNIQUE_ORDER:
        video = record["videos"][method]
        split = video["split"]
        src_dir = collect_source_dir(project_root, record, method)
        if not src_dir.exists():
            out_summary[method] = {"status": "missing_source", "source_dir": str(src_dir)}
            continue
        frames = sorted(src_dir.glob("frame_*.jpg"))
        if not frames:
            out_summary[method] = {"status": "no_frames", "source_dir": str(src_dir)}
            continue
        target_dir = output_root / split / identity / method
        target_dir.mkdir(parents=True, exist_ok=True)
        copied = 0
        for rank, frame_index in enumerate(frame_indices):
            if max_frames is not None and rank >= max_frames:
                break
            if rank >= len(frames):
                break
            source_path = frames[rank]
            target_path = target_dir / f"frame_{rank:04d}.jpg"
            shutil.copy2(source_path, target_path)
            metadata = {
                "identity": identity,
                "method": method,
                "split": split,
                "frame_rank": rank,
                "frame_index": frame_index,
                "source_frame_rank": rank,
                "video_id": video["video_id"],
                "video_path": video["path"],
                "source_image": str(source_path.relative_to(project_root)),
                "note": "copied_from_precomputed_faces",
            }
            meta_path = target_dir / f"frame_{rank:04d}.json"
            meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
            copied += 1
        out_summary[method] = {
            "status": "ok" if copied else "empty",
            "copied": copied,
            "source_dir": str(src_dir),
        }
    return out_summary


def run(args: argparse.Namespace) -> None:
    project_root = Path(__file__).resolve().parents[1]
    frame_index_dir = project_root / args.frame_indices_dir
    output_root = project_root / args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    identity_paths = {
        path.stem: path
        for path in frame_index_dir.glob("*.json")
        if path.name not in {"manifest.json", "summary.json"}
    }

    identities = args.identities or sorted(identity_paths.keys())
    if args.identity_limit is not None:
        identities = identities[: args.identity_limit]

    summary = {}
    for identity in identities:
        record_path = identity_paths.get(identity)
        if not record_path:
            continue
        record = load_json(record_path)
        result = prepare_identity(
            project_root=project_root,
            identity=identity,
            record=record,
            output_root=project_root / args.output_dir,
            max_frames=args.max_frames,
        )
        summary[identity] = result
        print(f"Identity {identity}: {result['real'].get('copied', 0)} frames copied for real")
    summary_path = (project_root / args.output_dir) / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Copy existing FF++ face crops into EFF++ cache structure.")
    parser.add_argument("--frame-indices-dir", default="data/effpp_cache/frame_indices", help="Directory with identity alignment JSON files.")
    parser.add_argument("--output-dir", default="data/effpp_cache/crops", help="Directory for copied crops and metadata.")
    parser.add_argument("--identities", nargs="*", help="Optional list of identities to process.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Optional limit of identities.")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit frames per identity.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
