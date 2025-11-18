"""
χ²-DFD 深度伪造检测系统 - 主接口
基于论文《χ²-DFD: A FRAMEWORK FOR EXPLAINABLE AND EXTENDABLE DEEPFAKE DETECTION》

使用方法:
python main_detector.py <image_path>
"""

import sys
import os
import json
from deepfake_detector import DeepfakeDetectionSystem

def detect_single_image(image_path):
    """检测单个图像"""
    if not os.path.exists(image_path):
        return {"error": f"图像文件不存在: {image_path}"}
    
    # 初始化检测系统
    detector = DeepfakeDetectionSystem()
    
    # 进行检测
    result = detector.detect(image_path)
    
    return result

def format_result(result):
    """格式化结果输出"""
    if "error" in result:
        return f"❌ 错误: {result['error']}"
    
    explanation = result['explanation']
    
    # 判断结果的emoji
    if result['fake_probability'] > 0.6:
        emoji = "🚨"
    elif result['fake_probability'] > 0.4:
        emoji = "⚠️"
    else:
        emoji = "✅"
    
    output = f"""
{emoji} χ²-DFD 深度伪造检测结果 {emoji}

📄 图像: {os.path.basename(result['image_path'])}
🎯 判断: {explanation['判断']}
📊 伪造概率: {explanation['伪造概率']}
🔍 置信度: {explanation['置信度级别']}

📋 分析详情:
{explanation['详细分析']}

🔍 可疑特征:
{chr(10).join('  • ' + feature for feature in explanation['可疑特征']) if explanation['可疑特征'] else '  • 无明显可疑特征'}

✅ 正常特征:
{chr(10).join('  • ' + feature for feature in explanation['正常特征']) if explanation['正常特征'] else '  • 无明显正常特征'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 特征评估详情:
"""
    
    # 添加特征详情
    for feature, details in result['feature_details'].items():
        score_bar = "█" * int(details['score'] * 10) + "░" * (10 - int(details['score'] * 10))
        output += f"  {feature}: {score_bar} {details['score']:.2f} (置信度: {details['confidence']:.2f})\n"
    
    return output

def save_result_json(result, output_path):
    """保存结果为JSON文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存结果失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 χ²-DFD 深度伪造检测系统")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python main_detector.py <image_path>")
        print("\n可用的测试图像:")
        from image_utils import get_test_images
        test_images = get_test_images()
        for i, img_path in enumerate(test_images, 1):
            print(f"  {i}. {os.path.basename(img_path)}")
        
        # 如果没有提供参数，检测所有测试图像
        if test_images:
            print(f"\n🚀 自动检测所有测试图像...")
            detector = DeepfakeDetectionSystem()
            
            for img_path in test_images:
                print(f"\n{'='*60}")
                result = detector.detect(img_path)
                print(format_result(result))
                
                # 保存结果
                output_file = f"results_{os.path.splitext(os.path.basename(img_path))[0]}.json"
                save_result_json(result, output_file)
                print(f"💾 结果已保存到: {output_file}")
        
        return
    
    image_path = sys.argv[1]
    
    print(f"📸 正在分析图像: {image_path}")
    print("⏳ 请稍候...")
    
    # 检测图像
    result = detect_single_image(image_path)
    
    # 显示结果
    print(format_result(result))
    
    # 保存结果
    if "error" not in result:
        output_file = f"result_{os.path.splitext(os.path.basename(image_path))[0]}.json"
        if save_result_json(result, output_file):
            print(f"💾 详细结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
