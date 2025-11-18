# CHECKPOINT - quick resume

Last update: 2025-11-03

Repo state:
- Current phase: Stage 1 / real-explanation replacement. Gemini 2.5 Flash (8 keys + proxy) has produced real text for identities 000-064 (65 identities total).
- Latest artefacts: `data/effpp_ann/` updated with Gemini annotations; throttle and key rotation implemented in `code/effpp_explain.py`.
- Outstanding hard goals: Finish remaining identities (065-999), then rerun `code/eval_effpp_annotations.py` and the QA panel.

How to continue (copy/paste plan):
1) Keep running `code/effpp_explain.py --mode chatgpt --chatgpt-provider gemini --identities <batch>` (20 identities per batch, next starting at 065).
2) Monitor for network/429 errors; the script rotates keys automatically and falls back to the proxy slot.
3) After full coverage, rerun metrics/QA and document Stage 1 completion in DECISIONS.md and PROJECT_ROADMAP.md before moving to Stage 2.
