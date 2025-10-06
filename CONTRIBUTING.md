# Contributing Guide

感谢你对 χ²-DFD 深度伪造检测系统复现项目的关注！本仓库当前聚焦于 MFA 模块和大规模数据实验，欢迎通过 Issue / PR 反馈问题与改进建议。

## 🙋‍♀️ 提交 Issue
- 复现问题：请附带操作系统、Python 版本、GPU/驱动、`pip list` 核心依赖、错误日志。
- 新功能建议：描述目标、预期收益及可能的实现思路。
- 数据问题：如发现划分异常或统计错误，请注明对应文件（如 `metadata/mfa_ffpp_val_progress.jsonl` 的行号）。

## 🧩 Pull Request 流程
1. Fork 仓库并创建新分支。
2. 确保代码遵循现有风格：
   - Python 使用 `black`/`isort` 风格（4 spaces）。
   - 文档使用 Markdown，保持中英混排语句通顺。
3. 运行必要脚本：
   - 若修改了抽帧或 MFA 逻辑，请至少在 `--limit 10` 场景下验证。
4. 更新相关文档（如 README / 指南 / 变更日志）。
5. 提交 PR 时附：改动摘要、测试方式、影响范围。

## 📦 大文件与数据策略
- 请 **不要** 在 PR 中上传以下内容：
  - `data/ffpp_c23/`、`data/celeb_df_v2/`、`data/processed/`
  - `models/` 下的权重文件
  - 临时日志或超过 5MB 的二进制文件
- 如果需要共享示例，请提供可下载链接或将小规模样本加入 `data/sample/`（需提前讨论）。

## 🧪 本地验证清单
- `python code/mfa_metadata.py` — 验证划分脚本正常。
- `python code/extract_ffpp_frames.py --split val --limit 5` — 验证抽帧流程。
- `python code/run_mfa_ffpp.py --split val --limit 5 --progress-interval 1` — 验证 LLaVA 推理与进度日志。

## 🔐 访问权限
- 本地量化模型及数据需自行下载，仓库不会提供重量级文件。
- 若涉及凭证（如 HuggingFace Token），请放置在环境变量或 `.env` 文件，勿提交到 Git。

如有更多问题，欢迎在 Issue 中交流或与维护者联系。谢谢！
