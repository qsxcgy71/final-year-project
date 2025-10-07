# Roadmap · χ²-DFD MFA Pipeline (FF++ → EFF++)

> Goal: lock down the FF++ c23 workflow (“seal the ruler”) so that swapping to new datasets (e.g., EFF++) becomes a drop-in change. Progress is tracked across five blocks.

## ✅ 0. Snapshot
- Metrics: `eval/ffpp_c23/metrics.json`
- Feature ranking: `mfa/ffpp_c23/mfa_feature_rankings.json`
- Progress logs: `mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`
- Sample wall: `reports/sample_cases.json`

## 1. 收尾 (Wrap-up)
- [x] Feature ranking enriched (`id`, `category`, `question_en`, `question_zh` placeholder, BA/AUC/AP/r_pb/CI, rank)
- [x] Rank stability (Spearman / Kendall τ) logged in metrics
- [x] Sample wall (`reports/sample_cases.json`) with TP/TN/FP/FN examples for top question
- [ ] Replace `question_zh` placeholders with validated Chinese text / translations
- [ ] Create visual “sample wall” (mosaic or Markdown gallery) for report appendix

## 2. 测量 (Measurement Panel)
- [x] `eval_mfa_ffpp.py` aggregates frame-level & video-level metrics (mean/max/top‑k pooling)
- [x] Balanced accuracy CI, r_pb, AUC, AP per question
- [x] Mean/max/top‑k light-weight “questionnaire” model with val-tuned thresholds
- [x] Extraction efficiency summary (`summary_*.json` consolidated in metrics)
- [ ] Log per-video MFA runtime / GPU memory profile (profiling hooks TBD)
- [ ] Document evaluation seeds (fixed to 2025) & threshold selection rules in Appendix E

## 3. 验证 (Validation & Generalization)
- [ ] Run the same pipeline on Celeb-DF v2 (抽帧 → MFA → `eval/celebdf_v2/metrics.json`)
- [ ] Compare FF++ vs Celeb-DF Top-K (Spearman / Kendall); flag stable cues for migration
- [ ] (Optional) Mild degradation test on FF++ (c23→c40, blur, noise) + delta metrics

## 4. 整理 (Organization & Docs)
- [x] Directory layout frozen (`data/`, `mfa/`, `eval/`, `reports/`)
- [x] README / Quick Start / Project Files rewritten around new structure
- [ ] Write one-page pipeline overview (input → extraction → MFA → metrics → outputs)
- [ ] Update Appendices:
  - A: data preprocessing & split protocol
  - E: evaluation metrics & scripts
  - F: hardware & runtime stats
  - G: dataset licensing / ethical notes

## 5. 留口 (Prepare for EFF++)
- [ ] Check dataloaders & evaluation scripts support image-text pairs
- [ ] Draft EFF++ migration plan (manipulation families, frame sampling rate, explanation preprocessing, licensing)
- [ ] Add placeholder hooks for textual evaluation (e.g., ROUGE/BLEU when explanations become available)

---
**Exit Criteria (before switching to EFF++)**
1. Metrics panel complete (classification + MFA + explainability proxy + efficiency)
2. Reproducible reruns (fixed seeds, deterministic splits, logged thresholds)
3. Top-K cues stable across datasets
4. Documentation & sample wall ready for reporting

Progress updates belong here; feel free to mark tasks with `[x]`, `[ ]`, or add notes as we close each block.
