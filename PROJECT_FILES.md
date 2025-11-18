# Project File Map (2025-09)

> Core directories tracked in Git. Raw datasets and model weights must be downloaded manually; see `.gitignore` for ignored paths.

## Top-level layout
```
final-year-project/
├── code/                 # scripts for extraction, MFA inference, evaluation
├── config/               # question configuration (MFA prompts)
├── data/                 # raw data (ffpp_c23, celeb_df_v2), processed caches, splits
├── eval/ffpp_c23/        # consolidated metrics (metrics.json)
├── mfa/ffpp_c23/         # LLaVA outputs, progress logs, feature rankings
├── reports/              # sample cases and visualization assets
├── models/               # local HuggingFace weights (ignored in git)
└── roadmap.md            # current work plan (seal FF++ → prep EFF++)
```

## Key files
| Path | Purpose |
|------|---------|
| `code/extract_ffpp_frames.py` | InsightFace frame extraction + 224×224 face crops |
| `code/run_mfa_ffpp.py` | LLaVA MFA inference (resumable progress logs) |
| `code/eval_mfa_ffpp.py` | Aggregates BA/AUC/AP/r_pb/CI, pooling metrics, efficiency |
| `code/generate_sample_cases.py` | Builds TP/TN/FP/FN sample wall (`reports/sample_cases.json`) |
| `config/mfa_questions.json` | 20 candidate questions (EN placeholders for now) |
| `data/splits/ffpp_c23_split.{json,csv}` | Train/val/test split metadata |
| `mfa/ffpp_c23/mfa_ffpp_<split>.{json,csv,jsonl}` | Question-level predictions & progress logs |
| `mfa/ffpp_c23/mfa_feature_rankings.json` | Ranked cues with BA/AUC/AP/r_pb/CI |
| `eval/ffpff_c23/metrics.json` | Unified panel: classification, pooling, rank stability, efficiency |
| `reports/sample_cases.json` | Representative examples per error type |

## Large assets (download manually)
- `data/ffpp_c23/` — FaceForensics++ c23 videos
- `data/celeb_df_v2/` — Celeb-DF v2 videos (optional)
- `models/llava-1.5-7b-hf/` — LLaVA 1.5 7B weights

> Before committing, run `git status` to ensure no large data/model files are staged.
