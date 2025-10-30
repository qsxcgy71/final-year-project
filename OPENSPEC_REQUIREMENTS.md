# OpenSpec 风格需求蓝图

## 目标与适用范围
- **目标**：将 X²-DFD → EFF++ 项目当前的关键能力、质量门槛与工作流，用 OpenSpec 的“规格-变更”范式重构为可执行的需求蓝图。
- **适用范围**：涵盖 Stage 0~4 的核心能力、解释对齐与效率指标，以及与 AI 协作者协同时的任务拆解方法。

## OpenSpec 工作流映射
OpenSpec 将“当前真相”（`openspec/specs/`）与“变更提案”（`openspec/changes/`）拆分管理。结合本项目：

| OpenSpec 构件 | 项目映射 | 说明 |
| --- | --- | --- |
| `specs/` | `PROJECT_ROADMAP.md`、`DECISIONS.md` 中的稳定要求 | 形成“现行规范”，确保 Stage 0~4 的指标、退出条件固定可查。|
| `changes/<feature>/proposal.md` | 针对 Stage 待办（如 Stage 1 QA 面板、Stage 2 PEFT）形成的任务意图说明 | 明确为什么需要这次变更、依赖与风险。|
| `changes/<feature>/tasks.md` | 拆解到脚本/实验的执行清单 | 与现有 scripts、code 子目录一一对齐。|
| `changes/<feature>/specs/` | 变更后应写回 `PROJECT_ROADMAP.md` 或配置文件的差异草稿 | 通过“delta”形式描述指标门槛或流程调整。|

> 建议在根目录增设 `openspec/` 结构，通过自动化 Agent 生成 proposal/tasks/spec delta，以便多人协同评审与归档。

## 当前规格（specs）概要
以下条目采用 OpenSpec 推荐的“Requirement + Scenario”结构，提炼现有路线图的硬性约束。

### Requirement: Baseline Integrity (Stage 0)
- **描述**：系统 SHALL 维持 FF++ c23 流水线的可复现性，作为后续迁移的对照基准。
- **Scenario: Metrics Coverage**
  - GIVEN 评估脚本运行完成
  - WHEN 生成 `eval/ffpp_c23/metrics.json`
  - THEN 文件 MUST 包含 BA、AUC、AP、r_pb、Spearman、Kendall τ 等指标的最新数值。
- **Scenario: Case Library**
  - GIVEN 抽样 TP/TN/FP/FN 案例
  - WHEN 更新 `reports/sample_cases.json`
  - THEN 每类 MUST 至少保留一组图像-解释配对，供 QA 抽查。

### Requirement: Interpretable EFF++ Dataset (Stage 1)
- **描述**：系统 SHALL 产出帧级图像-文本对，并保证解释质量可验证。
- **Scenario: Alignment Cache**
  - GIVEN 原始数据位于 `data/ffpp_c23/`
  - WHEN 运行对齐脚本
  - THEN MUST 生成 `data/effpp_cache/frame_indices/` 与对应裁剪缓存。
- **Scenario: Annotation Metrics**
  - GIVEN `code/eval_effpp_annotations.py` 执行完成
  - WHEN 输出 `reports/effpp_annotation_metrics.json`
  - THEN MUST 记录 Yes/No 准确率、文本覆盖率与冗余度，且结果可在 DECISIONS.md 中引用。

### Requirement: PEFT Alignment (Stage 2)
- **描述**：系统 SHALL 在不显著增加计算成本的前提下，实现统计显著的 BA/AUC 提升。
- **Scenario: Hyperparameter Grid**
  - GIVEN 设定学习率 × 提示长度网格
  - WHEN 在验证集上跑完实验
  - THEN MUST 将最优组合写入 `eval/effpp_peft/metrics.json`，并声明显存/时延增量。

### Requirement: Weak-Feature Plugins (Stage 3)
- **描述**：系统 SHALL 针对薄弱伪迹提供结构化插件证据，并纳入最终解释链路。
- **Scenario: Error Diagnostics**
  - GIVEN Stage 2 的误差日志
  - WHEN 编写 `reports/effpp_error_analysis.md`
  - THEN MUST 标注主导薄弱模式并映射到待开发插件。
- **Scenario: Evidence Stitching**
  - GIVEN 插件输出分数或掩码
  - WHEN 调用解释生成模块
  - THEN 文本 MUST 引用插件证据片段，且可在 QA 面板中验证。

### Requirement: Feature-Aware LoRA (Stage 4)
- **描述**：系统 SHALL 仅在目标层位启用 LoRA，并显式记录参数增量与性能收益。
- **Scenario: Layer Selection Rationale**
  - GIVEN 梯度热力或贡献度分析
  - WHEN 选择 LoRA 层与秩
  - THEN MUST 在 `code/lora_configs/` 存储配置，同时在 DECISIONS.md 写明选择依据与回滚条件。

## 变更提案（changes）骨架
结合当前待办，可预先定义以下变更文件夹以驱动 AI 协同：

1. `openspec/changes/stage1-qa-panel/`
   - `proposal.md`：描述 QA 面板覆盖率不足的风险与验收标准。
   - `tasks.md`：细化抽样策略、可视化脚本、人工复核流程。
   - `specs/project/roadmap.md`：更新 Stage 1 退出条件的 delta（如加入样例墙验收项）。

2. `openspec/changes/peft-grid-evaluation/`
   - `proposal.md`：定义超参网格、预算线与评估指标。
   - `tasks.md`：列出实验脚本、日志整理与 metrics 写入步骤。
   - `specs/config/effpp_peft.yaml`（若新增配置）或对现有 DECISIONS 条目的补充草稿。

3. `openspec/changes/feature-aware-lora/`
   - `proposal.md`：总结触发 LoRA 的误差模式与预期收益。
   - `tasks.md`：划分数据准备、训练、评估与回滚验证动作。
   - `specs/code/lora_configs/`：以 delta 形式说明新增/调整的配置文件结构。

这些骨架可由 Agent 自动生成后再补充细节，实现“先对齐再编码”。

## 与既有文档的差异
- **对比 `PROJECT_ROADMAP.md`**：路线图按时间与阶段串联任务，本文件则提炼为“系统当前必须满足的行为 + 验收场景”，更接近 OpenSpec 的规格定义，便于 AI 直接引用。
- **对比 `DECISIONS.md`**：决策日志记录历史决策与影响面，本文件提供静态的“现行需求”基线；二者搭配即可区分“为什么这么做”与“现在必须做到什么”。
- **对比 `progress.md`**：进度文件偏向会话级备忘，不具备结构化验收标准。本文件通过 Requirement/Scenario 将抽象目标转换为可验证的条件。
- **对比 `roadmap.md`、`PROJECT_FILES.md` 等说明性文件**：这些文档提供索引或文件落点，本文件则关注行为规范与验收方式，便于生成 OpenSpec delta 与任务。

## 为什么借助 OpenSpec 更易梳理需求
1. **需求与实现解耦**：OpenSpec 强调先对齐规格再编码，避免 AI 直接改动代码导致的需求漂移，符合本项目“解释可验证 + 成本可控”的硬约束。
2. **多阶段协同清晰**：通过 `specs/` 与 `changes/` 的分层，可并行处理 Stage 2~4 的探索，而不会污染 Stage 0~1 的既定指标。
3. **自动化友好**：Agent 可基于本蓝图自动生成 proposal/tasks/delta，形成可审计的工作流，降低人工整理成本。
4. **回滚有据可依**：每个 Requirement 的 Scenario 即“验收脚本”，失败时能快速定位需要回退的决策或配置，与 DECISIONS.md 的回滚条目呼应。

> 下一步建议：初始化 `openspec/` 目录，让 Agents 生成首批 proposal/tasks；同时在 CI 中加入对上述 Scenario 的检测脚本，确保规格落地。
