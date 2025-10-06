# STEP 6: 测试与验证完成报告

> 本报告总结 2025-09 阶段对 χ²-DFD MFA 模块的全量验证情况，包括数据处理、模型推理与评估结果。

## 1. 功能概览
| 模块 | 状态 | 说明 |
|------|------|------|
| 环境与依赖 | ✅ | Python 3.10 + CUDA + bitsandbytes + insightface 运行稳定 |
| 数据划分 | ✅ | `code/mfa_metadata.py` 划分 FF++ c23 (4000/500/500) |
| 抽帧裁脸 | ✅ | `code/extract_ffpp_frames.py` 抽取 2 FPS、最多 16 帧并裁剪 224×224 人脸 |
| LLaVA 推理 | ✅ | `code/run_mfa_ffpp.py` 集成 LLaVA-1.5-7B 4bit 量化，支持断点续跑 |
| 结果汇总 | ✅ | 生成 val/test 统计与 Top-K 特征排名 |

## 2. 运行记录
- 抽帧脚本输出：`data/processed/ffpp_c23/faces_224/`、`raw_frames/`，摘要见 `summary_train/val/test.json`。
- MFA 推理：
  - 验证集 `metadata/mfa_ffpp_val_progress.jsonl`（500 条）
  - 测试集 `metadata/mfa_ffpp_test_progress.jsonl`（500 条）
  - 每 20 个视频打印进度日志，支持 `Ctrl+C` 续跑。

## 3. 核心指标
| Question ID | Category | Val BA | Test BA | Avg |
|-------------|----------|--------|---------|-----|
| facial_symmetry | Symmetry | 0.616 | 0.630 | **0.623** |
| shadow_anomaly | Lighting | 0.620 | 0.609 | **0.614** |
| hairline_artifact | Hair | 0.571 | 0.578 | **0.574** |
| edge_color_bleeding | Color | 0.556 | 0.546 | **0.551** |
| feature_perspective | Geometry | 0.531 | 0.539 | **0.535** |

更多问题统计参见 `metadata/mfa_ffpp_val.json` 与 `metadata/mfa_ffpp_test.json`，综合排名存于 `metadata/mfa_feature_rankings.json`。

## 4. 问题与改进建议
- **运行时间**：500 段视频推理约 60+ 小时；可调整 `--frames-per-video` 或问题集合缩短时间。
- **资源占用**：量化 LLaVA 需 8GB 显存、约 16GB RAM；建议在空闲 GPU 上运行。
- **误判分析**：可结合 `*_progress.jsonl` 中的 `prediction=false/true`，抽取代表性样本进行可视化。

## 5. 下一步工作
1. 选取 Top-K 问题构建轻量级分类器或加权评分模型。
2. 扩展到 Celeb-DF v2、DFDC 等跨库，评估迁移能力。
3. 结合热力图/Grad-CAM 等手段增强可解释性展示。
4. 整理实验脚本，封装为一键执行的 pipeline，便于复现。

> 截止目前，STEP 6 所有验证任务已完成，结果持续同步至 GitHub 以保障备份与沟通。
