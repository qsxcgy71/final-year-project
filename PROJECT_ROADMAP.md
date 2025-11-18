PROJECT_ROADMAP — X²-DFD 到 EFF++（解释对齐、低成本微调）
0. 项目一句话

在承接 X²-DFD 的 MFA/SFS/WFS 思路上，以“带文本解释的 EFF++”为数据基座；加入 Prompt Injection（PEFT）先导对齐，再用“诊断驱动的轻量插件 + Feature‑Aware LoRA”对弱特征定点增益，在“解释可验证 + 成本可控”前提下提升准确度与泛化。

---

1. 背景对齐（与 X²-DFD 的差异点）

- 数据：从常规 FF++ 转到 EFF++（图像+文本对），让解释质量可被监督与验证（不再仅二分类标签）。
- 训练序列：在 SFS/LoRA 之前加入 PEFT 的先导阶段，低成本对齐 EFF++ 的特征与表述。
- 模块化补强：以“诊断 → 定向”的方式，为薄弱伪造痕迹（融合边界、颜色不一致等）挂接轻量插件（CNN/图像处理），其输出参与判定与解释。
- LoRA 策略：从“面向强特征的一体化 LoRA”转向 Feature‑Aware LoRA，仅在与弱特征最相关的层位做低秩适配。
- 评测约束：以“解释可验证（文本对齐）+ 计算效率”为贯穿四阶段的硬约束与里程碑指标。

---

2. 离线使用须知（执行前请先阅读）

按顺序阅读本页与下述文件，并遵循“分析 → 计划 → 执行 → 记录”的节奏：

1) PROJECT_ROADMAP.md（本页）
2) reports/EFFPP_migration_plan.md（若存在）
3) config/effpp_frame_schema.json、config/effpp_tags.json、config/effpp_mts.json
4) README.md / QUICK_START.md（若存在）
5) PROJECT.md（若存在，作为补充叙述）

阅读完后，应：
- 列出当次要触达的目标与退出条件
- 指定会修改/生成的文件清单
- 执行前给出计划步骤与回滚点
- 执行后更新 DECISIONS.md 与本页任务复选框

---

3. 目录与关键工件（统一规范）

```
code/                       # 抽帧、MFA、EFF++ 注释与后续插件/LoRA 脚本
config/                     # 问卷与 EFF++ frame schema、标签与摘要配置
data/
  ffpp_c23/                 # FF++ c23 原始视频（手动下载，gitignore 保护）
  celeb_df_v2/              # 可选：Celeb-DF v2 原始视频
  processed/ffpp_c23/       # 已有 faces_224 / raw_frames 缓存
  effpp_cache/
    frame_indices/          # code/effpp_alignment.py 产出身份对齐索引
    crops/                  # code/effpp_prepare_faces.py 复制的对齐裁剪
  splits/                   # ffpp_c23_split.{json,csv} 等元数据
mfa/ffpp_c23/               # LLaVA 问答输出、进度日志、特征排序
eval/
  ffpp_c23/metrics.json     # 基线指标面板
  celebdf_v2/metrics.json   # 迁移评估占位
reports/
  sample_cases.json
  EFFPP_migration_plan.md
  effpp_alignment_report.md # Stage 1 QA 完成后生成
docs/archive/               # 历史路线图（ROADMAP_FFPP_LEGACY.md）
models/                     # HuggingFace 模型缓存（不入库）
roadmap.md                  # 指向本路线图的提示文件
```

---

4. 指标与度量（贯穿全程）

- 分类与问答：Balanced Accuracy（含 CI）、AUC、AP、r_pb
- 问答池化：mean / max / top‑k（视频级）
- 稳定性：Spearman、Kendall τ（特征/问题排名稳定性）
- 效率：训练时长、显存、推理时延、参数增量（LoRA/PEFT）
- 解释对齐：基于 EFF++ 文本对的一致性/覆盖率/冗余（在评测钩子里统计）

---

5. 分阶段路线（Stage 0–4）

### Stage 0 - FF++ 基线巩固（已部分完成）

目标：把 FF++ c23 流水线定尺，形成后续迁移的对照与回归保护栏。

任务：
- [x] mfa_feature_rankings.json：补全 id/category/question_en/question_zh/BA/AUC/AP/r_pb/CI/rank
- [x] 排名稳定性（Spearman / Kendall τ）写入 eval/ffpp_c23/metrics.json
- [x] reports/sample_cases.json 覆盖 TP/TN/FP/FN
- [ ] question_zh 占位替换为校对中文
- [ ] 生成“样例墙”可视化（拼图或 Markdown gallery）

测量面板：
- [x] eval_mfa_ffpp.py 汇总帧/视频级指标
- [x] 输出 BA(CI)/r_pb/AUC/AP
- [x] mean/max/top‑k 的轻量问卷模型（val 上调参阈值）
- [x] 效率汇总落盘到 summary_*.json 与 metrics.json
- [ ] 为每视频记录 MFA 运行时与显存（profiling hook）

验证与泛化：
- [ ] 复刻于 Celeb‑DF v2（落盘到 eval/celebdf_v2/metrics.json）
- [ ] 比对 FF++ vs Celeb‑DF Top‑K（Spearman/Kendall），圈定可迁移 cue
- [ ] 轻度退化试验（c23→c40/模糊/噪声）记录鲁棒性

退出条件：
- 指标面板完整、实验可复现、Top‑K cue 跨数据集稳定、样例墙与文档就绪。

---

### Stage 1 — 迁移到 EFF++ 的可解释数据基座

目标

基于 FF++ 构建 帧级图像‑文本对 的 EFF++ 注释层：

- 成对对比（CFAD）：真/伪帧一一配对后输入 VLM 产出伪迹描述；
- 技术摘要（MTS）：为每类操控插入固定的一句话摘要；
- 统一 Yes/No + “Is this image manipulated?” 前缀与 Schema；
- 确保可复现、可抽检、可最小评估。

输入 / 输出

输入：data/ffpp_c23/ 原始视频或 processed/ffpp_c23/ 抽帧/对齐缓存

输出：
- 对齐索引：data/effpp_cache/frame_indices/<split>/<identity>.json
- 成对列表：data/effpp_cache/pairs/<split>/<method>/<identity>.pairs.json
- 面部裁剪：data/effpp_cache/crops/...（真/伪同策略）
- 注释：data/effpp_ann/<split>/<method>/<identity>/frame_xxxx.ann.json
- 统计与报告：reports/effpp_annotation_metrics_{split}.{json,md}、reports/effpp_alignment_report.md

必做任务（Must）

成对帧对齐（1‑to‑1） — code/effpp_alignment.py
- 规则写死：对每个 identity 的 {real, DF, F2F, FS, NT} 先求 最短帧数 N_min，各自视频在 [0, N_min) 做等间隔采样。
- 产出 pair_index/real_path/fake_path/method，固定 --seed 42。

统一人脸裁剪 — code/effpp_prepare_faces.py
- 真/伪两侧同一检测与外扩策略（推荐 RetinaFace + 固定边距）；落地到 effpp_cache/crops/，记录 run_meta.detector/expand。

MTS 一句话摘要 — config/mts_summaries.json
- 从 FF++ 官方描述提炼 DF/F2F/FS/NT 各 1 条固定文案；生成时按 method 强绑定插入。

解释生成（CFAD） — code/effpp_explain.py
- 成对输入：[REAL_IMAGE], [FAKE_IMAGE]（伪造帧）；单图输入（真实帧）。
- 通道一（默认）：本地 LLaVA（GPU，4bit/8bit/FP16 可切）；
- 通道二（可选）：API VLM 只做改写/复核（不得引入新事实）。
- 输出强制前缀：Yes/No + “Is this image manipulated?”，随后 CFAD 文本 + 对应 MTS 文本。
- 固定 --seed 42，将 llava_model_id/tokenizer_id/torch/cuda 写入 run_meta。

Schema 校验与文本统计 — code/effpp_schema.py, code/eval_effpp_annotations.py
- 校验 label_prefix/question/annotation.artifact_description/annotation.technique_summary/method/identity/pair_index/source/run_meta。
- 统计 Yes/No 比例、方法覆盖、长度分布、关键词覆盖率；落盘 reports/effpp_annotation_metrics_{split}.{json,md}。

QA 面板（抽查） — reports/effpp_alignment_report.md
- 抽查 5 个 identity × {train,val,test}：对齐截图、裁剪一致性、前缀合规、MTS‑method 一致、CFAD 含“部位词+伪迹词”。
- 附正反例图与相应 ann 片段。

Schema（最小必填）
```
{
  "image_path": ".../frame_0123.png",
  "identity": "000",
  "method": "DF|F2F|FS|NT|original",
  "pair_index": 37,
  "label_prefix": "Yes|No",
  "question": "Is this image manipulated?",
  "annotation": {
    "artifact_description": "具体伪迹 + 位置（或真实的自然线索）",
    "technique_summary": "来自 mts_summaries.json 的固定一句话"
  },
  "source": "local|api",
  "run_meta": {
    "seed": 42,
    "llava_model_id": "...",
    "tokenizer_id": "...",
    "retinaface_ckpt": "...",
    "torch": "2.x", "cuda": "12.x"
  }
}
```

Prompt（贴在仓库 /config/prompts.md）

伪造帧（成对 CFAD）
```
System: You compare a real face image and a manipulated one.
User: [REAL_IMAGE], [FAKE_IMAGE]
Instruction:
1) Begin with "Yes" or "No".
2) If manipulated, describe concrete artifacts and locations in 1–2 short sentences.
3) Mention the manipulation family summary: <{MTS_SUMMARY_FOR_METHOD}>.
Question: Is this image manipulated?
Style: Yes/No + one short paragraph (<=60 words). Do not guess identity/source/tool names.
```

真实帧（单图）
```
System: You check whether a face image is manipulated.
User: [REAL_IMAGE]
Instruction:
1) Start with "No" if unmanipulated, then briefly note natural cues (texture/lighting/boundary).
2) Keep it short (<=40 words). Do not speculate identity/source.
Question: Is this image manipulated?
```

度量（Stage 1 的硬指标）

- [x] 成对完整率 ≥ 99%（伪造帧均有真实对）。
- [x] 前缀合规率 = 100%（Yes|No + 固定问句）。
- [x] MTS 一致性 = 100%（summary 与 method 匹配）。
- [x] CFAD 结构性覆盖 ≥ 95%（文本同时含部位词与伪迹词）。
- [x] 真实帧自然线索率 ≥ 95%（含“纹理连贯/光照一致/边界自然/阴影连续”等）。
- [x] 长度约束：伪造 ≤ 60 词；真实 ≤ 40 




退出条件（通过即进入 Stage 2）

- [x] 三个 split 的 data/effpp_ann/.../*.ann.json 全量生成并通过 Schema 校验；
- [x] effpp_annotation_metrics_{split} 满足上表阈值；
- [x] effpp_alignment_report.md 抽查通过（对齐一致、前缀一致、MTS‑method 一致、CFAD 含位置信息）；
- [x] 所有入口支持 --seed，并将版本/依赖写入 run_meta；评测脚本能读图像‑文本对输出指标。
### Stage 2 - Prompt Injection（PEFT）先导对齐

目标：在冻结大部参数下，用可学习提示向量快速把模型对齐到 EFF++ 的文本与视觉分布。

任务：
- [ ] 训练/推理入口与 PEFT 配置（学习率、长度、插入位点）
- [ ] 在 val 上做 学习率 × 提示长度 网格；记录收敛曲线与效率
- [ ] 以 Stage 1 基线做“分类 + 解释对齐”双指标对比


- [ ] 将增量代价写入 eval/effpp_peft/metrics.json 与 DECISIONS.md

退出条件：
- 在不显著提高计算的前提下，实现统计显著的 BA/AUC 提升，且解释对齐指标不下降。

---

### Stage 3 - 诊断驱动的“弱特征插件”（WFS 增广）

目标：依据 Stage 2 的误差诊断，为薄弱 cue 定制轻量插件，其分数/标记参与融合与解释。

任务：
- [ ] 在 reports/effpp_error_analysis.md 标注主要薄弱模式（如：边界融合、色彩漂移、频带模糊等）
- [ ] 在 code/plugins/ 实现 1–2 个小插件（CNN 或图像处理），输出结构化分数/掩码
- [ ] 设计融合方式：规则/线性或学习式（记录参数量与延迟）
- [ ] 解释整合：把插件证据以自然语言短语拼接入最终解释（effpp_explain.py 添加钩子）

退出条件：
- 在指定薄弱模式子集上显著提升 BA/AUC/AP 或显著降低 FP/FN；解释文本能引用插件证据。

---

### Stage 4 - Feature‑Aware LoRA（定向层位微调）

目标：仅对与弱特征最相关的层位加 LoRA，低秩增益，成本可控。

任务：
- [ ] 依据 Stage 2/3 的“感受野贡献/梯度热力”或误差归因，选择层位与秩 r
- [ ] 在 code/lora_configs/ 存放对比配置（通用 vs 定向）
- [ ] 记录参数增量、时延变化与收益曲线
- [ ] 最佳配置写入 DECISIONS.md 与 eval/effpp_lora/metrics.json

退出条件：
- 在计算增量可控的前提下，整体指标再上台阶，且解释对齐稳定或更优。

---

6. 统一评测与里程碑（跨阶段追踪）

- 分类/问答：BA(CI)、AUC、AP、r_pb
- 解释对齐：一致性/覆盖率/冗余
- 效率：训练/推理时间、显存、参数增量
- 稳定性：排名相关（Spearman/Kendall）
- 跨数据集：FF++ / Celeb‑DF / EFF++ 子集

输出位置：
- eval/<dataset_or_stage>/metrics.json
- reports/sample_cases.json / effpp_alignment_report.md
- DECISIONS.md（关键抉择与理由）

---

7. 执行清单（每次运行都要遵守）

1) 读取：本页 + config/*.json + 最近的 DECISIONS.md
2) 打印计划：目标、文件写入点、回滚点
3) 最小变更：只改声明的文件；其余只读
4) 写入：产出物落在既定路径；追加日志到 <stage>_progress.jsonl
5) 记录：把关键信息同步到 DECISIONS.md（参数选择、消融结果、一句话结论）
6) 自检：跑快速评估，给出是否达成“退出条件”的结论与下一步建议

---

记忆包文件（热启动）

- 为保障“开新窗也能秒接上文”，每次会话结束前请：
  - 更新 progress.md（Done/Pending/Blockers/Next 各 1–3 行）
  - 覆盖 CHECKPOINT.md（当前阶段、最新产物路径、硬指标与三步续跑计划）
- 新会话默认读序：PROJECT_ROADMAP.md → DECISIONS.md → progress.md → CHECKPOINT.md（详见 AGENTS.md / codex.md）

---

8. 风险与缓解

- 解释漂移：文本生成可能自洽但与图像证据不一致；用 schema 校验与覆盖率/冗余指标约束。
- 插件过拟合：弱特征插件针对性强；加入退火与跨集验证；限制参数量与早停。
- 成本失控：LoRA/PEFT 叠加；固定“预算线”（显存/时延），超出即回退。
- 数据对齐误差：身份/帧对齐错误；强制运行 Stage 1 的 QA 面板后再进入后续阶段。

---

9. 开放决策（待填）

- [ ] PEFT 注入位点：输入侧/跨层/解码前？
- [ ] 插件清单：优先做哪两个薄弱模式？
- [ ] LoRA 层位与秩 r：基于哪种归因信号选择？
- [ ] 解释评价门槛：一致性 >= ? 覆盖率 >= ? 冗余 <= ?

> 每次定稿请在 DECISIONS.md 记录：决策 → 证据 → 影响面 → 回滚条件

---

10. 变更日志（摘录；按需续写）

- v0.9：合并 proposal 的改进方向与 roadmap；明确 Stage 0–4；引入解释对齐与效率双约束；补齐离线执行规范与文件落点。
- v0.8 及以前：FF++ 基线与 MFA 面板、初版 EFF++ 对齐脚本与 schema。

附：原有任务清单（已并入上文，保留复选）

- [ ] question_zh 校对替换
- [ ] 样例墙可视化
- [ ] MFA profiling（时延/显存）
- [ ] 附录 E（种子与阈值）
- [ ] Celeb‑DF 迁移与相关性分析
- [ ] 退化鲁棒性实验
- [ ] EFF++ QA 面板抽查与报告
PROJECT_ROADMAP — X²-DFD 到 EFF++（解释对齐、低成本微调）

0. 项目一句话

在承接 X²-DFD 的 MFA/SFS/WFS 思路上，以“带文本解释的 EFF++”为数据基座；加入 Prompt Injection（PEFT）先导对齐，再用“诊断驱动的轻量插件 + Feature‑Aware LoRA”对弱特征定点增益，在“解释可验证 + 成本可控”的前提下提升准确度与泛化。

---

1. 背景对齐（与 X²-DFD 的差异点）

- 数据：从常规 FF++ 转到 EFF++（图像+文本对），让解释质量可被监督与验证（不再仅二分类标签）。
- 训练序列：在 SFS/LoRA 之前加入 PEFT 的先导阶段，低成本对齐 EFF++ 的特征与表述。
- 模块化补强：以“诊断 → 定向”的方式，为薄弱伪造痕迹（融合边界、颜色不一致等）挂接轻量插件（CNN/图像处理），其输出参与判定与解释。
- LoRA 策略：从“面向强特征的一体化 LoRA”转向 Feature‑Aware LoRA，仅在与弱特征最相关的层位做低秩适配。
- 评测约束：以“解释可验证（文本对齐）+ 计算效率”为贯穿四阶段的硬约束与里程碑指标。

---

2. 离线使用须知（执行前请先阅读）

按顺序阅读本页与下述文件，并遵循“分析 → 计划 → 执行 → 记录”的节奏：

1) PROJECT_ROADMAP.md（本页）
2) reports/EFFPP_migration_plan.md（若存在）
3) config/effpp_frame_schema.json、config/effpp_tags.json、config/effpp_mts.json
4) README.md / QUICK_START.md（若存在）
5) PROJECT.md（若存在，作为补充叙述）

阅读完后，应：
- 列出当次要触达的目标与退出条件
- 指定会修改/生成的文件清单
- 执行前给出计划步骤与回滚点
- 执行后更新 DECISIONS.md 与本页任务复选框

---

3. 目录与关键工件（统一规范）

```
code/                       # 抽帧、MFA、EFF++ 注释与后续插件/LoRA 脚本
config/                     # 问卷与 EFF++ frame schema、标签与摘要配置
data/
  ffpp_c23/                 # FF++ c23 原始视频（手动下载，gitignore 保护）
  celeb_df_v2/              # 可选：Celeb-DF v2 原始视频
  processed/ffpp_c23/       # 已有 faces_224 / raw_frames 缓存
  effpp_cache/
    frame_indices/          # code/effpp_alignment.py 产出身份对齐索引
    crops/                  # code/effpp_prepare_faces.py 复制的对齐裁剪
  splits/                   # ffpp_c23_split.{json,csv} 等元数据
mfa/ffpp_c23/               # LLaVA 问答输出、进度日志、特征排序
eval/
  ffpp_c23/metrics.json     # 基线指标面板
  celebdf_v2/metrics.json   # 迁移评估占位
reports/
  sample_cases.json
  EFFPP_migration_plan.md
  effpp_alignment_report.md # Stage 1 QA 完成后生成
docs/archive/               # 历史路线图（ROADMAP_FFPP_LEGACY.md）
models/                     # HuggingFace 模型缓存（不入库）
roadmap.md                  # 指向本路线图的提示文件
```

---

4. 指标与度量（贯穿全程）

- 分类与问答：Balanced Accuracy（含 CI）、AUC、AP、r_pb
- 问答池化：mean / max / top‑k（视频级）
- 稳定性：Spearman、Kendall τ（特征/问题排名稳定性）
- 效率：训练时长、显存、推理时延、参数增量（LoRA/PEFT）
- 解释对齐：基于 EFF++ 文本对的一致性/覆盖率/冗余（在评测钩子里统计）

---

5. 分阶段路线（Stage 0–4）

### Stage 0 - FF++ 基线巩固（已部分完成）

目标：把 FF++ c23 流水线定尺，形成后续迁移的对照与回归保护栏。

任务：
- [x] mfa_feature_rankings.json：补全 id/category/question_en/question_zh/BA/AUC/AP/r_pb/CI/rank
- [x] 排名稳定性（Spearman / Kendall τ）写入 eval/ffpp_c23/metrics.json
- [x] reports/sample_cases.json 覆盖 TP/TN/FP/FN
- [ ] question_zh 占位替换为校对中文
- [ ] 生成“样例墙”可视化（拼图或 Markdown gallery）

测量面板：
- [x] eval_mfa_ffpp.py 汇总帧/视频级指标
- [x] 输出 BA(CI)/r_pb/AUC/AP
- [x] mean/max/top‑k 的轻量问卷模型（val 上调参阈值）
- [x] 效率汇总落盘到 summary_*.json 与 metrics.json
- [ ] 为每视频记录 MFA 运行时与显存（profiling hook）

验证与泛化：
- [ ] 复刻于 Celeb‑DF v2（落盘到 eval/celebdf_v2/metrics.json）
- [ ] 比对 FF++ vs Celeb‑DF Top‑K（Spearman/Kendall），圈定可迁移 cue
- [ ] 轻度退化试验（c23→c40/模糊/噪声）记录鲁棒性

退出条件：
- 指标面板完整、实验可复现、Top‑K cue 跨数据集稳定、样例墙与文档就绪。

---

### Stage 2 — Prompt Injection（PEFT）先导对齐

目标：在冻结大部参数下，用可学习提示向量快速把模型对齐到 EFF++ 的文本与视觉分布。

任务：
- [ ] 训练/推理入口与 PEFT 配置（学习率、长度、插入位点）
- [ ] 在 val 上做 学习率 × 提示长度 网格；记录收敛曲线与效率
- [ ] 以 Stage 1 基线做“分类 + 解释对齐”双指标对比
- [ ] 将增量代价写入 eval/effpp_peft/metrics.json 与 DECISIONS.md

退出条件：
- 在不显著提高计算的前提下，实现统计显著的 BA/AUC 提升，且解释对齐指标不下降。

---

### Stage 3 — 诊断驱动的“弱特征插件”（WFS 增广）

目标：依据 Stage 2 的误差诊断，为薄弱 cue 定制轻量插件，其分数/标记参与融合与解释。

任务：
- [ ] 在 reports/effpp_error_analysis.md 标注主要薄弱模式（如：边界融合、色彩漂移、频带模糊等）
- [ ] 在 code/plugins/ 实现 1–2 个小插件（CNN 或图像处理），输出结构化分数/掩码
- [ ] 设计融合方式：规则/线性或学习式（记录参数量与延迟）
- [ ] 解释整合：把插件证据以自然语言短语拼接入最终解释（effpp_explain.py 添加钩子）

退出条件：
- 在指定薄弱模式子集上显著提升 BA/AUC/AP 或显著降低 FP/FN；解释文本能引用插件证据。

---

### Stage 4 — Feature‑Aware LoRA（定向层位微调）

目标：仅对与弱特征最相关的层位加 LoRA，低秩增益，成本可控。

任务：
- [ ] 依据 Stage 2/3 的“感受野贡献/梯度热力”或误差归因，选择层位与秩 r
- [ ] 在 code/lora_configs/ 存放对比配置（通用 vs 定向）
- [ ] 记录参数增量、时延变化与收益曲线
- [ ] 最佳配置写入 DECISIONS.md 与 eval/effpp_lora/metrics.json

退出条件：
- 在计算增量可控的前提下，整体指标再上台阶，且解释对齐稳定或更优。

---

6. 统一评测与里程碑（跨阶段追踪）

- 分类/问答：BA(CI)、AUC、AP、r_pb
- 解释对齐：一致性/覆盖率/冗余
- 效率：训练/推理时间、显存、参数增量
- 稳定性：排名相关（Spearman/Kendall）
- 跨数据集：FF++ / Celeb‑DF / EFF++ 子集

输出位置：
- eval/<dataset_or_stage>/metrics.json
- reports/sample_cases.json / effpp_alignment_report.md
- DECISIONS.md（关键抉择与理由）

---

7. 执行清单（每次运行都要遵守）

1) 读取：本页 + config/*.json + 最近的 DECISIONS.md
2) 打印计划：目标、文件写入点、回滚点
3) 最小变更：只改声明的文件；其余只读
4) 写入：产出物落在既定路径；追加日志到 <stage>_progress.jsonl
5) 记录：把关键信息同步到 DECISIONS.md（参数选择、消融结果、一句话结论）
6) 自检：跑快速评估，给出是否达成“退出条件”的结论与下一步建议

---

8. 风险与缓解

- 解释漂移：文本生成可能自洽但与图像证据不一致；用 schema 校验与覆盖率/冗余指标约束。
- 插件过拟合：弱特征插件针对性强；加入退火与跨集验证；限制参数量与早停。
- 成本失控：LoRA/PEFT 叠加；固定“预算线”（显存/时延），超出即回退。
- 数据对齐误差：身份/帧对齐错误；强制运行 Stage 1 的 QA 面板后再进入后续阶段。

---

9. 开放决策（待填）

- [ ] PEFT 注入位点：输入侧/跨层/解码前？
- [ ] 插件清单：优先做哪两个薄弱模式？
- [ ] LoRA 层位与秩 r：基于哪种归因信号选择？
- [ ] 解释评价门槛：一致性 >= ? 覆盖率 >= ? 冗余 <= ?

> 每次定稿请在 DECISIONS.md 记录：决策 → 证据 → 影响面 → 回滚条件

---

10. 变更日志（摘录；按需续写）

- v0.9：合并 proposal 的改进方向与 roadmap；明确 Stage 0–4；引入解释对齐与效率双约束；补齐离线执行规范与文件落点。
- v0.8 及以前：FF++ 基线与 MFA 面板、初版 EFF++ 对齐脚本与 schema。


