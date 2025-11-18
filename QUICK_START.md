# Quick Start

Target: reproduce the χ²‑DFD MFA pipeline on FaceForensics++ (c23) and export evaluation artifacts that will support the upcoming EFF++ experiments.

## 1. Environment
```bash
python -m venv deepfake_env
# Windows
deepfake_env\Scripts\activate
# Linux/macOS
source deepfake_env/bin/activate

pip install -r requirements.txt
pip install insightface onnxruntime-gpu
```

## 2. Data & Models
1. Download FF++ (c23) into `data/ffpp_c23/` (keep original directory layout).
2. (Optional) Download Celeb-DF v2 into `data/celeb_df_v2/`.
3. Place `llava-hf/llava-1.5-7b-hf` under `models/` (you can run `python scripts/download_llava_cpu.py`).

## 3. Splits & Frame Extraction
```bash
python code/mfa_metadata.py  # outputs data/splits/ffpp_c23_split.{json,csv}
python code/extract_ffpp_frames.py --split train
python code/extract_ffpp_frames.py --split val
python code/extract_ffpp_frames.py --split test
# extra methods (FaceShifter / DeepFakeDetection)
python code/extract_ffpp_frames.py --split extra --include-extra
```

## 4. LLaVA-MFA Inference (resumable)
```bash
python code/run_mfa_ffpp.py --split val  --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
python code/run_mfa_ffpp.py --split test --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
```
- Progress logs are written to `mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`; you can stop/restart without losing work.

## 5. Metrics & Samples
```bash
python code/eval_mfa_ffpp.py         # eval/ffpp_c23/metrics.json
default metrics: BA, AUC, AP, r_pb, CI, pooling (mean/max/topk), rank stability, efficiency
python code/generate_sample_cases.py # reports/sample_cases.json (TP/TN/FP/FN examples)
```

## 6. Where to Look
- Top-K ranking: `mfa/ffpp_c23/mfa_feature_rankings.json`
- Unified metrics panel: `eval/ffpp_c23/metrics.json`
- Progress logs: `mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`
- Sample wall assets: `reports/sample_cases.json`

## 7. Common Pitfalls
| Issue | Checklist |
|-------|-----------|
| `insightface` install fails | Install Visual Studio Build Tools (MSVC) → retry `pip install insightface onnxruntime-gpu` |
| LLaVA load is slow | First 4bit load takes ~30–40 s; keep the process running |
| GPU memory errors | Reduce `--frames-per-video` or trim the question list |
| Large files staged in git | Always run `git status`; raw data, processed caches, and models are ignored via `.gitignore` |

## 8. Next Steps
Consult [`roadmap.md`](roadmap.md) for the five work blocks (seal / measure / validate / organize / prepare) before switching to EFF++.
