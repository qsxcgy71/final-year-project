# χ²-DFD Deepfake Detection · MFA Progress (FF++ c23)

This repo tracks the reproduction of the **Model Feature Assessment (MFA)** module described in *“χ²-DFD: A Framework for Explainable and Extendable Deepfake Detection”*. We now have a fully scripted pipeline to run LLaVA‑1.5‑7B (4bit) on FaceForensics++ (c23), log per-question votes, rank discriminative cues, and export evaluation panels and sample cases. The goal for this phase is to make the FF++ workflow robust before switching to new datasets (e.g., EFF++).

## 📌 Current Milestones (2025‑09)
- ✅ Downloaded & cleaned FF++ c23; stratified 4000/500/500 train/val/test splits (data/splits/).
- ✅ InsightFace-based frame extraction (2 FPS, ≤16 frames/video) with logs in `data/processed/ffpp_c23/summary_*.json`.
- ✅ LLaVA MFA inference with resumable progress logs (`mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`).
- ✅ Unified evaluation panel (`eval/ffpp_c23/metrics.json`) and feature ranking (`mfa/ffpp_c23/mfa_feature_rankings.json`), plus sample cases (`reports/sample_cases.json`).

### Top‑10 MFA Questions (val/test metrics)
| Rank | Question ID | Category | Val BA | Test BA | Val AUC | Test AUC |
|------|-------------|----------|--------|---------|---------|----------|
| 1 | facial_symmetry | Symmetry | 0.616 | 0.630 | 0.646 | 0.657 |
| 2 | shadow_anomaly | Lighting | 0.620 | 0.609 | 0.639 | 0.639 |
| 3 | hairline_artifact | Hair | 0.571 | 0.578 | 0.607 | 0.623 |
| 4 | edge_color_bleeding | Color | 0.556 | 0.546 | 0.587 | 0.589 |
| 5 | feature_perspective | Geometry | 0.531 | 0.539 | 0.536 | 0.571 |
| 6 | compression_inconsistency | Signal | 0.529 | 0.529 | 0.525 | 0.546 |
| 7 | teeth_boundary_drift | Mouth | 0.523 | 0.510 | 0.531 | 0.526 |
| 8 | skin_texture_repeat | Texture | 0.513 | 0.512 | 0.520 | 0.526 |
| 9 | feature_proportions | Symmetry | 0.510 | 0.515 | 0.524 | 0.532 |
| 10 | jawline_seams | Blending | 0.509 | 0.512 | 0.533 | 0.529 |

> Rank stability: Spearman = 0.787, Kendall τ = 0.654 (val vs. test). See [`eval/ffpp_c23/metrics.json`](eval/ffpp_c23/metrics.json) for full statistics (BA, AUC, AP, r_pb, CI, pooling metrics, efficiency).

## ⚙️ Environment
- Python 3.10 (virtualenv recommended)
- CUDA‑capable GPU ≥8 GB
- Dependencies: `torch`, `transformers`, `accelerate`, `bitsandbytes`, `opencv-python-headless`, `insightface`, `onnxruntime-gpu`
- Local model: place `llava-hf/llava-1.5-7b-hf` under `models/`

## 🚀 Quick Recipe
```bash
# 1. virtualenv & deps
python -m venv deepfake_env
# Windows
deepfake_env\Scripts\activate
# Linux/macOS
source deepfake_env/bin/activate

pip install -r requirements.txt
pip install insightface onnxruntime-gpu

# 2. dataset split & frame extraction
python code/mfa_metadata.py
python code/extract_ffpp_frames.py --split train
python code/extract_ffpp_frames.py --split val
python code/extract_ffpp_frames.py --split test
# optional (FaceShifter / DeepFakeDetection)
python code/extract_ffpp_frames.py --split extra --include-extra

# 3. MFA inference (resumable)
python code/run_mfa_ffpp.py --split val  --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
python code/run_mfa_ffpp.py --split test --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20

# 4. Evaluation & sample wall
python code/eval_mfa_ffpp.py
python code/generate_sample_cases.py
```

Artifacts (stored in Git):
- `data/splits/ffpp_c23_split.{json,csv}` — stratified splits
- `mfa/ffpp_c23/mfa_ffpp_<split>.{json,jsonl,csv}` — question-level outputs
- `eval/ffpp_c23/metrics.json` — consolidated metrics (frame/video, pooling, stability, efficiency)
- `mfa/ffpp_c23/mfa_feature_rankings.json` — Top‑K ranking with BA/AUC/AP/r_pb/CI
- `reports/sample_cases.json` — representative TP/TN/FP/FN frames for the top question

## 📁 Repo Snapshot
```
code/
  ├── extract_ffpp_frames.py   # InsightFace frame extraction & face crops
  ├── run_mfa_ffpp.py          # LLaVA batch inference (progress logs, resumable)
  ├── eval_mfa_ffpp.py         # metrics panel (classification + MFA + efficiency)
  ├── generate_sample_cases.py # export representative examples
  └── ...
config/mfa_questions.json      # MFA question list (EN/placeholder ZH)
data/
  ├── ffpp_c23/                # raw videos (manual download)
  ├── splits/                  # metadata outputs
  └── processed/ffpp_c23/      # cached frames/faces (generated)
mfa/ffpp_c23/                  # MFA outputs & rankings
eval/ffpp_c23/                 # metrics.json, future plots
reports/                       # sample cases & supporting assets
roadmap.md                     # task tracker (seal FF++, prep for EFF++)
```

## 📚 Next Steps
All follow-up tasks are tracked in [`roadmap.md`](roadmap.md):
1. **Seal FF++** — finalize Top‑K metadata, rank stability, sample wall.
2. **Measurement** — enrich metrics (frame/video, pooling, efficiency) & standardize seeds/thresholds.
3. **Validation** — replicate on Celeb-DF v2, test robustness under mild degradation.
4. **Organization** — frozen directory layout, appendix updates, reproducible documentation.
5. **Prepare EFF++** — ensure loaders handle image-text pairs, draft migration plan & licensing notes.

## 🤝 Contributing & Notes
- Large assets (`data/ffpp_c23`, `data/celeb_df_v2`, `data/processed`, `models`) are ignored by Git.
- Run `code/eval_mfa_ffpp.py` after MFA runs to refresh metrics; re-run `generate_sample_cases.py` when progress logs change.
- Contributions welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

Enjoy exploring the MFA pipeline, and keep the “尺子” steady before we move on to EFF++! 
