# EFF++ Migration Checklist (FF++ Baseline)

## Project Snapshot
- Raw videos: `data/ffpp_c23/<method>/<video>.mp4` (compression c23). Metadata CSVs live in `data/ffpp_c23/csv/` with frame counts and codecs.
- Active splits: `data/splits/ffpp_c23_split.json` generated via `code/mfa_metadata.py` (stratified per method, not per identity).
- Extracted faces and raw frames: `data/processed/ffpp_c23/{faces_224,raw_frames}/<split>/<label>/<method>/<video_id>/` produced by `code/extract_ffpp_frames.py`.
- MFA pipeline: `code/run_mfa_ffpp.py` (uses `llava_quant.py` to talk to local LLaVA) with outputs under `mfa/ffpp_c23/` and `eval/ffpp_c23/`.

## 0. Pre-flight Toggles
- Frame alignment K: start with `K=128` (fallback to video length if shorter). Commit this to a small config such as `config/effpp_alignment.yaml`.
- Text generator: keep placeholder strings (`a = <PENDING>`) until external API keys are wired; when ready, either call local LLaVA (see `code/run_mfa_ffpp.py`) or the ChatGPT Mini HTTP client.

## 1. Keep Pixels and Splits Frozen
- Do not move files under `data/ffpp_c23/` or alter `ffpp_c23_split.json` until the EFF++ layer is complete.
- Heads-up: the current split builder shuffles per method, so only 307 identities keep all five videos inside the same split; the remaining 693 land across different splits (for example: real=train, Face2Face=test). Document this in Appendix A and decide whether to
  - accept cross-split pairing but log provenance in each annotation, or
  - rebuild splits with identity-level grouping in a later pull request (rerun `code/mfa_metadata.py`).

## 2. Identity-wise Frame Alignment
- Source identity lists from the CSVs:
  ```bash
  python - <<'PY'
  import csv
  from pathlib import Path
  from collections import defaultdict
  base = Path('data/ffpp_c23/csv')
  methods = ['Deepfakes','Face2Face','FaceSwap','NeuralTextures']
  identity_map = defaultdict(lambda: defaultdict(list))
  for method in methods:
      with (base / f"{method}.csv").open('r', encoding='utf-8') as f:
          reader = csv.DictReader(f)
          for row in reader:
              stem = Path(row['File Path']).stem
              identity = stem.split('_')[0]
              identity_map[identity][method].append(stem)
  print(len(identity_map))  # 1000 identities
  PY
  ```
- For each identity, assemble the set `{real, Deepfakes, Face2Face, FaceSwap, NeuralTextures}` by joining with `ffpp_c23_split.json`. Record their original splits for auditing.
- Compute `Lmin` using the CSV `Frame Count` field (fast) or a runtime probe via `cv2.VideoCapture`. Persist per-identity frame indices (zero based) to something like `data/effpp_cache/frame_indices/<identity>.json`:
  ```json
  {
    "identity": "042",
    "videos": {
      "real": {"video_id": "042", "path": "ffpp_c23/original/042.mp4", "split": "val", "length": 435},
      "Deepfakes": {"video_id": "042_615", "path": "ffpp_c23/Deepfakes/042_615.mp4", "split": "train", "length": 435}
    },
    "frame_indices": [0, 3, 7, 10]
  }
  ```
- These indices feed both face cropping (step 3) and CFAD explanation pairing (step 6).

## 3. Unified Face Cropping
- Refactor `code/extract_ffpp_frames.py` into a reusable component (for example `code/face_cropper.py`) that accepts
  - a bounding-box provider (RetinaFace via `insightface` as today),
  - a target list of frame indices,
  - a margin sampler callable.
- Training-time crop: random margin between 4% and 20% of the bounding-box size. Record the sampled margin so the same value can be reused across the paired fake frames.
- Inference-time crop: fixed 12.5% margin.
- CFAD export: reuse the training-time sampler.
- Persist raw detections (`bbox`, `landmarks`, `margin`) next to each saved crop, e.g., `faces_224/.../frame_000123.json`, to keep the pipeline reproducible.

## 4. Frame Annotation Schema
- Declare schema in `config/effpp_frame_schema.json` with fields:
  - `q`: literal "Is this image manipulated?".
  - `manipulated`: boolean (true for fake).
  - `a`: `Yes/No + rationale` (60 words or fewer, visual evidence only).
  - `cfad_rationale`: optional longer text; default to `a`.
  - `evidence_tags`: choose 2 to 4 items from a controlled list (store in `config/effpp_tags.json`).
  - `evidence_regions`: optional list of `{"tag": "jawline", "bbox": [x0, y0, x1, y1]}` in normalized coordinates.
  - `technique_summary`: one-liner from step 5.
  - `pair`: cross-reference fields (`real_frame_path`, `fake_frame_path`, `identity`, `frame_index`, `split_info`).
- Provide either a JSON Schema document or a pydantic model so ingestion scripts can validate annotations.

## 5. Manipulation Technique Summaries
- Hard-code the four descriptions in `config/effpp_mts.json`:
  - Deepfakes: learned-face swap, boundary seams, texture mismatch.
  - Face2Face: expression transfer, mouth and nasolabial remapping artefacts.
  - FaceSwap: whole-face replacement, geometric slip, jawline or hairline color mismatch.
  - NeuralTextures: neural texture rendering, specular inconsistency, detail smearing, temporal flicker.
- Link these strings inside the annotation writer so they remain consistent across frames.

## 6. CFAD Explanation Generation
- Bundle inputs per frame index: cropped real frame, cropped fake frame, and metadata (identity, method, technique summary, proposed evidence tags).
- Store prompt templates in `config/effpp_prompts/`. Enforce `Yes/No` prefix, forbid guessing identity or algorithm, remind the 60-word limit.
- Implement a generator module (for example `code/effpp_explain.py`) with three modes:
  1. Offline placeholder (`a = "<PENDING>"`, `evidence_tags = []`).
  2. Local inference via `llava_quant.build()`.
  3. Remote inference via ChatGPT Mini using `OPENAI_BASE_URL` and `OPENAI_API_KEY` (already saved in `.env`).
- Append raw prompt/response pairs to `logs/effpp_cfad/*.jsonl` for audit trails.

## 7. Annotation Storage Layout
```
data/
  FFpp/                # untouched raw videos
  processed/ffpp_c23/  # existing crops (legacy)
  effpp_ann/           # new annotations
    train/
      Deepfakes/<video_id>/frame_000123.ann.json
      Face2Face/...
      FaceSwap/...
      NeuralTextures/...
      real/<video_id>/frame_000123.ann.json
    val/
    test/
```
- Each `.ann.json` should follow the schema from step 4 and include an MD5 checksum of the source crop to detect drift.
- Use symlinks or path references back to the shared frame cache if duplicate storage becomes an issue.

## 8. Training and Evaluation Hooks
- Classification-only models continue to consume images plus labels; annotations stay optional.
- For MFA or explainable heads:
  - Extend `code/run_mfa_ffpp.py` (or add `code/run_mfa_effpp.py`) to read per-frame annotation JSON and enforce rule checks (Yes/No prefix, word count, tag vocabulary).
  - Expand `code/eval_mfa_ffpp.py` to compute textual metrics (tag precision, tag coverage, Yes/No compliance).
  - Update README and Appendix E after prototypes are ready.

## 9. QA Checklist
- Sample at least five identities per split:
  - Verify real and fake crops share the same frame index.
  - Confirm crop size and margin parity across the pair.
  - Check answers start with `Yes` or `No`, stay within 60 words, and reference only visible evidence.
  - Validate `evidence_tags` belong to the controlled vocabulary.
  - Ensure `pair` metadata points to existing video paths and the recorded splits.
- Maintain a lightweight status page (for example `reports/effpp_alignment_report.md`) summarising pass/fail counts.

---
**Next Actions**
1. Prototype the identity alignment script that emits `frame_indices` cache and highlights split mismatches.
2. Refactor `extract_ffpp_frames.py` into a modular cropper with margin strategies and detection caching.
3. Draft the JSON schema and tag vocabulary, then scaffold the placeholder annotation writer.
4. Integrate LLaVA / ChatGPT Mini call path with `.env` secrets and add a dry-run switch.

## Latest Updates (2025-10-08)
- `code/effpp_alignment.py` 生成 `data/effpp_cache/frame_indices/`（当前测试 1 个身份，支持 k=128 和 consistent-only 过滤）。
- `code/effpp_prepare_faces.py` 临时复用 `data/processed/ffpp_c23/faces_224/`，在 `data/effpp_cache/crops/` 建立对齐副本 + 元数据。
- `code/effpp_explain.py` 接入 ChatGPT Mini API（默认 `--mode chatgpt`），示例注释存放于 `data/effpp_ann/train/<method>/<identity>/`。
