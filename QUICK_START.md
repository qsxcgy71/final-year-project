# χ²-DFD 快速开始指南

## 🚀 5分钟快速启动

### 1. 克隆项目
```bash
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行检测
```bash
# 检测所有测试图像
python code/main_detector.py

# 或检测指定图像
python code/main_detector.py path/to/your/image.jpg
```

## 📊 预期输出

```
🔍 χ²-DFD 深度伪造检测系统
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ χ²-DFD 深度伪造检测结果 ⚠️

📄 图像: fake_face_1.jpg
🎯 判断: 可能伪造
📊 伪造概率: 41.42%
🔍 置信度: 中

🔍 可疑特征:
  • 鼻子(分数: 0.45)
  • 面部对称性(分数: 0.42)
  • 面部布局(分数: 0.30)

✅ 正常特征:
  • 面部边界融合(分数: 0.87)
  • 眼睛(分数: 0.75)
  • 光照阴影(分数: 0.72)
```

## 🧪 运行测试

```bash
# 基础结构测试
python code/basic_test.py

# 完整功能测试  
python code/test_validation.py
```

## 🆘 常见问题

**Q: 安装依赖失败？**
A: 升级pip后重试：`pip install --upgrade pip`

**Q: 图像加载失败？**  
A: 确保图像路径正确，支持JPG/PNG格式

**Q: 内存不足？**
A: 使用较小图像测试，关闭其他程序

## 📚 详细文档

- `项目总结报告.md` - 完整技术文档
- `本地运行指南.md` - 详细安装说明
- `deploy_to_github.md` - GitHub部署指南

---
🎯 χ²-DFD: 可解释可扩展的深度伪造检测系统
