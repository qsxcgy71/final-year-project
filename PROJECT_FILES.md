# 项目文件清单（2025-09）

> 仅列出核心目录与关键文件，实际数据集与模型权重需手动下载，均已在 `.gitignore` 中忽略。

## 顶层结构
```
final-year-project/
├── code/                     # 脚本与核心代码
├── config/                   # MFA 问题配置
├── metadata/                 # 划分与推理结果
├── scripts/                  # 工具脚本（模型下载等）
├── data/                     # 数据目录（需自行准备）
│   ├── ffpp_c23/             # FaceForensics++ c23 原始视频（未纳入 Git）
│   ├── celeb_df_v2/          # Celeb-DF v2（可选）
│   └── processed/            # 抽帧裁脸缓存（自动生成）
├── models/                   # 本地 HuggingFace 权重（未纳入 Git）
└── *.md / requirements.txt   # 文档与依赖
```

## 代码目录
| 文件 | 说明 |
|------|------|
| `code/extract_ffpp_frames.py` | 调用 InsightFace 抽帧并裁剪 224×224 人脸，支持覆盖与进度提示 |
| `code/run_mfa_ffpp.py` | 批量执行 LLaVA 问答并写入进度日志，可断点续跑 |
| `code/llava_quant.py` | LLaVA-1.5-7B 模型加载与 4bit 推理封装 |
| `code/mfa_metadata.py` | 构建 FF++ c23 的 train/val/test 分层划分 |
| `code/deepfake_detector.py` | 早期的简化版 χ²-DFD 演示逻辑（保留以对比） |
| `code/main_detector.py` | CLI 演示入口（基础版） |
| 其余脚本 | 单元测试、旧版演示代码 |

## 配置与元数据
| 路径 | 说明 |
|------|------|
| `config/mfa_questions.json` | MFA 候选问题清单（中英双语，20 条） |
| `metadata/ffpp_c23_split.json/csv` | 视频划分详情：video_id、label、method、split |
| `metadata/mfa_ffpp_val.json` | 验证集问题统计（Balanced Accuracy、TP/TN/FP/FN） |
| `metadata/mfa_ffpp_test.json` | 测试集问题统计 |
| `metadata/mfa_ffpp_<split>_progress.jsonl` | 逐视频问答记录，可用于断点恢复 |
| `metadata/mfa_feature_rankings.json` | Top-K 问题及平均 BA 汇总 |

## 文档
| 文件 | 更新内容 |
|------|----------|
| `README.md` | 最新进度概览、快速指引、Top-K 特征列表 |
| `QUICK_START.md` | 一站式流程：环境、数据、抽帧、MFA |
| `本地运行指南.md` | 详细部署操作（中文） |
| `项目总结报告.md` | 阶段成果、指标与下一步计划 |
| 其他 `.md` | 贡献指南、GitHub 推送说明等 |

## 数据与模型（需手动获取）
- `data/ffpp_c23/`：FaceForensics++ c23 原始视频
- `data/celeb_df_v2/`：Celeb-DF v2（可选）
- `models/llava-1.5-7b-hf/`：LLaVA 模型权重

这些目录尺寸较大，未提交至 Git，请根据文档自行下载并放置到位。
