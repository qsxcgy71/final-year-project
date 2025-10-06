# QUICK START

> 目标：在本地环境中完成 χ²-DFD 的 MFA 复现流程，包括数据划分、抽帧裁脸、LLaVA 推理与特征排序。

## 1. 准备环境
```bash
python -m venv deepfake_env
# Windows
deepfake_env\Scripts\activate
# Linux/macOS
source deepfake_env/bin/activate

pip install -r requirements.txt
pip install insightface onnxruntime-gpu
```

## 2. 准备数据
1. 下载 FaceForensics++ (c23) 并解压至 `data/ffpp_c23/`。
2. （可选）下载 Celeb-DF(v2) 至 `data/celeb_df_v2/`。
3. 下载 LLaVA-1.5-7B 模型权重到 `models/llava-1.5-7b-hf/`（可使用 `scripts/download_llava_cpu.py`）。

## 3. 生成元数据
```bash
python code/mfa_metadata.py
```
输出：`metadata/ffpp_c23_split.json`，包含 4000/500/500 的 train/val/test 划分。

## 4. 抽帧与裁脸
```bash
python code/extract_ffpp_frames.py --split train
python code/extract_ffpp_frames.py --split val
python code/extract_ffpp_frames.py --split test
# 额外伪造方法（FaceShifter / DeepFakeDetection）
python code/extract_ffpp_frames.py --split extra --include-extra
```
缓存存放于 `data/processed/ffpp_c23/faces_224/` 与 `raw_frames/`，脚本支持重复运行覆盖。

## 5. 运行 MFA（可断点续跑）
```bash
python code/run_mfa_ffpp.py --split val  --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
python code/run_mfa_ffpp.py --split test --model-dir models/llava-1.5-7b-hf --quant 4bit --progress-interval 20
```
- 进度日志：`metadata/mfa_ffpp_<split>_progress.jsonl`
- 中断后重复执行同一命令即可续跑。

## 6. 查看结果
```bash
# Top-K 特征
cat metadata/mfa_feature_rankings.json

# 完整问题统计
cat metadata/mfa_ffpp_val.json
cat metadata/mfa_ffpp_test.json
```

## 7. 常见问题
- **模型加载慢**：首次量化加载约 30~40 s，随后推理耗时较长（建议保持命令运行）。
- **InsightFace 未安装**：确保已安装 `insightface` + `onnxruntime-gpu`，并具备 Microsoft Visual C++ Build Tools。
- **数据未提交**：`data/ffpp_c23/`、`data/celeb_df_v2/`、`data/processed/` 均被 `.gitignore` 忽略，避免误传 Git 远程仓库。

完成以上步骤后，即可得到论文中 MFA 模块的复现结果，并据此继续后续的 MFC/MHR 研究。
