"""
测试 LLaVA 模型集成
"""

import sys
import os
sys.path.append('/workspace/code')

from llava_model import LLaVADetector
from image_utils import get_test_images, ImageProcessor

def main():
    """主测试函数"""
    try:
        print("=== 开始测试 LLaVA 模型集成 ===")
        
        # 获取测试图像
        test_images = get_test_images()
        print(f"找到 {len(test_images)} 个测试图像")
        
        if not test_images:
            print("没有找到测试图像，退出测试")
            return
        
        # 初始化图像处理器
        processor = ImageProcessor()
        
        # 初始化 LLaVA 检测器
        print("\n正在初始化 LLaVA 检测器...")
        detector = LLaVADetector()
        
        # 测试第一张图像
        test_image_path = test_images[0]
        print(f"\n测试图像: {os.path.basename(test_image_path)}")
        
        # 加载图像
        image = processor.load_image(test_image_path)
        if image is None:
            print("无法加载测试图像")
            return
        
        # 进行基础检测
        print("\n=== 进行深度伪造检测 ===")
        results = detector.detect_deepfake_basic(image)
        
        # 显示结果
        for key, result in results.items():
            if "error" not in result:
                print(f"\n问题 {key}: {result['question']}")
                print(f"回答: {result['answer']}")
            else:
                print(f"错误: {result['error']}")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
