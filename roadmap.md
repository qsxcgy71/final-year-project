# Roadmap · χ²-DFD MFA Pipeline (2025-09)

> 目标：打磨 FF++ c23 流程、明确评测口径、验证 Top-K 稳定性，并为下一阶段（EFF++）迁移预留接口。

## 0. 总览
- 当前阶段：MFA 复现与评测
- 下一阶段：EFF++ 数据迁移（待满足“指标齐全 + 流程可复现 + Top-K 稳定 + 文档完备”四项条件）

## 1. 收尾
- [ ] 校验 `metadata/mfa_feature_rankings.json` 字段：`id`, `question_en`, `question_zh`, `auc`, `r_pb`, `ci95`, `rank`
- [ ] 固定 Top-K（5~10 个）问题列表，写入 README / roadmap
- [ ] 计算 val/test 排名一致性（Spearman, Kendall τ）
- [ ] 汇总典型样例（TP/TN/FP/FN 各 3~4 个），导出帧路径 + 模型回答，生成 `reports/sample_cases.json`

## 2. 测量
- [ ] 扩展评测脚本：
  - 分类指标（frame/video, AUROC, AUPRC, F1；阈值由 Val 寻优）
  - MFA 指标（question-level AUC, r_pb, BA, CI、稳定性）
  - 轻量问卷模型（Top-K 加权得分）
  - 可解释性指标（关键词覆盖、代理热力图，逐步补充）
  - 效率指标（抽帧耗时、MFA 推理耗时 / 显存）
- [ ] 统一随机种子（2025）、数据切分、阈值求解流程
- [ ] 输出统一评测结果到 `eval/metrics_ffpp.json`

## 3. 验证
- [ ] 在 Celeb-DF v2 跑通完整流程（抽帧 → MFA）
- [ ] 比较 FF++ vs Celeb-DF 的 Top-K 一致性（Spearman, Kendall τ）
- [ ] （可选）做轻度退化实验（压缩、模糊、噪声），记录性能变化

## 4. 整理
- [ ] 整理目录结构：
  - `data/` 数据与缓存
  - `mfa/` 推理输出（JSON/JSONL）
  - `eval/` 指标结果与图表
  - `reports/` 样例、可视化素材
- [ ] 补写流程说明：输入 → 抽帧 → MFA → 评测 → 产出
- [ ] 更新 Appendix
  - A：数据清洗与切分策略
  - E：评测指标与脚本口径
  - F：硬件环境与运行时间
  - G：数据许可与伦理说明

## 5. 留口（为 EFF++ 准备）
- [ ] 检查 dataloader / 评测脚本是否支持 image-text 对
- [ ] 规划 EFF++ 使用的 manipulation 集、抽帧率、解释文本预处理
- [ ] 整理迁移计划与待办（Stage 1: EFF++ 数据基础与基线复评）

---
**里程碑判断标准**：
1. 指标齐全（分类 + MFA + 可解释性 + 效率）
2. 程序可复现（固定种子，重跑一致）
3. Top-K 稳定（跨库一致性良好）
4. 文档与样例墙准备完毕

满足以上条件后，再进入 EFF++ 阶段。
