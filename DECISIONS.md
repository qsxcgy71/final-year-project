# DECISIONS · Project Logbook

使用说明：每当形成“可传播的决定”，按下述模板追加一条；非决定性碎片请写入 progress.md。  
条目模板见本文件正文；热启动读序见 AGENTS.md 与 codex.md。  
最近更新：2025-10-28

## Index
- [2025-10-28] Stage 1 数据流水线：EFF++ dataloader 与文本指标脚本
- [2025-10-28] Stage 1 基础合并：整合 roadmap.md → PROJECT_ROADMAP.md
- [2025-10-28] 初始化：采用 PROJECT_ROADMAP.md 作为唯一权威路线图

---

## [2025-10-28] Stage 1 数据流水线：EFF++ dataloader 与文本指标脚本
**背景**：Stage 1 剩余工作需要让评测脚本读取图像-文本对，并对注释质量做自动化体检。  
**决策**：新增 `code/effpp_dataset.py`（帧级 Dataset + CLI）与 `code/eval_effpp_annotations.py`（Yes/No、词数、标签合法性统计，输出 `reports/effpp_annotation_metrics.{json,md}`）。  
**影响**：dataloader 子任务完成，评估脚本可直接复用；QA 面板仍需人工抽查与视觉确认。  
**回滚条件**：若后续改用在线裁剪而不复用缓存，需要同步调整 dataset 实现，可切换至 `code/effpp_crop.py` 重构产物。

---

## [2025-10-28] Stage 1 基础合并：整合 roadmap.md → PROJECT_ROADMAP.md
**背景**：Stage 1 已完成帧对齐与注释原型，但旧版 `roadmap.md` 仍保留独立任务清单，状态分散。  
**决策**：将旧 roadmap 任务并入 `PROJECT_ROADMAP.md`（补充 dataloader 检查、文本评价钩子等条目），历史内容归档到 `docs/archive/ROADMAP_FFPP_LEGACY.md`，根目录 `roadmap.md` 改为指向说明。  
**影响**：路线图与复选框集中到单一文件；Stage 1 剩余待办聚焦 QA 面板 / dataloader 支持 / 文本指标接入；后续只需维护 `PROJECT_ROADMAP.md` 与本日志。  
**回滚条件**：若团队仍需并行维护 FF++ 专用路线，可从归档恢复旧文件并在独立分支维护，但需避免双头管理。

---

## [2025-10-28] 初始化：采用 PROJECT_ROADMAP.md 作为唯一权威路线图
**背景**：旧版 `roadmap.md` 仅覆盖 FF++，新版本引入 EFF++ 与四阶段方案。  
**决策**：新建 `PROJECT_ROADMAP.md` 并设为唯一权威；旧文归档为 `docs/archive/ROADMAP_FFPP_LEGACY.md`。  
**影响**：后续任务以新路线图为准；Stage 0 仍保留 FF++ 作为回归基线。  
**回滚条件**：若一周内无法跑通 EFF++ 评测脚本，可暂时回退到 FF++ 流水线继续收尾。

---

## [yyyy-mm-dd] 阶段/主题（例如：Stage 1 QA 面板通过）
**假设/目标**：…  
**操作**：…（脚本、参数、样本量）  
**观察到的结果**：…（BA / AUC / AP / r_pb / 解释对齐指标）  
**结论（是否达成退出条件）**：…  
**影响面**：…（受影响的模块/数据/文档）  
**回滚条件**：…（触发回滚的场景）
