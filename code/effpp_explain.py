"""Generate EFF++ frame annotations with optional language model support."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image

from effpp_schema import load_tags, validate_annotation

try:  # pragma: no cover
    import torch  # type: ignore
except (ImportError, OSError):  # pragma: no cover
    torch = None  # type: ignore

ORIGINAL_METHOD = "original"
TECHNIQUE_ORDER = [ORIGINAL_METHOD, "Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]


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
    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        provider: str = "openai",
        timeout: int = 180,
        max_retries: int = 5,
        retry_delay: float = 5.0,
        request_interval: float = 0.0,
        force_proxy: bool = False,
    ) -> None:
        self.provider = provider
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_interval = request_interval
        self.last_request_ts = 0.0
        self.base_url: str
        if provider == "gemini":
            primary_base = (base_url or f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent").rstrip("/")
            gemini_keys: List[str] = []
            if api_key:
                gemini_keys.append(api_key.strip())
            index = 1
            while True:
                env_name = "GEMINI_API_KEY" if index == 1 else f"GEMINI_API_KEY_{index}"
                key_val = os.environ.get(env_name)
                if not key_val:
                    break
                key_val = key_val.strip()
                if key_val and key_val not in gemini_keys:
                    gemini_keys.append(key_val)
                index += 1
            self._gemini_slots: List[Dict[str, object]] = []
            # Official Google Gemini keys throttle according to CLI override; default 4s.
            official_interval = self.request_interval if self.request_interval >= 0 else 0.0
            for key_val in gemini_keys:
                self._gemini_slots.append(
                    {
                        "key": key_val,
                        "base": primary_base,
                        "url": primary_base,
                        "headers": {
                            "Content-Type": "application/json",
                            "x-goog-api-key": key_val,
                        },
                        "interval": official_interval,
                    }
                )
            self._gemini_official_count = len(self._gemini_slots)
            proxy_index: Optional[int] = None
            proxy_base = os.environ.get("LLM_API_BASE_GEMINI")
            proxy_key = os.environ.get("LLM_API_KEY")
            if proxy_base and proxy_key:
                proxy_base = proxy_base.rstrip("/")
                proxy_key = proxy_key.strip()
                proxy_index = len(self._gemini_slots)
                self._gemini_slots.append(
                    {
                        "key": proxy_key,
                        "base": proxy_base,
                        "url": f"{proxy_base}/v1beta/models/{model}:generateContent",
                        "headers": {
                            "Authorization": f"Bearer {proxy_key}",
                            "Content-Type": "application/json",
                        },
                        "interval": 0.0,  # third-party proxy: no enforced interval
                    }
                )
            if not self._gemini_slots:
                raise RuntimeError("GEMINI_API_KEY is required for gemini mode")
            self.api_keys = [slot["key"] for slot in self._gemini_slots]  # type: ignore[list-item]
            self.api_key_index = 0
            self.slot_request_interval = self.request_interval
            self._gemini_proxy_index = proxy_index
            self._gemini_limit_counter = 0
            self._gemini_force_proxy = False
            self._set_gemini_key(self.api_key_index)
            if force_proxy:
                if not self._switch_to_proxy():
                    raise RuntimeError("Proxy Gemini key required for --chatgpt-force-proxy but none configured.")
        else:
            base = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
            if base.endswith("/v1"):
                self.url = base.rstrip("/") + "/chat/completions"
                self.base_url = base.rstrip("/")
            else:
                self.url = base.rstrip("/") + "/v1/chat/completions"
                self.base_url = base.rstrip("/")
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")
            if not self.api_key:
                raise RuntimeError("OPENAI_API_KEY is required for chatgpt mode")
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            self.api_keys = [self.api_key]
            self.api_key_index = 0
            self.slot_request_interval = self.request_interval

    def _set_gemini_key(self, index: int) -> None:
        slot = self._gemini_slots[index]
        self.api_key_index = index
        self.api_key = slot["key"]  # type: ignore[assignment]
        self.base_url = slot["base"]  # type: ignore[assignment]
        self.url = slot["url"]  # type: ignore[assignment]
        self.headers = slot["headers"]  # type: ignore[assignment]
        interval = slot.get("interval", self.request_interval)
        self.slot_request_interval = float(interval) if interval is not None else self.request_interval

    def _advance_gemini_key(self) -> bool:
        if self.provider != "gemini":
            return False
        total = len(self._gemini_slots)
        if total == 0:
            return False
        candidate = (self.api_key_index + 1) % total
        self._set_gemini_key(candidate)
        return True

    def _switch_to_proxy(self) -> bool:
        proxy_index = getattr(self, "_gemini_proxy_index", None)
        if proxy_index is None:
            return False
        self._set_gemini_key(proxy_index)
        self._gemini_force_proxy = True
        self._gemini_limit_counter = 0
        return True

    def _handle_gemini_limit(self) -> bool:
        if self.provider != "gemini":
            return False
        if getattr(self, "_gemini_force_proxy", False):
            return False
        is_official = self.api_key_index < getattr(self, "_gemini_official_count", 0)
        if is_official:
            self._gemini_limit_counter += 1
            threshold = max(1, getattr(self, "_gemini_official_count", 0)) + 1
            if self._gemini_limit_counter >= threshold:
                if self._switch_to_proxy():
                    return True
                return False
            self._advance_gemini_key()
            return True
        self._gemini_limit_counter = 0
        return False

    def _wait_for_window(self) -> None:
        interval = getattr(self, "slot_request_interval", self.request_interval)
        if interval <= 0:
            return
        now = time.time()
        wait = interval - (now - self.last_request_ts)
        if wait > 0:
            time.sleep(wait)

    def _mark_request(self) -> None:
        self.last_request_ts = time.time()

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
        if self.provider == "gemini":
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": prompt + "\n\n" + user,
                            }
                        ],
                    }
                ]
            }
            last_error: Optional[str] = None
            attempt = 0
            while attempt < self.max_retries:
                self._wait_for_window()
                try:
                    response = requests.post(self.url, json=payload, headers=self.headers, timeout=self.timeout)
                except requests.RequestException as exc:  # pragma: no cover
                    last_error = f"Google Gemini request exception: {exc}"
                    response = None
                    self._mark_request()
                else:
                    self._mark_request()
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise RuntimeError("Google Gemini API returned no candidates")
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if not parts:
                            raise RuntimeError("Google Gemini API returned empty content")
                        if self.api_key_index < getattr(self, "_gemini_official_count", 0):
                            self._gemini_limit_counter = 0
                        return parts[0].get("text", "").strip()
                    if response.status_code in {403, 429, 503}:
                        message = response.text.lower()
                        limit_hit = (
                            response.status_code in {429, 503}
                            or (response.status_code == 403 and ("limit" in message or "exceed" in message))
                            or "overload" in message
                            or "rate" in message
                        )
                        if limit_hit and self._handle_gemini_limit():
                            last_error = "Google Gemini API limit hit; switched key."
                            continue
                    if response.status_code not in {429, 500, 502, 503}:
                        raise RuntimeError(f"Google Gemini API error {response.status_code}: {response.text}")
                    last_error = f"Google Gemini API error {response.status_code}: {response.text}"
                attempt += 1
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
            raise RuntimeError(last_error or "Google Gemini API failed after retries")
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user},
            ],
            "max_tokens": 160,
            "temperature": 0.2,
        }
        last_error: Optional[str] = None
        for attempt in range(self.max_retries):
            self._wait_for_window()
            try:
                response = requests.post(self.url, json=payload, headers=self.headers, timeout=self.timeout)
            except requests.RequestException as exc:  # pragma: no cover
                last_error = f"ChatGPT request exception: {exc}"
                response = None
                self._mark_request()
            else:
                self._mark_request()
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if not choices:
                        raise RuntimeError("ChatGPT API returned no choices")
                    return choices[0]["message"]["content"].strip()
                if response.status_code not in {429, 500, 502, 503}:
                    raise RuntimeError(f"ChatGPT API error {response.status_code}: {response.text}")
                last_error = f"ChatGPT API error {response.status_code}: {response.text}"
            if attempt + 1 < self.max_retries:
                time.sleep(self.retry_delay * (attempt + 1))
            raise RuntimeError(last_error or "ChatGPT API failed after retries")


def build_chatgpt_session(args: argparse.Namespace) -> Optional[ChatGPTSession]:
    if args.mode != "chatgpt":
        return None
    return ChatGPTSession(
        model=args.chatgpt_model,
        base_url=args.chatgpt_base_url,
        api_key=args.chatgpt_api_key,
        provider=args.chatgpt_provider,
        timeout=args.chatgpt_timeout,
        max_retries=args.chatgpt_max_retries,
        retry_delay=args.chatgpt_retry_delay,
        request_interval=args.chatgpt_request_interval,
        force_proxy=args.chatgpt_force_proxy,
    )


def process_identity_record(
    identity: str,
    index_path: Path,
    args: argparse.Namespace,
    technique_summary: Dict[str, str],
    tag_ids: Dict[str, str],
    run_meta_base: Dict[str, object],
    project_root: Path,
    crops_dir: Path,
    output_root: Path,
    llava_session: Optional[LlavaSession],
    chatgpt_session: Optional[ChatGPTSession],
) -> None:
    record = load_json(index_path)
    frame_indices = record.get("frame_indices", [])
    videos = record.get("videos", {})
    if ORIGINAL_METHOD not in videos:
        if args.verbose:
            print(f"[warn] Identity {identity} missing original video info, skipping.")
        return
    real_split = videos[ORIGINAL_METHOD]["split"]
    for rank, frame_index in enumerate(frame_indices):
        if args.max_frames is not None and rank >= args.max_frames:
            break
        try:
            real_image_path, _, real_meta = prepare_pair(crops_dir, real_split, identity, ORIGINAL_METHOD, rank)
        except FileNotFoundError:
            if args.verbose:
                print(f"Missing original crop for identity {identity} rank {rank}, skipping pairs.")
            continue
        for method in TECHNIQUE_ORDER:
            video_meta = videos.get(method)
            if video_meta is None:
                continue
            method_split = video_meta["split"]
            target_dir = output_root / method_split / method / identity
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                target_image_path, _, target_meta = prepare_pair(crops_dir, method_split, identity, method, rank)
            except FileNotFoundError:
                if args.verbose:
                    print(f"Missing crop for {method} identity {identity} rank {rank}, skipping")
                continue
            manipulated = method != ORIGINAL_METHOD
            summary_key = method if method in technique_summary else method.replace("real", ORIGINAL_METHOD)
            technique_text = "" if method == ORIGINAL_METHOD else technique_summary.get(summary_key, "")
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
            else:
                assert chatgpt_session is not None
                context = {
                    "identity": identity,
                    "frame_rank": rank,
                    "method": method,
                    "split": method_split,
                }
                description = chatgpt_session.describe(
                    manipulated=manipulated,
                    technique_summary=technique_text,
                    tags=tags,
                    context=context,
                )
            answer = build_answer(description, manipulated)
            pair_info = {
                "identity": identity,
                "frame_rank": rank,
                "frame_index": int(target_meta.get("frame_index", frame_index)),
                "method": method,
                "split": method_split,
                "video_id": video_meta.get("video_id", ""),
                "real_frame_path": real_image_path.relative_to(project_root).as_posix(),
                "target_frame_path": target_image_path.relative_to(project_root).as_posix(),
            }
            source_label = "api" if args.mode == "chatgpt" else ("local" if args.mode == "llava" else "placeholder")
            run_meta = dict(run_meta_base)
            if args.mode == "chatgpt" and chatgpt_session is not None:
                run_meta.update(
                    {
                        "llm_provider": args.chatgpt_provider,
                        "llm_model_id": args.chatgpt_model,
                        "llm_base_url": chatgpt_session.base_url,
                        "llm_max_retries": chatgpt_session.max_retries,
                        "llm_retry_delay": chatgpt_session.retry_delay,
                        "llm_request_interval": getattr(
                            chatgpt_session, "slot_request_interval", chatgpt_session.request_interval
                        ),
                        "llm_active_key_index": chatgpt_session.api_key_index,
                        "llm_key_pool_size": len(chatgpt_session.api_keys),
                    }
                )
            run_meta["pair_rank"] = rank
            ann = {
                "q": "Is this image manipulated?",
                "manipulated": manipulated,
                "a": answer,
                "cfad_rationale": answer,
                "evidence_tags": tags,
                "evidence_regions": [],
                "technique_summary": technique_text,
                "source": source_label,
                "pair": pair_info,
                "run_meta": run_meta,
            }
            errors = validate_annotation(ann, tag_ids)
            if errors and args.verbose:
                print(f"Validation warnings for {identity} frame {rank} {method}: {errors}")
            ann_path = target_dir / f"frame_{rank:04d}.ann.json"
            ann_path.write_text(json.dumps(ann, ensure_ascii=False, indent=2), encoding="utf-8")
            if args.verbose:
                print(f"Saved {(ann_path).relative_to(project_root).as_posix()}")
EVIDENCE_TAG_PRESETS: Dict[str, List[str]] = {
    ORIGINAL_METHOD: ["natural_consistency", "lighting_shadow"],
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


def collect_identity_records(
    frame_index_dir: Path,
    identities_filter: Optional[List[str]],
    identity_limit: Optional[int],
) -> List[Tuple[str, Path]]:
    target = set(identities_filter) if identities_filter else None
    records: List[Tuple[str, Path]] = []
    for split_dir in sorted(frame_index_dir.iterdir()):
        if not split_dir.is_dir():
            continue
        for record_path in sorted(split_dir.glob("*.json")):
            if record_path.name in {"manifest.json"}:
                continue
            identity = record_path.stem
            if target and identity not in target:
                continue
            records.append((identity, record_path))
    records.sort(key=lambda item: item[0])
    if identity_limit is not None:
        records = records[: identity_limit]
    return records


def get_torch_meta() -> Tuple[Optional[str], Optional[str]]:
    if torch is None:  # type: ignore[truthy-function]
        return None, None
    version = getattr(torch, "__version__", None)  # type: ignore[attr-defined]
    cuda_version = getattr(getattr(torch, "version", None), "cuda", None)  # type: ignore[attr-defined]
    return version, cuda_version


def generate_annotations(args: argparse.Namespace) -> None:
    project_root = Path(__file__).resolve().parents[1]
    frame_index_dir = project_root / args.frame_indices_dir
    crops_dir = project_root / args.crops_dir
    output_root = project_root / args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    technique_summary = load_json(project_root / args.technique_summary)
    if ORIGINAL_METHOD in technique_summary:
        technique_summary[ORIGINAL_METHOD] = ""
    if "real" in technique_summary and ORIGINAL_METHOD not in technique_summary:
        technique_summary[ORIGINAL_METHOD] = ""
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
    chatgpt_session_builder = None
    if args.mode == "chatgpt":
        def _builder() -> Optional[ChatGPTSession]:
            return build_chatgpt_session(args)

        chatgpt_session_builder = _builder
        if args.workers <= 1:
            chatgpt_session = chatgpt_session_builder()

    identity_records = collect_identity_records(frame_index_dir, args.identities, args.identity_limit)
    torch_version, cuda_version = get_torch_meta()
    llava_model_id = None
    llava_quant = None
    llava_max_new_tokens = None
    if args.mode == "llava":
        llava_model_id = args.llava_model_id or Path(args.model_dir).name
        llava_quant = args.quant
        llava_max_new_tokens = args.max_new_tokens

    mode_label = args.mode
    if args.mode == "chatgpt" and args.chatgpt_provider == "gemini":
        mode_label = "gemini"
    run_meta_base = {
        "k": args.alignment_k,
        "seed": args.alignment_seed,
        "llava_model_id": llava_model_id,
        "retinaface_ckpt": args.retinaface_ckpt,
        "llava_quant": llava_quant,
        "max_new_tokens": llava_max_new_tokens,
        "mode": mode_label,
        "torch": torch_version,
        "cuda": cuda_version,
    }

    if args.workers > 1 and args.mode != "chatgpt":
        if args.verbose:
            print("[warn] Parallel workers only supported in chatgpt mode; falling back to single worker.")
        args.workers = 1

    if args.workers <= 1:
        for identity, index_path in identity_records:
            process_identity_record(
                identity,
                index_path,
                args,
                technique_summary,
                tag_ids,
                run_meta_base,
                project_root,
                crops_dir,
                output_root,
                llava_session,
                chatgpt_session,
            )
    else:
        if chatgpt_session_builder is None:
            raise RuntimeError("Parallel execution requires chatgpt mode.")
        chunk_size = (len(identity_records) + args.workers - 1) // args.workers
        chunks = [identity_records[i : i + chunk_size] for i in range(0, len(identity_records), chunk_size)]

        def worker(records: List[Tuple[str, Path]]) -> None:
            local_session = chatgpt_session_builder()
            for identity, index_path in records:
                process_identity_record(
                    identity,
                    index_path,
                    args,
                    technique_summary,
                    tag_ids,
                    run_meta_base,
                    project_root,
                    crops_dir,
                    output_root,
                    llava_session,
                    local_session,
                )

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(worker, records) for records in chunks]
            for future in futures:
                future.result()

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
    parser.add_argument(
        "--chatgpt-provider",
        choices=["openai", "gemini"],
        default="openai",
        help="LLM provider used in chatgpt mode (OpenAI or Google Gemini).",
    )
    parser.add_argument("--chatgpt-timeout", type=int, default=180, help="Request timeout (seconds) for chatgpt/gemini mode.")
    parser.add_argument("--chatgpt-max-retries", type=int, default=5, help="Maximum retry attempts for chatgpt/gemini requests.")
    parser.add_argument("--chatgpt-retry-delay", type=float, default=5.0, help="Base delay (seconds) between retry attempts.")
    parser.add_argument(
        "--chatgpt-request-interval",
        type=float,
        default=4.0,
        help="Minimum interval (seconds) between consecutive chatgpt/gemini requests (default 4s).",
    )
    parser.add_argument(
        "--chatgpt-force-proxy",
        action="store_true",
        help="Force Gemini runs to use the proxy key only (zero interval, skips official keys).",
    )
    parser.add_argument("--identities", nargs="*", help="Optional list of identities to process.")
    parser.add_argument("--identity-limit", type=int, default=None, help="Optional limit on number of identities.")
    parser.add_argument("--max-frames", type=int, default=None, help="Limit frames per identity.")
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of parallel workers for chatgpt/gemini mode (official + proxy).",
    )
    parser.add_argument("--verbose", action="store_true", help="Print output paths while writing annotations.")
    parser.add_argument("--alignment-k", type=int, default=128, help="Frame alignment k recorded in run_meta.")
    parser.add_argument("--alignment-seed", type=int, default=42, help="Alignment seed recorded in run_meta.")
    parser.add_argument("--llava-model-id", default=None, help="Identifier recorded for the LLaVA model.")
    parser.add_argument(
        "--retinaface-ckpt",
        default="insightface/buffalo_l",
        help="Detector checkpoint identifier recorded in run_meta.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    generate_annotations(args)


if __name__ == "__main__":
    main()


