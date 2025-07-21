# 贡献指南 / Contributing Guide

感谢您对 χ²-DFD 深度伪造检测系统的关注！我们欢迎所有形式的贡献。

## 🤝 如何贡献

### 报告问题 / Reporting Issues

如果您发现了bug或有功能建议，请：

1. 检查是否已有相似的issue
2. 创建新的issue，包含：
   - 清晰的标题和描述
   - 复现步骤（如果是bug）
   - 期望的行为
   - 实际发生的行为
   - 系统环境信息

### 提交代码 / Submitting Code

1. **Fork 项目**
   ```bash
   git clone https://github.com/qsxcgy71/final-year-project.git
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b bugfix/your-bugfix-name
   ```

3. **编写代码**
   - 遵循现有的代码风格
   - 添加必要的注释
   - 更新相关文档

4. **测试**
   ```bash
   python code/basic_test.py
   python code/test_validation.py
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复bug描述"
   ```

6. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建Pull Request**
   - 填写清晰的PR描述
   - 链接相关的issue
   - 确保所有检查通过

## 📝 代码规范

### Python代码风格

- 使用4个空格缩进
- 行长度不超过88字符
- 遵循PEP 8规范
- 使用有意义的变量名和函数名

### 注释规范

```python
def detect_deepfake(image_path):
    """
    检测图像是否为深度伪造
    
    Args:
        image_path (str): 图像文件路径
        
    Returns:
        dict: 包含检测结果的字典
    """
    pass
```

### 提交信息格式

使用conventional commits格式：

- `feat: 添加新功能`
- `fix: 修复bug`
- `docs: 更新文档`
- `style: 代码格式调整`
- `refactor: 重构代码`
- `test: 添加测试`
- `chore: 维护性任务`

## 🧪 测试

在提交PR前，请确保：

1. **基础测试通过**
   ```bash
   python code/basic_test.py
   ```

2. **功能测试通过**
   ```bash
   python code/test_validation.py
   ```

3. **代码检测工具**
   ```bash
   # 安装检测工具
   pip install flake8 black

   # 代码格式化
   black code/

   # 代码检查
   flake8 code/
   ```

## 📚 文档贡献

文档同样重要！您可以：

- 改进现有文档的清晰度
- 添加使用示例
- 翻译文档到其他语言
- 修复文档中的错误

## 🎯 贡献领域

我们特别欢迎以下方面的贡献：

### 核心功能
- 模型性能优化
- 新的特征检测算法
- 更好的解释性方法
- 支持更多图像格式

### 用户体验
- GUI界面开发
- Web界面实现
- 移动端适配
- 性能监控

### 测试和质量
- 增加测试覆盖率
- 性能基准测试
- 持续集成配置
- 代码质量工具

### 文档和示例
- API文档完善
- 使用教程
- 最佳实践指南
- 视频教程

## 🏆 贡献者认可

所有贡献者都会在项目中得到认可：

- README.md中的贡献者列表
- 发布说明中的致谢
- 特殊徽章和荣誉

## 📞 联系方式

如果您有任何问题：

- 创建GitHub Issue
- 参与GitHub Discussions
- 发送邮件（如果有公开邮箱）

## 📋 开发环境设置

```bash
# 1. 克隆项目
git clone https://github.com/qsxcgy71/final-year-project.git
cd final-year-project

# 2. 创建开发环境
python -m venv dev_env
source dev_env/bin/activate  # Linux/macOS
# 或 dev_env\Scripts\activate  # Windows

# 3. 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有开发依赖

# 4. 安装pre-commit钩子
pip install pre-commit
pre-commit install

# 5. 运行测试确保环境正常
python code/basic_test.py
```

## 🚫 不接受的贡献

请避免：

- 恶意代码或后门
- 侵犯版权的内容
- 不相关的功能
- 破坏性的重构（没有充分讨论）
- 违反开源协议的代码

## 🎉 感谢

感谢每一位贡献者让这个项目变得更好！

---

*此贡献指南会根据项目发展持续更新*
