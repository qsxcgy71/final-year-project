# χ²-DFD 深度伪造检测系统（复现进度）

基于论文 **“χ²-DFD: A Framework for Explainable and Extendable Deepfake Detection”**，本仓库聚焦于复现其中的 **Model Feature Assessment (MFA)** 模块，并在此基础上扩展真实数据集实验与特征筛选流程。本阶段我们在本地离线环境中集成了 LLaVA-1.5-7B（4bit 量化）模型，对 FaceForensics++ (c23) 数据集开展特征问题评估。

## 📌 最新进展（2025-09）
- ✅ 下载并清洗 FF++ c23 数据集，完成 4000/500/500（train/val/test）的分层划分与抽帧裁脸缓存。
- ✅ 本地加载 LLaVA-1.5-7B (nf4 量化) 并实现批量问题判别，支持断点续跑与实时进度日志。
- ✅ 生成验证 / 测试集的 MFA 统计，融合成 `metadata/mfa_feature_rankings.json`，筛选最具判别力的 10 个问题：

| Rank | Question ID | Category | Val BA | Test BA | Avg BA |
|------|-------------|----------|--------|---------|--------|
| 1 | facial_symmetry | Symmetry | 0.616 | 0.630 | **0.623** |
| 2 | shadow_anomaly | Lighting | 0.620 | 0.609 | **0.614** |
| 3 | hairline_artifact | Hair | 0.571 | 0.578 | **0.574** |
| 4 | edge_color_bleeding | Color | 0.556 | 0.546 | **0.551** |
| 5 | feature_perspective | Geometry | 0.531 | 0.539 | **0.535** |
| 6 | compression_inconsistency | Signal | 0.529 | 0.529 | 0.529 |
| 7 | teeth_boundary_drift | Mouth | 0.523 | 0.510 | 0.516 |
| 8 | skin_texture_repeat | Texture | 0.513 | 0.513 | 0.513 |
| 9 | feature_proportions | Symmetry | 0.510 | 0.515 | 0.512 |
| 10 | jawline_seams | Blending | 0.509 | 0.513 | 0.511 |

> 详细问题列表请见 [`config/mfa_questions.json`](config/mfa_questions.json)，完整统计位于 [`metadata/mfa_ffpp_val.json`](metadata/mfa_ffpp_val.json) 与 [`metadata/mfa_ffpp_test.json`](metadata/mfa_ffpp_test.json)。

## ⚙️ 环境与依赖
- Python 3.10（建议使用虚拟环境）
- GPU：8GB 显存以上（RTX 30 系列实测可运行 4bit 量化模型）
- 必备依赖：`torch`、`transformers`、`accelerate`、`bitsandbytes`、`opencv-python-headless`、`insightface`、`onnxruntime-gpu`
- 本地 HuggingFace 模型：`models/llava-1.5-7b-hf/`（请手动下载）

## 📁 数据准备
1. 下载 FaceForensics++ (c23) 并解压到 `data/ffpp_c23/`，保持原始 `original` / `Deepfakes` / `Face2Face` / `FaceSwap` / `NeuralTextures` 目录结构。
2. （可选）下载 Celeb-DF(v2) 到 `data/celeb_df_v2/` 用于跨库评估。
3. `data/processed/` 将由脚本自动生成抽帧与人脸裁剪缓存，已在 `.gitignore` 中忽略。

## 🚀 快速运行
```bash
# 1. 创建并激活虚拟环境
python -m venv deepfake_env
# Windows
deepfake_env\Scripts\activate
# Linux/macOS
source deepfake_env/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
pip install insightface onnxruntime-gpu

# 3. 构建元数据（生成 train/val/test 划分）
python code/mfa_metadata.py

# 4. 抽帧与人脸裁剪（分批执行，可断点续跑）
python code/extract_ffpp_frames.py --split train
python code/extract_ffpp_frames.py --split val
python code/extract_ffpp_frames.py --split test
# 如需 FaceShifter / DeepFakeDetection：
python code/extract_ffpp_frames.py --split extra --include-extra

# 5. 运行 MFA（默认写入 metadata/mfa_ffpp_<split>_progress.jsonl）
python code/run_mfa_ffpp.py --split val --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
python code/run_mfa_ffpp.py --split test --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20

# 6. 查看结果
type metadata\mfa_feature_rankings.json
```

> 脚本支持断点续跑：终止后再次执行相同命令，会读取 `metadata/mfa_ffpp_<split>_progress.jsonl` 自动跳过已处理视频。

## 📂 仓库结构概览
```
code/
  ├── extract_ffpp_frames.py   # InsightFace 抽帧与裁脸
  ├── run_mfa_ffpp.py          # LLaVA 批量推理 + 进度日志
  ├── llava_quant.py           # 4bit 量化加载与推理封装
  ├── mfa_metadata.py          # FF++ 数据划分工具
  └── ...                      # 其他辅助脚本
config/
  └── mfa_questions.json       # 候选伪造问题清单（中英双语）
metadata/
  ├── ffpp_c23_split.json/csv  # 划分清单
  ├── mfa_ffpp_val*.json[l]    # 验证集统计 + 进度日志
  ├── mfa_ffpp_test*.json[l]   # 测试集统计 + 进度日志
  └── mfa_feature_rankings.json# Top-K 特征汇总
scripts/
  └── download_llava_cpu.py    # HuggingFace 模型下载脚本
```

更多细节请参见：
- [`QUICK_START.md`](QUICK_START.md)：5 分钟上手流程
- [`本地运行指南`](��������ָ��.md)：完整环境部署（中文）
- [`项目总结报告`](��Ŀ�ܽᱨ��.md)：阶段性成果与下一步计划

## 📚 参考
- 原论文：*χ²-DFD: A Framework for Explainable and Extendable Deepfake Detection*
- LLaVA 官方仓库与 HuggingFace 权重

---
如需了解数据生成、更多脚本细节或贡献代码，请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)。
