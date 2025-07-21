# χ²-DFD 项目 GitHub 部署指南

## 🚀 快速部署到GitHub

### 方法1: 使用GitHub Web界面（推荐）

1. **创建新仓库**
   - 访问 https://github.com 并登录
   - 点击右上角的 "+" → "New repository"
   - 仓库名称：`deepfake-detection-chi2-dfd`
   - 描述：`χ²-DFD: 可解释可扩展的深度伪造检测系统`
   - 设置为 Public（公开）
   - ✅ 勾选 "Add a README file"
   - 点击 "Create repository"

2. **上传项目文件**
   - 在新创建的仓库页面，点击 "uploading an existing file"
   - 选择并上传以下文件：

### 📁 需要上传的核心文件

```
📦 deepfake-detection-chi2-dfd/
├── code/                          # 核心代码目录
│   ├── main_detector.py          # 主用户界面
│   ├── deepfake_detector.py      # 核心检测系统
│   ├── image_utils.py            # 图像处理工具
│   ├── llava_model.py            # LLaVA模型接口
│   ├── test_validation.py        # 完整功能测试
│   └── basic_test.py             # 基础结构测试
├── data/                         # 数据目录
│   └── test_images/              # 测试图像
│       ├── fake_face_1.jpg
│       ├── real_face_1.jpg
│       └── real_face_2.jpg
├── README.md                     # 项目说明
├── requirements.txt              # 依赖包列表
├── .gitignore                    # Git忽略文件
├── 项目总结报告.md               # 技术报告
└── 本地运行指南.md               # 运行指南
```

### 方法2: 使用Git命令行

```bash
# 1. 克隆新仓库
git clone https://github.com/YOUR_USERNAME/deepfake-detection-chi2-dfd.git
cd deepfake-detection-chi2-dfd

# 2. 复制项目文件到仓库目录
# (将项目文件复制到克隆的目录中)

# 3. 添加文件到Git
git add .
git commit -m "初始提交: χ²-DFD深度伪造检测系统"
git push origin main
```

## 📋 项目部署检查清单

### ✅ 核心功能文件
- [ ] `code/main_detector.py` - 主用户界面
- [ ] `code/deepfake_detector.py` - 核心检测系统
- [ ] `code/image_utils.py` - 图像处理工具
- [ ] `code/llava_model.py` - 模型接口
- [ ] `code/test_validation.py` - 完整测试
- [ ] `code/basic_test.py` - 基础测试

### ✅ 文档文件
- [ ] `README.md` - 项目主要说明
- [ ] `requirements.txt` - 依赖包列表
- [ ] `项目总结报告.md` - 详细技术报告
- [ ] `本地运行指南.md` - 本地运行说明
- [ ] `.gitignore` - Git忽略规则

### ✅ 测试数据
- [ ] `data/test_images/fake_face_1.jpg`
- [ ] `data/test_images/real_face_1.jpg`
- [ ] `data/test_images/real_face_2.jpg`

## 🎯 部署后验证

部署完成后，用户可以通过以下方式验证：

### 1. 克隆仓库
```bash
git clone https://github.com/YOUR_USERNAME/deepfake-detection-chi2-dfd.git
cd deepfake-detection-chi2-dfd
```

### 2. 基础测试
```bash
python code/basic_test.py
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 完整测试
```bash
python code/test_validation.py
```

### 5. 运行检测
```bash
python code/main_detector.py
```

## 📞 技术支持

如果遇到问题，请：
1. 检查 `基础测试报告.json` 中的错误信息
2. 确认Python版本 ≥ 3.8
3. 验证所有依赖包正确安装
4. 查看项目文档了解详细信息

## 🏷️ 项目标签建议

为GitHub仓库添加以下标签：
- `deepfake-detection`
- `computer-vision`
- `pytorch`
- `explainable-ai`
- `image-analysis`
- `llava`
- `python`
- `research`

---

*更新时间: 2025-07-21*
*χ²-DFD 深度伪造检测系统*
