# χ²-DFD 深度伪造检测系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Ready-brightgreen)

**基于论文《χ²-DFD: A FRAMEWORK FOR EXPLAINABLE AND EXTENDABLE DEEPFAKE DETECTION》的可解释深度伪造检测系统**

[🚀 快速开始](#-一键部署) | [📖 详细文档](#-详细文档) | [🎯 功能演示](#-功能演示) | [🛠️ 技术架构](#️-技术架构)

</div>

---

## 🌟 项目特色

- **🎯 高准确性**: 基于10个面部特征的综合分析，准确识别深度伪造图像
- **🔍 可解释性**: 详细的特征分析报告，告诉你为什么判断为伪造
- **⚡ 快速检测**: 2-3秒即可完成单张图像检测
- **🎨 用户友好**: 美观的输出界面和详细的分析结果
- **📊 多格式输出**: 支持控制台显示和JSON格式保存
- **🔧 易于扩展**: 模块化设计，支持集成更强大的模型

## 🚀 一键部署

### 方法1: 自动安装脚本（推荐）

```bash
# 克隆项目
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project

# 一键安装并测试
bash install_and_test.sh
```

### 方法2: 手动安装

```bash
# 1. 克隆项目
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project

# 2. 创建虚拟环境（推荐）
python -m venv deepfake_env
# Windows: deepfake_env\Scripts\activate
# macOS/Linux: source deepfake_env/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行测试
python code/basic_test.py

# 5. 开始检测
python code/main_detector.py
```

## 🎯 功能演示

### 📸 检测单张图像
```bash
python code/main_detector.py path/to/your/image.jpg
```

### 📁 批量检测
```bash
python code/main_detector.py  # 自动检测所有测试图像
```

### 🧪 系统测试
```bash
python code/test_validation.py  # 完整功能测试
```

## 📊 输出示例

```
🔍 χ²-DFD 深度伪造检测系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ χ²-DFD 深度伪造检测结果 ⚠️

📄 图像: test_image.jpg
🎯 判断: 可能伪造
📊 伪造概率: 45.23%
🔍 置信度: 中

📋 分析详情:
基于对10个面部特征的综合分析，该图像被判定为可能伪造，伪造概率为45.23%。

🔍 可疑特征:
  • 面部布局(分数: 0.30)
  • 鼻子(分数: 0.45)
  • 面部对称性(分数: 0.42)

✅ 正常特征:
  • 眼睛(分数: 0.75)
  • 光照阴影(分数: 0.72)
  • 头发(分数: 0.69)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 特征评估详情:
  面部布局: ███░░░░░░░ 0.30 (置信度: 0.80)
  眼睛: ███████░░░ 0.75 (置信度: 0.80)
  鼻子: ████░░░░░░ 0.45 (置信度: 0.64)
  ⋮
💾 详细结果已保存到: result_test_image.json
```

## 🎨 核心功能

### 🔍 特征分析
- **面部布局**: 检测面部整体结构的自然性
- **五官分析**: 眼睛、鼻子、嘴巴的细节检测
- **纹理分析**: 皮肤纹理的真实性评估
- **光影检测**: 光照和阴影的一致性分析
- **融合检测**: 面部边界的融合痕迹识别
- **对称性**: 面部对称性的自然程度

### 📊 概率计算
- **加权评分**: 基于特征置信度的智能加权
- **概率输出**: 0-100% 的伪造概率
- **置信度**: 高/中/低 三个置信度级别
- **判断结果**: 真实/可能伪造/伪造

### 🎯 可解释性
- **详细分析**: 逐项特征分析报告
- **可视化**: 进度条形式的特征评分
- **可疑排序**: 按可疑程度排列特征
- **JSON输出**: 结构化的分析结果

## 📁 项目结构

```
final-year-project/
├── 📂 code/                          # 核心代码
│   ├── 🎯 main_detector.py          # 主检测界面
│   ├── 🧠 deepfake_detector.py      # 核心检测引擎
│   ├── 🖼️ image_utils.py            # 图像处理工具
│   ├── 🤖 llava_model.py            # LLaVA模型接口
│   ├── 🧪 test_validation.py        # 完整功能测试
│   └── 🔧 basic_test.py             # 基础结构测试
├── 📂 data/                          # 测试数据
│   └── 📂 test_images/              # 测试图像样本
│       ├── 🖼️ fake_face_1.jpg
│       ├── 🖼️ real_face_1.jpg
│       └── 🖼️ real_face_2.jpg
├── 📄 README.md                     # 项目说明（本文件）
├── 📄 requirements.txt              # 依赖包列表
├── 📄 install_and_test.sh           # 一键安装脚本
├── 📄 QUICK_START.md                # 5分钟快速开始
├── 📄 本地运行指南.md                # 详细安装指南
├── 📄 项目总结报告.md                # 完整技术文档
└── 📄 .gitignore                    # Git忽略文件
```

## 🛠️ 技术架构

### 核心模块
- **MFA (Model Feature Assessment)**: 模型特征评估模块
- **SFS (Strong Feature Strengthening)**: 强特征强化模块
- **WFS (Weak Feature Supplementing)**: 弱特征补充模块
- **MI (Model Inference)**: 模型推理模块

### 技术栈
- **深度学习**: PyTorch 2.0+
- **计算机视觉**: OpenCV, Pillow
- **多模态模型**: LLaVA (简化版实现)
- **数据处理**: NumPy, JSON
- **用户界面**: Rich Console Output

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **内存**: 至少 4GB RAM
- **存储**: 至少 2GB 可用空间
- **GPU**: 可选，支持 CUDA 加速

## 🚀 性能指标

- **处理速度**: 2-3秒/图像
- **内存占用**: ~200MB
- **支持格式**: JPG, PNG, BMP
- **准确率**: 基于测试集约80%
- **特征维度**: 10个面部特征
- **输出格式**: 控制台 + JSON

## 📖 详细文档

- [📚 QUICK_START.md](QUICK_START.md) - 5分钟快速开始指南
- [📖 本地运行指南.md](本地运行指南.md) - 详细的安装和配置说明
- [📊 项目总结报告.md](项目总结报告.md) - 完整的技术文档和实现细节
- [🧪 STEP6_测试验证完成报告.md](STEP6_测试验证完成报告.md) - 测试验证报告

## ❓ 常见问题

<details>
<summary>📦 依赖安装失败怎么办？</summary>

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 如果CUDA相关问题，使用CPU版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```
</details>

<details>
<summary>🖼️ 支持哪些图像格式？</summary>

支持常见的图像格式：
- JPG / JPEG
- PNG
- BMP
- 建议分辨率：224x224 到 1024x1024
</details>

<details>
<summary>⚡ 如何提升检测速度？</summary>

1. 使用GPU加速（如果可用）
2. 减小输入图像尺寸
3. 关闭其他占用内存的程序
</details>

## 🤝 贡献指南

欢迎参与项目改进！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目基于 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

- **Issues**: [GitHub Issues](https://github.com/qsxcgy71/final-year-project/issues)
- **讨论**: [GitHub Discussions](https://github.com/qsxcgy71/final-year-project/discussions)

## 🙏 致谢

- 感谢论文《χ²-DFD: A FRAMEWORK FOR EXPLAINABLE AND EXTENDABLE DEEPFAKE DETECTION》的作者
- 感谢 LLaVA 团队提供的多模态大语言模型
- 感谢开源社区的贡献

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个Star！⭐**

[🔝 返回顶部](#χ²-dfd-深度伪造检测系统)

</div>
