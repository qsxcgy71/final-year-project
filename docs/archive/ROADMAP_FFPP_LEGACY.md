# Roadmap χ²-DFD MFA Pipeline (FF++ → EFF++)

> 目标：夯实 FF++ c23 流水线（“定尺”），把 EFF++ 迁移变成可插拔更新；进度按五个模块追踪。

## 0. 快照
- 指标：`eval/ffpp_c23/metrics.json`
- 特征排序：`mfa/ffpp_c23/mfa_feature_rankings.json`
- 进度日志：`mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`
- 样例墙：`reports/sample_cases.json`

## 1. 收尾 (Wrap-up)
- [x] 特征排序补充 `id` / `category` / `question_en` / `question_zh` 占位 / BA / AUC / AP / r_pb / CI / rank
- [x] 排名稳定性（Spearman / Kendall τ）写入 metrics
- [x] 样例墙 `reports/sample_cases.json`，覆盖该 split 的 TP/TN/FP/FN
- [ ] 将 `question_zh` 占位替换为校对后的中文
- [ ] 生成可视化“样例墙”（拼图或 Markdown gallery）用于报告附录

## 2. 测量面板 (Measurement Panel)
- [x] `eval_mfa_ffpp.py` 汇总帧级 & 视频级指标（mean/max/top-k pooling）
- [x] 每题输出 Balanced Accuracy CI、r_pb、AUC、AP
- [x] mean/max/top-k 轻量问卷模型（val 上调参阈值）
- [x] 抽取效率汇总（`summary_*.json` 收敛至 metrics）
- [ ] 记录每个视频的 MFA 运行时 / GPU 显存（profiling hook 待定）
- [ ] 在附录 E 说明评估随机种子（固定 2025）与阈值选取规则

## 3. 验证与泛化 (Validation & Generalization)
- [ ] 在 Celeb-DF v2 上复刻流水线（MFA 输出到 `eval/celebdf_v2/metrics.json`）
- [ ] 比对 FF++ 与 Celeb-DF Top-K（Spearman / Kendall），圈定可迁移的 cue
- [ ] （可选）对 FF++ 做轻度退化（c23→c40、模糊、噪声）并记录指标变化

## 4. 组织与文档 (Organization & Docs)
- [x] 目录结构冻结（`data/`、`mfa/`、`eval/`、`reports/`）
- [x] README / Quick Start / Project Files 围绕新结构重写
- [ ] 撰写 1 页流水线概览（输入 → 抽取 → MFA → 指标 → 输出）
- [ ] 更新附录：
  - A：数据预处理与划分策略
  - E：评估指标与脚本
  - F：硬件 / 运行时统计
  - G：数据集许可 / 伦理说明

## 5. 面向 EFF++ (Prepare for EFF++)
- [ ] 核对 dataloader 与评估脚本是否支持图像-文本对（引用 `reports/EFFPP_migration_plan.md`）
- [x] 身份级帧对齐脚本：输出 `data/effpp_cache/frame_indices/<identity>.json`（见 `code/effpp_alignment.py`），summary.json 统计同/跨 split 情况
- [x] 统一裁剪模块：阶段性改用 `code/effpp_prepare_faces.py` 复用 `faces_224`，生成 `data/effpp_cache/crops/`（后续可替换为全量裁剪）
- [x] 注释 schema 与标签集：`config/effpp_frame_schema.json`、`config/effpp_tags.json`、`config/effpp_mts.json` + 校验器 `code/effpp_schema.py`
- [x] CFAD 解释生成：`code/effpp_explain.py` 已接入 ChatGPT Mini API，生成示例注释（支持 placeholder / llava / chatgpt）
- [ ] QA 面板：抽查 5 个身份/划分，检查对齐、裁剪、Yes/No 前缀/字数、标签合法性，并汇总到 `reports/effpp_alignment_report.md`

---
**退出条件（在切换到 EFF++ 前）**
1. 指标面板完整（分类 + MFA + 可解释性代理 + 效率）
2. 可复现实验（种子固定、划分确定、阈值有记录）
3. Top-K cue 在跨数据集上稳定
4. 文档与样例墙就绪，可直接用于汇报

更新时在此标记任务状态，必要时添加补充说明。
