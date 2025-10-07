# QUICK START

> 目标：在本地环境中复现 χ²-DFD 的 MFA 流程，获得 FF++ c23 的抽帧缓存、LLaVA 推理日志与评测指标。

## 1. 环境准备
```bash
python -m venv deepfake_env
# Windows
deepfake_env\Scripts\activate
# Linux/macOS
source deepfake_env/bin/activate

pip install -r requirements.txt
pip install insightface onnxruntime-gpu
```

## 2. 数据与模型
1. 下载 FaceForensics++ (c23) 至 `data/ffpp_c23/`（保持原目录结构）。
2. （可选）下载 Celeb-DF v2 至 `data/celeb_df_v2/`。
3. 手动下载 `llava-hf/llava-1.5-7b-hf` 权重至 `models/llava-1.5-7b-hf/`，可执行 `python scripts/download_llava_cpu.py`。

## 3. 划分与抽帧
```bash
python code/mfa_metadata.py  # 生成 data/splits/ffpp_c23_split.{json,csv}
python code/extract_ffpp_frames.py --split train
python code/extract_ffpp_frames.py --split val
python code/extract_ffpp_frames.py --split test
# 扩展：FaceShifter / DeepFakeDetection
python code/extract_ffpp_frames.py --split extra --include-extra
```

## 4. LLaVA-MFA 推理
```bash
python code/run_mfa_ffpp.py --split val  --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
python code/run_mfa_ffpp.py --split test --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
```
- 进度日志写入 `mfa/ffpp_c23/mfa_ffpp_<split>_progress.jsonl`；中断后重复执行即可续跑。

## 5. 评测与样例
```bash
python code/eval_mfa_ffpp.py         # 输出 eval/ffpp_c23/metrics.json
python code/generate_sample_cases.py # 输出 reports/sample_cases.json
```
- Top-K 排名：`mfa/ffpp_c23/mfa_feature_rankings.json`
- 样例墙素材：`reports/sample_cases.json`

## 6. 常见问题
| 问题 | 排查建议 |
|------|----------|
| 安装 insightface 失败 | 安装 Visual Studio Build Tools (MSVC)，再执行 pip 安装 |
| LLaVA 加载慢 | 首次量化加载约 30–40 s，推理耗时长属正常，建议保持命令运行 |
| 运行内存不足 | 减小 `--frames-per-video` 或缩减问题集合 |
| 数据被误提交 | `data/ffpp_c23`、`data/processed`、`models` 已写入 `.gitignore`，推送前检查 `git status` |

## 7. 下一步
参考 [`roadmap.md`](roadmap.md) 获取最新任务（指标补齐、跨库验证、目录整理与迁移准备）。
