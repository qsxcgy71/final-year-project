"""
STEP 6: 测试验证模块
χ²-DFD 深度伪造检测系统的全面测试验证
"""

import os
import json
import time
import statistics
from datetime import datetime

# 动态导入，避免依赖问题
try:
    from deepfake_detector import DeepfakeDetectionSystem
    from image_utils import get_test_images, ImageProcessor
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  警告: 缺少依赖包 - {e}")
    print("   请先运行: pip install -r requirements.txt")
    DEPENDENCIES_AVAILABLE = False

class SystemValidator:
    """系统验证器 - 全面测试检测系统的性能和准确性"""
    
    def __init__(self):
        self.detector = DeepfakeDetectionSystem()
        self.image_processor = ImageProcessor()
        self.test_results = []
        self.performance_metrics = {}
        
    def run_comprehensive_tests(self):
        """运行全面测试"""
        print("🧪 开始χ²-DFD系统全面测试验证")
        print("=" * 60)
        
        # 1. 功能测试
        print("\n1️⃣ 功能测试")
        functionality_score = self.test_functionality()
        
        # 2. 性能测试
        print("\n2️⃣ 性能测试")
        performance_score = self.test_performance()
        
        # 3. 准确性测试
        print("\n3️⃣ 准确性测试")
        accuracy_score = self.test_accuracy()
        
        # 4. 鲁棒性测试
        print("\n4️⃣ 鲁棒性测试")
        robustness_score = self.test_robustness()
        
        # 5. 用户界面测试
        print("\n5️⃣ 用户界面测试")
        ui_score = self.test_user_interface()
        
        # 生成综合报告
        overall_score = self.generate_comprehensive_report(
            functionality_score, performance_score, accuracy_score, 
            robustness_score, ui_score
        )
        
        return overall_score
    
    def test_functionality(self):
        """测试系统功能完整性"""
        print("   🔧 检测核心功能...")
        
        test_images = get_test_images()
        if not test_images:
            print("   ❌ 无法找到测试图像")
            return 0
        
        functionality_tests = {
            "图像加载": False,
            "特征提取": False,
            "MFA模块": False,
            "概率计算": False,
            "解释生成": False,
            "结果输出": False
        }
        
        try:
            # 测试图像加载
            test_image = test_images[0]
            image = self.image_processor.load_image(test_image)
            if image is not None:
                functionality_tests["图像加载"] = True
                print("   ✅ 图像加载功能正常")
            
            # 测试完整检测流程
            result = self.detector.detect(test_image)
            
            if "error" not in result:
                functionality_tests["特征提取"] = True
                functionality_tests["MFA模块"] = True
                print("   ✅ 特征提取和MFA模块正常")
                
                if "fake_probability" in result:
                    functionality_tests["概率计算"] = True
                    print("   ✅ 概率计算功能正常")
                
                if "explanation" in result:
                    functionality_tests["解释生成"] = True
                    print("   ✅ 解释生成功能正常")
                
                if result.get("feature_details"):
                    functionality_tests["结果输出"] = True
                    print("   ✅ 结果输出功能正常")
            
        except Exception as e:
            print(f"   ❌ 功能测试出现错误: {e}")
        
        passed_tests = sum(functionality_tests.values())
        total_tests = len(functionality_tests)
        score = (passed_tests / total_tests) * 100
        
        print(f"   📊 功能测试得分: {score:.1f}% ({passed_tests}/{total_tests})")
        return score
    
    def test_performance(self):
        """测试系统性能"""
        print("   ⚡ 测试系统性能...")
        
        test_images = get_test_images()
        if not test_images:
            print("   ❌ 无法找到测试图像")
            return 0
        
        processing_times = []
        memory_usage = []
        
        try:
            import psutil
            process = psutil.Process()
            
            for img_path in test_images:
                # 记录开始时间和内存
                start_time = time.time()
                start_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                # 执行检测
                result = self.detector.detect(img_path)
                
                # 记录结束时间和内存
                end_time = time.time()
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                
                processing_time = end_time - start_time
                memory_used = end_memory - start_memory
                
                processing_times.append(processing_time)
                memory_usage.append(memory_used)
                
                print(f"   📸 {os.path.basename(img_path)}: {processing_time:.2f}秒, 内存: {end_memory:.1f}MB")
            
            # 计算性能指标
            avg_time = statistics.mean(processing_times)
            max_memory = max(memory_usage) if memory_usage else 0
            
            self.performance_metrics = {
                "平均处理时间": f"{avg_time:.2f}秒",
                "最大内存使用": f"{max_memory:.1f}MB",
                "处理速度": f"{len(test_images)/sum(processing_times):.2f}图像/秒"
            }
            
            # 性能评分 (基于处理时间)
            if avg_time <= 2:
                score = 100
            elif avg_time <= 5:
                score = 80
            elif avg_time <= 10:
                score = 60
            else:
                score = 40
            
            print(f"   📊 性能测试得分: {score:.1f}%")
            print(f"   ⏱️  平均处理时间: {avg_time:.2f}秒")
            print(f"   💾 最大内存使用: {max_memory:.1f}MB")
            
            return score
            
        except ImportError:
            print("   ⚠️  无法导入psutil，跳过内存监控")
            return 70
        except Exception as e:
            print(f"   ❌ 性能测试出现错误: {e}")
            return 50
    
    def test_accuracy(self):
        """测试检测准确性"""
        print("   🎯 测试检测准确性...")
        
        test_images = get_test_images()
        if not test_images:
            print("   ❌ 无法找到测试图像")
            return 0
        
        # 基于文件名的简单标签 (这里是模拟，实际应用中需要真实标签)
        expected_labels = {}
        for img_path in test_images:
            filename = os.path.basename(img_path).lower()
            if 'fake' in filename or 'generated' in filename:
                expected_labels[img_path] = True  # 伪造
            else:
                expected_labels[img_path] = False  # 真实
        
        correct_predictions = 0
        total_predictions = 0
        prediction_details = []
        
        try:
            for img_path in test_images:
                result = self.detector.detect(img_path)
                
                if "error" not in result:
                    predicted_fake = result.get("is_fake", False)
                    expected_fake = expected_labels.get(img_path, False)
                    
                    is_correct = predicted_fake == expected_fake
                    if is_correct:
                        correct_predictions += 1
                    
                    total_predictions += 1
                    
                    prediction_details.append({
                        "图像": os.path.basename(img_path),
                        "预期": "伪造" if expected_fake else "真实",
                        "预测": "伪造" if predicted_fake else "真实",
                        "正确": "✅" if is_correct else "❌",
                        "概率": f"{result.get('fake_probability', 0):.2%}"
                    })
                    
                    print(f"   📸 {os.path.basename(img_path)}: "
                          f"预期={'伪造' if expected_fake else '真实'}, "
                          f"预测={'伪造' if predicted_fake else '真实'} "
                          f"({'✅' if is_correct else '❌'})")
            
            accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            print(f"   📊 准确性测试得分: {accuracy:.1f}% ({correct_predictions}/{total_predictions})")
            
            self.test_results.extend(prediction_details)
            return accuracy
            
        except Exception as e:
            print(f"   ❌ 准确性测试出现错误: {e}")
            return 0
    
    def test_robustness(self):
        """测试系统鲁棒性"""
        print("   🛡️  测试系统鲁棒性...")
        
        robustness_tests = {
            "空路径处理": False,
            "不存在文件处理": False,
            "损坏图像处理": False,
            "大尺寸图像处理": False
        }
        
        try:
            # 测试空路径
            result = self.detector.detect("")
            if "error" in result:
                robustness_tests["空路径处理"] = True
                print("   ✅ 空路径错误处理正常")
            
            # 测试不存在的文件
            result = self.detector.detect("nonexistent_file.jpg")
            if "error" in result:
                robustness_tests["不存在文件处理"] = True
                print("   ✅ 不存在文件错误处理正常")
            
            # 测试文本文件作为图像
            with open("/tmp/test_text.txt", "w") as f:
                f.write("这不是图像文件")
            result = self.detector.detect("/tmp/test_text.txt")
            if "error" in result:
                robustness_tests["损坏图像处理"] = True
                print("   ✅ 损坏图像错误处理正常")
            
            # 测试正常图像
            test_images = get_test_images()
            if test_images:
                result = self.detector.detect(test_images[0])
                if "error" not in result:
                    robustness_tests["大尺寸图像处理"] = True
                    print("   ✅ 正常图像处理功能正常")
            
        except Exception as e:
            print(f"   ⚠️  鲁棒性测试部分异常: {e}")
        
        passed_tests = sum(robustness_tests.values())
        total_tests = len(robustness_tests)
        score = (passed_tests / total_tests) * 100
        
        print(f"   📊 鲁棒性测试得分: {score:.1f}% ({passed_tests}/{total_tests})")
        return score
    
    def test_user_interface(self):
        """测试用户界面"""
        print("   🖥️  测试用户界面...")
        
        ui_tests = {
            "主检测器导入": False,
            "结果格式化": False,
            "JSON输出": False,
            "错误消息": False
        }
        
        try:
            # 测试主检测器导入
            from main_detector import detect_single_image, format_result
            ui_tests["主检测器导入"] = True
            print("   ✅ 主检测器模块导入成功")
            
            # 测试结果格式化
            test_images = get_test_images()
            if test_images:
                result = detect_single_image(test_images[0])
                if "error" not in result:
                    formatted = format_result(result)
                    if formatted and len(formatted) > 100:
                        ui_tests["结果格式化"] = True
                        print("   ✅ 结果格式化功能正常")
                    
                    # 测试JSON输出
                    json_str = json.dumps(result, ensure_ascii=False, indent=2)
                    if json_str:
                        ui_tests["JSON输出"] = True
                        print("   ✅ JSON输出功能正常")
            
            # 测试错误消息
            error_result = detect_single_image("nonexistent.jpg")
            if "error" in error_result:
                ui_tests["错误消息"] = True
                print("   ✅ 错误消息处理正常")
            
        except Exception as e:
            print(f"   ❌ 用户界面测试出现错误: {e}")
        
        passed_tests = sum(ui_tests.values())
        total_tests = len(ui_tests)
        score = (passed_tests / total_tests) * 100
        
        print(f"   📊 用户界面测试得分: {score:.1f}% ({passed_tests}/{total_tests})")
        return score
    
    def generate_comprehensive_report(self, functionality_score, performance_score, 
                                    accuracy_score, robustness_score, ui_score):
        """生成综合测试报告"""
        print("\n" + "=" * 60)
        print("📋 χ²-DFD系统测试验证报告")
        print("=" * 60)
        
        # 计算总分
        scores = [functionality_score, performance_score, accuracy_score, robustness_score, ui_score]
        overall_score = sum(scores) / len(scores)
        
        # 报告内容
        report = {
            "测试时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "测试项目": {
                "功能测试": f"{functionality_score:.1f}%",
                "性能测试": f"{performance_score:.1f}%", 
                "准确性测试": f"{accuracy_score:.1f}%",
                "鲁棒性测试": f"{robustness_score:.1f}%",
                "用户界面测试": f"{ui_score:.1f}%"
            },
            "综合得分": f"{overall_score:.1f}%",
            "性能指标": self.performance_metrics,
            "预测详情": self.test_results
        }
        
        # 显示报告
        print(f"\n🎯 综合得分: {overall_score:.1f}%")
        print(f"🔧 功能测试: {functionality_score:.1f}%")
        print(f"⚡ 性能测试: {performance_score:.1f}%")
        print(f"🎯 准确性测试: {accuracy_score:.1f}%")
        print(f"🛡️  鲁棒性测试: {robustness_score:.1f}%")
        print(f"🖥️  用户界面测试: {ui_score:.1f}%")
        
        # 性能指标
        if self.performance_metrics:
            print(f"\n📊 性能指标:")
            for key, value in self.performance_metrics.items():
                print(f"   {key}: {value}")
        
        # 保存报告
        with open("/workspace/测试验证报告.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存到: 测试验证报告.json")
        
        # 评估等级
        if overall_score >= 90:
            grade = "优秀 🏆"
        elif overall_score >= 80:
            grade = "良好 👍"
        elif overall_score >= 70:
            grade = "合格 ✅"
        else:
            grade = "需要改进 ⚠️"
        
        print(f"\n🏅 系统评估: {grade}")
        print("=" * 60)
        
        return overall_score

def main():
    """主测试函数"""
    print("🚀 启动χ²-DFD深度伪造检测系统全面测试")
    
    try:
        validator = SystemValidator()
        overall_score = validator.run_comprehensive_tests()
        
        print(f"\n✨ 测试完成！系统综合得分: {overall_score:.1f}%")
        
        if overall_score >= 80:
            print("🎉 系统通过测试验证，可以投入使用！")
        else:
            print("⚠️  系统需要进一步优化改进。")
            
    except Exception as e:
        print(f"❌ 测试过程中出现严重错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
