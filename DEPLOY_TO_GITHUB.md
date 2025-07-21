# 🚀 GitHub部署完整指南

本指南将帮助您将 χ²-DFD 深度伪造检测系统部署到您的GitHub仓库。

## 📋 前置准备

1. **GitHub账户**: 确保您有GitHub账户
2. **Git工具**: 安装Git命令行工具
3. **项目文件**: 确保您有完整的项目文件

## 🎯 方法1: 使用GitHub Web界面（推荐新手）

### 步骤1: 创建仓库

1. 访问 [GitHub](https://github.com) 并登录
2. 点击右上角的 `+` → `New repository`
3. 填写仓库信息：
   - **Repository name**: `final-year-project`
   - **Description**: `χ²-DFD: 可解释可扩展的深度伪造检测系统`
   - **Visibility**: Public（推荐）
   - ✅ 勾选 `Add a README file`
4. 点击 `Create repository`

### 步骤2: 上传项目文件

1. 在新仓库页面，点击 `uploading an existing file`
2. 将以下文件夹和文件拖拽上传：

```
📁 需要上传的文件结构：
├── code/                    # 整个文件夹
├── data/                    # 整个文件夹
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── QUICK_START.md
├── README.md
├── install_and_test.sh
├── install_and_test.bat
├── requirements.txt
├── 本地运行指南.md
└── 项目总结报告.md
```

3. 在提交信息中输入: `初始提交: χ²-DFD深度伪造检测系统`
4. 点击 `Commit changes`

### 步骤3: 更新仓库链接

需要编辑以下文件，将 `qsxcgy71` 替换为您的GitHub用户名：

- `README.md`
- `QUICK_START.md` 
- `本地运行指南.md`
- `CONTRIBUTING.md`

## 🔧 方法2: 使用Git命令行（推荐开发者）

### 步骤1: 初始化本地仓库

```bash
# 进入项目目录
cd /path/to/final-year-project

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 首次提交
git commit -m "初始提交: χ²-DFD深度伪造检测系统"
```

### 步骤2: 创建GitHub仓库

1. 在GitHub上创建空仓库（不要初始化README）
2. 复制仓库地址

### 步骤3: 推送到GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/qsxcgy71/final-year-project.git

# 推送代码
git branch -M main
git push -u origin main
```

## 🛠️ 方法3: 使用自动化脚本

我们提供了自动化脚本来简化部署：

```bash
# 运行自动部署脚本
python create_github_repo.py
```

该脚本将：
- 创建GitHub仓库
- 自动上传所有文件
- 更新文档中的链接

## ✅ 部署验证

部署完成后，验证以下内容：

### 文件结构检查
```
✅ code/ 目录存在且包含7个Python文件
✅ data/test_images/ 包含3张测试图像
✅ README.md 显示正确且格式良好
✅ requirements.txt 包含所有依赖
✅ 安装脚本可执行
```

### 功能测试
让其他用户尝试：

```bash
# 克隆仓库
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project

# 运行安装脚本
bash install_and_test.sh  # Linux/macOS
# 或
install_and_test.bat      # Windows
```

## 📝 仓库配置

### 添加标签（Tags）

在仓库设置中添加以下标签：
```
deepfake-detection, computer-vision, pytorch, explainable-ai, 
image-analysis, llava, python, research, chi2-dfd
```

### 设置Branch保护

对于main分支启用：
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Restrict pushes to matching branches

### 创建Release

1. 点击 `Releases` → `Create a new release`
2. 标签版本: `v1.0.0`
3. 发布标题: `χ²-DFD v1.0.0 - 初始发布`
4. 描述发布内容和功能

## 📚 文档维护

定期更新以下文档：
- README.md - 保持功能说明最新
- CHANGELOG.md - 记录版本变更
- CONTRIBUTING.md - 更新贡献指南

## 🔗 用户使用流程

部署完成后，用户可以通过以下方式使用：

### 一键安装使用
```bash
# 1. 克隆项目
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project

# 2. 一键安装和测试
bash install_and_test.sh
```

### 手动安装使用
```bash
# 1. 克隆项目
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行检测
python code/main_detector.py
```

## ❓ 常见问题

### Q: 上传文件时提示文件过大
A: GitHub有100MB的单文件限制。如果测试图像过大，可以：
- 压缩图像文件
- 使用Git LFS
- 提供下载链接

### Q: 用户反馈安装失败
A: 检查：
- requirements.txt 是否包含所有依赖
- Python版本兼容性
- 安装脚本权限问题

### Q: 如何更新项目
A: 推荐使用：
```bash
git add .
git commit -m "更新: 描述具体更改"
git push origin main
```

## 🎉 部署完成

恭喜！您已成功将 χ²-DFD 系统部署到GitHub。

**接下来可以：**
- 分享项目链接
- 邀请用户测试
- 收集反馈意见
- 持续改进项目

---

📞 **需要帮助？**
- 查看 [GitHub文档](https://docs.github.com)
- 创建Issue寻求帮助
- 参考项目文档

*部署指南 - 2025年7月21日*
