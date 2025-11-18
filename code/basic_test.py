"""
STEP 6: 基础测试验证 (不依赖深度学习库)
χ²-DFD 深度伪造检测系统的基础功能测试
"""

import os
import json
import sys
from datetime import datetime

def test_file_structure():
    """测试文件结构完整性"""
    print("📁 测试文件结构...")
    
    required_files = [
        "code/main_detector.py",
        "code/deepfake_detector.py", 
        "code/image_utils.py",
        "code/llava_model.py",
        "README.md",
        "requirements.txt",
        "项目总结报告.md"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = os.path.join("/workspace", file_path)
        if os.path.exists(full_path):
            existing_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path}")
    
    score = (len(existing_files) / len(required_files)) * 100
    print(f"   📊 文件结构完整性: {score:.1f}% ({len(existing_files)}/{len(required_files)})")
    
    return score, existing_files, missing_files

def test_code_syntax():
    """测试代码语法正确性"""
    print("\n🔍 测试代码语法...")
    
    python_files = [
        "code/main_detector.py",
        "code/deepfake_detector.py",
        "code/image_utils.py", 
        "code/llava_model.py",
        "code/test_validation.py"
    ]
    
    syntax_results = {}
    
    for file_path in python_files:
        full_path = os.path.join("/workspace", file_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                # 尝试编译代码 (不执行)
                compile(code, full_path, 'exec')
                syntax_results[file_path] = True
                print(f"   ✅ {file_path} - 语法正确")
                
            except SyntaxError as e:
                syntax_results[file_path] = False
                print(f"   ❌ {file_path} - 语法错误: {e}")
            except Exception as e:
                syntax_results[file_path] = False
                print(f"   ⚠️  {file_path} - 检查失败: {e}")
        else:
            syntax_results[file_path] = False
            print(f"   ❌ {file_path} - 文件不存在")
    
    passed = sum(syntax_results.values())
    total = len(syntax_results)
    score = (passed / total) * 100 if total > 0 else 0
    
    print(f"   📊 代码语法正确性: {score:.1f}% ({passed}/{total})")
    return score

def test_documentation():
    """测试文档完整性"""
    print("\n📚 测试文档完整性...")
    
    doc_tests = {
        "README.md": False,
        "项目总结报告.md": False,
        "本地运行指南.md": False,
        "requirements.txt": False
    }
    
    for doc_file in doc_tests.keys():
        full_path = os.path.join("/workspace", doc_file)
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查文档是否有实质内容
                if len(content.strip()) > 100:
                    doc_tests[doc_file] = True
                    print(f"   ✅ {doc_file} - 内容完整")
                else:
                    print(f"   ⚠️  {doc_file} - 内容过少")
                    
            except Exception as e:
                print(f"   ❌ {doc_file} - 读取失败: {e}")
        else:
            print(f"   ❌ {doc_file} - 文件不存在")
    
    passed = sum(doc_tests.values())
    total = len(doc_tests)
    score = (passed / total) * 100 if total > 0 else 0
    
    print(f"   📊 文档完整性: {score:.1f}% ({passed}/{total})")
    return score

def test_data_files():
    """测试数据文件"""
    print("\n🖼️  测试数据文件...")
    
    test_image_dir = "/workspace/data/test_images"
    
    if not os.path.exists(test_image_dir):
        print(f"   ❌ 测试图像目录不存在: {test_image_dir}")
        return 0
    
    image_files = []
    for file in os.listdir(test_image_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(file)
            print(f"   ✅ 发现测试图像: {file}")
    
    if len(image_files) >= 3:
        score = 100
        print(f"   📊 测试数据: {score:.1f}% (发现 {len(image_files)} 个图像文件)")
    elif len(image_files) >= 1:
        score = 70
        print(f"   📊 测试数据: {score:.1f}% (发现 {len(image_files)} 个图像文件，建议至少3个)")
    else:
        score = 0
        print(f"   📊 测试数据: {score:.1f}% (未发现图像文件)")
    
    return score

def test_import_structure():
    """测试模块导入结构"""
    print("\n📦 测试模块导入结构...")
    
    # 添加code目录到Python路径
    code_path = "/workspace/code"
    if code_path not in sys.path:
        sys.path.insert(0, code_path)
    
    import_tests = {
        "image_utils": False,
        "main_detector": False
    }
    
    # 测试基础模块导入（不依赖深度学习库）
    try:
        # 只测试基础函数
        exec("from image_utils import get_test_images")
        import_tests["image_utils"] = True
        print("   ✅ image_utils 基础功能导入成功")
    except Exception as e:
        print(f"   ❌ image_utils 导入失败: {e}")
    
    try:
        # 测试主检测器的基础部分
        exec("import main_detector")
        import_tests["main_detector"] = True
        print("   ✅ main_detector 模块导入成功")
    except Exception as e:
        print(f"   ❌ main_detector 导入失败: {e}")
    
    passed = sum(import_tests.values())
    total = len(import_tests)
    score = (passed / total) * 100 if total > 0 else 0
    
    print(f"   📊 模块导入结构: {score:.1f}% ({passed}/{total})")
    return score

def generate_test_report(scores):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("📋 χ²-DFD系统基础测试报告")
    print("=" * 60)
    
    overall_score = sum(scores.values()) / len(scores) if scores else 0
    
    report = {
        "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "测试类型": "基础功能测试",
        "测试项目": {
            key: f"{value:.1f}%" for key, value in scores.items()
        },
        "综合得分": f"{overall_score:.1f}%",
        "测试说明": "这是不依赖深度学习库的基础测试，完整功能测试需要安装所有依赖包"
    }
    
    print(f"\n🎯 综合得分: {overall_score:.1f}%")
    for test_name, score in scores.items():
        print(f"   {test_name}: {score:.1f}%")
    
    # 保存报告
    report_path = "/workspace/基础测试报告.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试报告已保存到: 基础测试报告.json")
    
    # 评估等级
    if overall_score >= 90:
        grade = "优秀 🏆"
        message = "项目结构完整，可以进行完整功能测试"
    elif overall_score >= 80:
        grade = "良好 👍"
        message = "项目基本完整，建议检查缺失项目"
    elif overall_score >= 70:
        grade = "合格 ✅"
        message = "项目基础功能可用，需要完善部分内容"
    else:
        grade = "需要改进 ⚠️"
        message = "项目存在问题，需要修复后再进行测试"
    
    print(f"\n🏅 基础测试评估: {grade}")
    print(f"💡 建议: {message}")
    
    return overall_score

def main():
    """主测试函数"""
    print("🚀 启动χ²-DFD深度伪造检测系统基础测试")
    print("   注意: 这是基础结构测试，完整功能测试需要安装依赖包")
    print("=" * 60)
    
    scores = {}
    
    try:
        # 执行各项测试
        scores["文件结构完整性"], _, _ = test_file_structure()
        scores["代码语法正确性"] = test_code_syntax()
        scores["文档完整性"] = test_documentation()
        scores["测试数据完备性"] = test_data_files()
        scores["模块导入结构"] = test_import_structure()
        
        # 生成报告
        overall_score = generate_test_report(scores)
        
        print(f"\n✨ 基础测试完成！系统基础得分: {overall_score:.1f}%")
        
        if overall_score >= 80:
            print("🎉 项目基础结构良好，可以进行依赖安装和完整测试！")
            print("📋 下一步:")
            print("   1. pip install -r requirements.txt")
            print("   2. python code/test_validation.py  # 完整功能测试")
            print("   3. python code/main_detector.py   # 运行检测系统")
        else:
            print("⚠️  项目基础结构需要完善，请检查缺失的文件和问题。")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
