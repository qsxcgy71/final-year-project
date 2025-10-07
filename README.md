# χ²-DFD 深度伪造检测系统（MFA 复现进度）

基于论文 **“χ²-DFD: A Framework for Explainable and Extendable Deepfake Detection”**，本仓库聚焦复现其中的 **Model Feature Assessment (MFA)** 模块，落地 FaceForensics++ (c23) 的批量评测，并将结果整理成可复用的流程，为后续迁移到 EFF++ 等数据集做准备。

## 📌 2025-09 里程碑
- ✅ 完成 FF++ c23 的 4000/500/500 分层划分、抽帧裁脸缓存（2 FPS，≤16 帧/段）。
- ✅ 集成 LLaVA-1.5-7B（nf4 量化），支持断点续跑与进度日志 (`mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`)。
- ✅ 输出统一评测面板：`eval/ffpp_c23/metrics.json`、Top-K 排名 `mfa/ffpp_c23/mfa_feature_rankings.json`、样例墙 `reports/sample_cases.json`。

### Top-10 问题（val/test 指标）
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

> 完整统计与稳定性指标详见 [`eval/ffpp_c23/metrics.json`](eval/ffpp_c23/metrics.json)。

## ⚙️ 环境依赖
- Python 3.10（建议 virtualenv）
- CUDA 兼容 GPU（≥8 GB 显存）
- 关键依赖：`torch`、`transformers`、`accelerate`、`bitsandbytes`、`opencv-python-headless`、`insightface`、`onnxruntime-gpu`
- 本地 HuggingFace 权重：`models/llava-1.5-7b-hf/`

## 🚀 快速复现流程
```bash
# 1. 虚拟环境
python -m venv deepfake_env
# Windows
deepfake_env\Scripts\activate
# Linux/macOS
source deepfake_env/bin/activate

pip install -r requirements.txt
pip install insightface onnxruntime-gpu

# 2. 数据划分
python code/mfa_metadata.py  # 输出 data/splits/ffpp_c23_split.{json,csv}

# 3. 抽帧与裁脸（可断点续跑）
python code/extract_ffpp_frames.py --split train
python code/extract_ffpp_frames.py --split val
python code/extract_ffpp_frames.py --split test
# 若需 FaceShifter / DeepFakeDetection：
python code/extract_ffpp_frames.py --split extra --include-extra

# 4. MFA 推理
python code/run_mfa_ffpp.py --split val  --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
python code/run_mfa_ffpp.py --split test --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20

# 5. 评测&素材
python code/eval_mfa_ffpp.py        # 生成 eval/ffpp_c23/metrics.json
python code/generate_sample_cases.py # 生成 reports/sample_cases.json
```
> 脚本支持断点续跑，进度存于 `mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`，重复执行会自动跳过已完成视频。

## 📂 目录结构（核心）
```
code/
  ├── extract_ffpp_frames.py   # InsightFace 抽帧 & 裁脸
  ├── run_mfa_dataset.py?      # TODO: 数据集通用化（roadmap）
  ├── run_mfa_ffpp.py          # LLaVA 批量推理 + 日志
  ├── eval_mfa_ffpp.py         # 指标汇总
  ├── generate_sample_cases.py # 样例墙抽取
  └── ...                      # 其他辅助脚本
config/
  └── mfa_questions.json       # 问题清单
roadmap.md                      # 当前阶段任务与里程碑
mfa/
  └── ffpp_c23/
      ├── mfa_ffpp_val*.json[l]
      ├── mfa_ffpp_test*.json[l]
      └── mfa_feature_rankings.json
eval/
  └── ffpp_c23/
      └── metrics.json
reports/
  └── sample_cases.json
data/
  ├── ffpp_c23/                # 原始视频（需自行下载）
  ├── processed/ffpp_c23/      # 抽帧缓存（自动生成）
  └── splits/ffpp_c23_split.*  # 划分文件
```

## 🔁 当前工作重点
详见 [`roadmap.md`](roadmap.md)。概要：
1. **收尾**：补齐 question metrics 字段、Top-K 列表、Spearman/Kendall、一套样例墙。
2. **测量**：完善分类/MFA/可解释性/效率指标，统一随机种子与阈值口径。
3. **验证**：在 Celeb-DF v2 复现流程，比较 Top-K 一致性，视情况做轻度退化实验。
4. **整理**：统一目录、补 Appendix，确保流程可复用。
5. **留口**：检查脚本兼容 image-text，对接 EFF++ 迁移计划与数据许可说明。

## 📚 参考
- 原论文：*χ²-DFD: A Framework for Explainable and Extendable Deepfake Detection*
- LLaVA 官方仓库与 HuggingFace 权重

---
如需贡献或反馈，请查阅 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
