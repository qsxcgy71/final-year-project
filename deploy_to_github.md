# 部署到 GitHub / Remote Backup 指南

> 目标：在不泄露大文件和敏感数据的前提下，将项目最新进度推送到远程仓库（如 GitHub）。

## 1. 推送前检查
1. 确认 `.gitignore` 已包含以下目录：
   - `data/ffpp_c23/`
   - `data/celeb_df_v2/`
   - `data/processed/`
   - `models/`
2. 运行 `git status`，确保上述目录未被跟踪。
3. 仅提交必要文件：脚本、配置、文档、`metadata/*.json`（可展示实验结果）。

## 2. 常用命令
```bash
# 查看状态
git status

# 将关键脚本与文档加入暂存区（示例）
git add code/*.py config/mfa_questions.json metadata/*.json README.md QUICK_START.md
git add CONTRIBUTING.md PROJECT_FILES.md ��������ָ��.md ��Ŀ�ܽᱨ��.md

# 提交
git commit -m "docs: update MFA pipeline and feature rankings"

# 推送到远程主分支
git push origin main
```

> 如仓库使用其他默认分支名称，请将 `main` 替换为实际分支。

## 3. 首次配置远程仓库
```bash
git remote add origin https://github.com/<username>/<repo>.git
git branch -M main
git push -u origin main
```

## 4. 建议做法
- 推送前备份 `metadata/` 目录，以防本地意外。
- 对于较大的日志（`*_progress.jsonl`），可按需保留或压缩后上传。
- 推送成功后，在 GitHub Releases 或 Wiki 中记录阶段性成果，便于对外展示。

## 5. 避免的问题
- 不要将 FF++ / Celeb-DF 等受限数据上传公网。
- 不要推送 HuggingFace 模型权重或需要授权的文件。
- 避免提交超过 GitHub 单文件 100MB 的内容。

如需自动化备份，可结合 GitHub Actions 或自建镜像仓库，但请确保所有敏感数据均已脱敏或忽略。
