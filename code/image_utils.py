"""
图像处理工具模块
用于 χ²-DFD 深度伪造检测系统
"""

import os
from PIL import Image
import torch
from torchvision import transforms
import cv2
import numpy as np

class ImageProcessor:
    """图像处理器"""
    
    def __init__(self, image_size=224):
        self.image_size = image_size
        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def load_image(self, image_path):
        """加载图像"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return image
        except Exception as e:
            print(f"加载图像失败 {image_path}: {e}")
            return None
    
    def preprocess_image(self, image):
        """预处理图像用于模型输入"""
        if image is None:
            return None
        
        try:
            # 应用变换
            tensor = self.transform(image)
            # 添加批次维度
            return tensor.unsqueeze(0)
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return None
    
    def preprocess_image_from_path(self, image_path):
        """从路径加载并预处理图像"""
        image = self.load_image(image_path)
        return self.preprocess_image(image)
    
    def get_image_info(self, image_path):
        """获取图像基本信息"""
        try:
            image = self.load_image(image_path)
            if image is None:
                return None
            
            return {
                'path': image_path,
                'size': image.size,
                'mode': image.mode,
                'format': image.format
            }
        except Exception as e:
            print(f"获取图像信息失败 {image_path}: {e}")
            return None

def get_test_images():
    """获取测试图像列表"""
    test_dir = "/workspace/data/test_images"
    if not os.path.exists(test_dir):
        return []
    
    image_files = []
    for filename in os.listdir(test_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(os.path.join(test_dir, filename))
    
    return sorted(image_files)

def display_image_info(image_path):
    """显示图像信息"""
    processor = ImageProcessor()
    info = processor.get_image_info(image_path)
    
    if info:
        print(f"图像路径: {info['path']}")
        print(f"图像尺寸: {info['size']}")
        print(f"图像模式: {info['mode']}")
        print(f"图像格式: {info['format']}")
    else:
        print(f"无法获取图像信息: {image_path}")

if __name__ == "__main__":
    # 测试图像处理功能
    test_images = get_test_images()
    print(f"找到 {len(test_images)} 个测试图像:")
    
    for img_path in test_images:
        print(f"\n=== {os.path.basename(img_path)} ===")
        display_image_info(img_path)
