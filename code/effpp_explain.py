"""Generate EFF++ frame annotations with optional language model support."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import requests
from PIL import Image

from effpp_schema import load_tags, validate_annotation

TECHNIQUE_ORDER = ["real", "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]


def load_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def truncate_words(text: str, limit: int) -> str:
    words = text.replace("\n", " ").split()
    if len(words) <= limit:
        return " ".join(words)
    return " ".join(words[:limit])


class LlavaSession:
    def __init__(self, model_dir: Path, quant: str, max_new_tokens: int, force_cpu: bool = False) -> None:
        from llava_quant import build as llava_build, infer as llava_infer

        self.llava_infer = llava_infer
        self.processor, self.model, self.device = llava_build(
            str(model_dir), quant=quant, max_new_tokens=max_new_tokens, force_cpu=force_cpu
        )
        self.max_new_tokens = max_new_tokens

    def describe(self, image_path: Path, prompt: str) -> str:
        image = Image.open(image_path).convert("RGB")
        return self.llava_infer(self.processor, self.model, self.device, image, prompt, self.max_new_tokens)


class ChatGPTSession:
    def __init__(self, model: str, base_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        base = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
        if base.endswith("/v1"):
            self.url = base.rstrip("/") + "/chat/completions"
        else:
            self.url = base.rstrip("/") + "/v1/chat/completions"
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for chatgpt mode")
        self.model = model

    def describe(self, manipulated: bool, technique_summary: str, tags: List[str], context: Dict[str, object]) -> str:
        identity = context.get("identity", "unknown")
        frame_rank = context.get("frame_rank", 0)
        prompt = (
            "You are writing concise visual evidence statements for face forensics."
            " Produce at most 55 English words describing observable cues."
            " Focus on the listed evidence tags."
        )
        user = (
            f"Identity {identity}, frame {frame_rank}. "
            f"Manipulated: {'yes' if manipulated else 'no'}. "
            f"Technique summary: {technique_summary}. "
            f"Evidence tags: {', '.join(tags)}. "
            "Describe what a reviewer should look for."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user},
            ],
            "max_tokens": 160,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.url, json=payload, headers=headers, timeout=180)
        if response.status_code != 200:
            raise RuntimeError(f"ChatGPT API error {response.status_code}: {response.text}")
        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("ChatGPT API returned no choices")
        return choices[0]["message"]["content"].strip()


EVIDENCE_TAG_PRESETS: Dict[str, List[str]] = {
    "real": ["natural_consistency", "lighting_shadow"],
    "Deepfakes": ["boundary_blend", "skin_texture"],
    "Face2Face": ["mouth_artifact", "lighting_shadow"],
    "FaceSwap": ["geometry_distortion", "hairline_mismatch"],
    "NeuralTextures": ["specular_inconsistency", "detail_smearing"],
}


def build_answer(raw: str, manipulated: bool) -> str:
    raw_clean = truncate_words(raw.strip(), 55)
    if not raw_clean:
        raw_clean = "explanation pending"
    prefix = "Yes" if manipulated else "No"
    if raw_clean.lower().startswith("yes") or raw_clean.lower().startswith("no"):
        return raw_clean
    return f"{prefix}, {raw_clean}"


def prepare_pair(identity_dir: Path, split: str, identity: str, method: str, frame_rank: int) -> tuple[Path, Path, Dict[str, object]]:
    method_dir = identity_dir / split / identity / method
    frame_name = f"frame_{frame_rank:04d}.jpg"
    meta_name = f"frame_{frame_rank:04d}.json"
    image_path = method_dir / frame_name
    meta_path = method_dir / meta_name
    if not image_path.exists() or not meta_path.exists():
        raise FileNotFoundError(str(image_path))
    metadata = load_json(meta_path)
    return image_path, meta_path, metadata


def generate_annotations(args: argparse.Namespace) -> None:
    project_root = Path(__file__).resolve().parents[1]
    frame_index_dir = project_root / args.frame_indices_dir
    crops_dir = project_root / args.crops_dir
    output_root = project_root / args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    technique_summary = load_json(project_root / args.technique_summary)
    tag_ids = load_tags(project_root / args.tag_list)

    llava_session: Optional[LlavaSession] = None
    if args.mode == "llava":
        llava_session = LlavaSession(
            model_dir=project_root / args.model_dir,
            quant=args.quant,
            max_new_tokens=args.max_new_tokens,
            force_cpu=args.force_cpu,
        )

    chatgpt_session: Optional[ChatGPTSession] = None
    if args.mode == "chatgpt":
        chatgpt_session = ChatGPTSession(model=args.chatgpt_model, base_url=args.chatgpt_base_url, api_key=args.chatgpt_api_key)

    identities = args.identities or [
        path.stem for path in sorted(frame_index_dir.glob("*.json")) if path.name not in {"manifest.json", "summary.json"}
    ]
    if args.identity_limit is not None:
        identities = identities[: args.identity_limit]

    for identity in identities:
        index_path = frame_index_dir / f"{identity}.json"
        if not index_path.exists():
            continue
        record = load_json(index_path)
        frame_indices = record.get("frame_indices", [])
        for rank, _ in enumerate(frame_indices):
            if args.max_frames is not None and rank >= args.max_frames:
                break
            real_split = record["videos"]["real"]["split"]
            try:
                real_image_path, _, real_meta = prepare_pair(crops_dir, real_split, identity, "real", rank)
            except FileNotFoundError:
                if args.verbose:
                    print(f"Missing real crop for identity {identity} rank {rank}, skipping")
                continue
            for method in TECHNIQUE_ORDER:
                video_meta = record["videos"][method]
                method_split = video_meta["split"]
                target_dir = output_root / method_split / method / identity
                target_dir.mkdir(parents=True, exist_ok=True)
                try:
                    target_image_path, _, target_meta = prepare_pair(crops_dir, method_split, identity, method, rank)
                except FileNotFoundError:
                    if args.verbose:
                        print(f"Missing crop for {method} identity {identity} rank {rank}, skipping")
                    continue
                manipulated = method != "real"
                tags = EVIDENCE_TAG_PRESETS.get(method, ["natural_consistency", "lighting_shadow"])
                if args.mode == "placeholder":
                    description = "explanation pending"
                elif args.mode == "llava":
                    assert llava_session is not None
                    if manipulated:
                        prompt = (
                            "Identify visible manipulation artefacts (boundary seams, lighting mismatch, texture loss,"
                            " warped geometry, color bleed). Provide at most 55 English words."
                        )
                    else:
                        prompt = (
                            "Explain why this face appears authentic. Describe consistent lighting, textures, or geometry"
                            " in at most 55 English words."
                        )
                    description = llava_session.describe(target_image_path, prompt)
                else:  # chatgpt
                    assert chatgpt_session is not None
                    context = {
                        "identity": identity,
                        "frame_rank": rank,
                        "method": method,
                        "split": method_split,
                    }
                    description = chatgpt_session.describe(
                        manipulated=manipulated,
                        technique_summary=technique_summary.get(method, ""),
                        tags=tags,
                        context=context,
                    )
                answer = build_answer(description, manipulated)
                ann = {
                    "q": "Is this image manipulated?",
                    "manipulated": manipulated,
                    "a": answer,
                    "cfad_rationale": answer,
                    "evidence_tags": tags,
                    "evidence_regions": [],
                    "technique_summary": technique_summary.get(method, ""),
                    "pair": {
                        "identity": identity,
                        "frame_rank": rank,
                        "frame_index": int(target_meta["frame_index"]),
                        "method": method,
                        "split": method_split,
                        "video_id": video_meta["video_id"],
                        "real_frame_path": str(real_image_path.relative_to(project_root)),
                        "target_frame_path": str(target_image_path.relative_to(project_root)),
                    },
                }
                errors = validate_annotation(ann, tag_ids)
                if errors and args.verbose:
                    print(f"Validation warnings for {identity} frame {rank} {method}: {errors}")
                ann_path = target_dir / f"frame_{rank:04d}.ann.json"
                ann_path.write_text(json.dumps(ann, ensure_ascii=False, indent=2), encoding="utf-8")
                if args.verbose:
                    print(f"Saved {ann_path.relative_to(project_root)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate EFF++ annotations from cropped frames.")
    parser.add_argument("--frame-indices-dir", default="data/effpp_cache/frame_indices", help="Directory with identity alignment JSON files.")
    parser.add_argument("--crops-dir", default="data/effpp_cache/crops", help="Directory with face crops and metadata.")
    parser.add_argument("--output-dir", default="data/effpp_ann", help="Directory to store annotation JSON files.")
    parser.add_argument("--technique-summary", default="config/effpp_mts.json", help="Technique description JSON.")
    parser.add_argument("--tag-list", default="config/effpp_tags.json", help="Evidence tag list JSON.")
    parser.add_argument("--model-dir", default="models/llava-1.5-7b-hf", help="Path to LLaVA model directory (llava mode only).")
    parser.add_argument("--quant", choices=["none", "4bit", "8bit"], default="4bit", help="Quantisation mode for LLaVA.")
    parser.add_argument("--max-new-tokens", type=int, default=120, help="Maximum tokens generated by LLaVA.")
    parser.add_argument("--force-cpu", action="store_true", help="Force CPU inference for LLaVA.")
    parser.add_argument("--mode", choices=["placeholder", "chatgpt", "llava"], default="chatgpt", help="Annotation generation mode.")
    parser.add_argument("--chatgpt-model", default="gpt-4.1-mini", help="Model name for ChatGPT mode.")
    parser.add_argument("--chatgpt-api-key", default=None, help="API key for ChatGPT mode (falls back to env variable).")
    parser.add_argument("--chatgpt-base-url", default=None, help="Override base URL for ChatGPT API.")
    parser.add_argument("--identities", nargs="*", help="Optional list of identities to process.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Optional limit on number of identities.")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit frames per identity.")
    parser.add_argument("--verbose", action="store_true", help="Print output paths while writing annotations.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    generate_annotations(args)


if __name__ == "__main__":
    main()


