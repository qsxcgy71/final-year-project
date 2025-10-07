# 📁 项目文件清单（2025-09）

> 仅列出核心目录与关键文件，原始数据与模型权重需自行下载，均已在 `.gitignore` 中忽略。

## 顶层结构
```
final-year-project/
├── code/                 # 抽帧、MFA、评测脚本
├── config/               # 问题配置
├── data/                 # 数据集及缓存（processed、splits 等）
├── eval/ffpp_c23/        # 指标面板
├── mfa/ffpp_c23/         # LLaVA 推理结果与排名
├── reports/              # 样例墙、可视化素材
├── models/               # LLaVA 本地权重（需手动下载）
└── roadmap.md            # 阶段任务与里程碑
```

## 关键文件
| 路径 | 说明 |
|------|------|
| `code/extract_ffpp_frames.py` | 调用 InsightFace 抽帧并裁剪 224×224 人脸 |
| `code/run_mfa_ffpp.py` | LLaVA 批量问答，写入进度日志（可断点续跑） |
| `code/eval_mfa_ffpp.py` | 汇总 AUC/F1/BA 等指标，并写入 `eval/ffpp_c23/metrics.json` |
| `code/generate_sample_cases.py` | 整理 TP/FP/TN/FN 样例，生成 `reports/sample_cases.json` |
| `config/mfa_questions.json` | MFA 候选问题列表（中英同文） |
| `data/splits/ffpp_c23_split.json` | FF++ train/val/test 划分详情 |
| `mfa/ffpp_c23/mfa_ffpp_val_progress.jsonl` | 验证集推理日志（每视频票数） |
| `mfa/ffpp_c23/mfa_feature_rankings.json` | Top-K 排名与 AUC/r_pb/CI |
| `eval/ffpp_c23/metrics.json` | 统一评测结果（分类 + MFA + 效率） |
| `reports/sample_cases.json` | 样例墙（TP/TN/FP/FN） |
| `roadmap.md` | 当前阶段任务（收尾/测量/验证/整理/留口） |

## 数据与模型（需手动获取）
- `data/ffpp_c23/`：FaceForensics++ c23 原始视频
- `data/celeb_df_v2/`：Celeb-DF v2（可选）
- `models/llava-1.5-7b-hf/`：LLaVA 权重

> 建议在运行脚本前核对 `git status`，确保大规模文件未被跟踪。
