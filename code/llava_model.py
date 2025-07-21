"""
LLaVA 模型集成模块
用于 χ²-DFD 深度伪造检测系统
"""

import torch
from transformers import LlavaForConditionalGeneration, LlavaProcessor
from PIL import Image
import warnings
warnings.filterwarnings("ignore")

class LLaVADetector:
    """LLaVA 深度伪造检测器"""
    
    def __init__(self, model_name="llava-hf/llava-1.5-7b-hf"):
        """
        初始化 LLaVA 模型
        
        Args:
            model_name: HuggingFace 模型名称
        """
        self.model_name = model_name
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        
        try:
            print("正在加载 LLaVA 模型...")
            # 加载处理器和模型
            self.processor = LlavaProcessor.from_pretrained(model_name)
            self.model = LlavaForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True
            )
            self.model.to(self.device)
            print("LLaVA 模型加载完成！")
            
        except Exception as e:
            print(f"加载 LLaVA 模型失败: {e}")
            raise
    
    def analyze_image(self, image, question):
        """
        分析图像并回答问题
        
        Args:
            image: PIL 图像对象
            question: 问题文本
            
        Returns:
            str: 模型回答
        """
        try:
            # 构建提示
            prompt = f"USER: <image>\n{question}\nASSISTANT:"
            
            # 处理输入
            inputs = self.processor(prompt, image, return_tensors="pt").to(self.device)
            
            # 生成回答
            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            # 解码输出
            generated_text = self.processor.decode(output[0], skip_special_tokens=True)
            
            # 提取回答部分
            if "ASSISTANT:" in generated_text:
                answer = generated_text.split("ASSISTANT:")[-1].strip()
            else:
                answer = generated_text.strip()
            
            return answer
            
        except Exception as e:
            print(f"图像分析失败: {e}")
            return "分析失败"
    
    def detect_deepfake_basic(self, image):
        """
        基础深度伪造检测
        
        Args:
            image: PIL 图像对象或图像路径
            
        Returns:
            dict: 检测结果
        """
        if isinstance(image, str):
            from .image_utils import ImageProcessor
            processor = ImageProcessor()
            image = processor.load_image(image)
        
        if image is None:
            return {"error": "无法加载图像"}
        
        # 基础检测问题
        questions = [
            "这张图片是真实的人脸还是人工生成的？请给出是或否的回答。",
            "这张图片中的人脸有没有不自然的地方？",
            "这张图片的面部特征看起来真实吗？",
            "这张图片是否可能是深度伪造的？"
        ]
        
        results = {}
        for i, question in enumerate(questions):
            answer = self.analyze_image(image, question)
            results[f"question_{i+1}"] = {
                "question": question,
                "answer": answer
            }
        
        return results
    
    def assess_features(self, image, features):
        """
        评估图像的特定特征
        
        Args:
            image: PIL 图像对象
            features: 特征列表
            
        Returns:
            dict: 特征评估结果
        """
        if isinstance(image, str):
            from .image_utils import ImageProcessor
            processor = ImageProcessor()
            image = processor.load_image(image)
        
        if image is None:
            return {"error": "无法加载图像"}
        
        feature_results = {}
        
        for feature in features:
            question = f"这张图片中的{feature}看起来自然吗？请给出是或否的回答并简单说明原因。"
            answer = self.analyze_image(image, question)
            feature_results[feature] = {
                "question": question,
                "answer": answer
            }
        
        return feature_results

# 定义论文中提到的关键特征
DEEPFAKE_FEATURES = [
    "面部布局",
    "眼睛",
    "鼻子", 
    "嘴巴",
    "皮肤纹理",
    "光照阴影",
    "面部边界融合",
    "面部对称性",
    "牙齿",
    "头发"
]

def test_llava_model():
    """测试 LLaVA 模型功能"""
    try:
        from image_utils import get_test_images, ImageProcessor
        
        print("=== 测试 LLaVA 模型 ===")
        
        # 初始化模型
        detector = LLaVADetector()
        
        # 获取测试图像
        test_images = get_test_images()
        if not test_images:
            print("没有找到测试图像")
            return
        
        # 测试第一张图像
        test_image_path = test_images[0]
        print(f"\n测试图像: {test_image_path}")
        
        # 加载图像
        processor = ImageProcessor()
        image = processor.load_image(test_image_path)
        
        if image is None:
            print("无法加载测试图像")
            return
        
        # 基础检测
        print("\n=== 基础深度伪造检测 ===")
        results = detector.detect_deepfake_basic(image)
        
        for key, result in results.items():
            if "error" not in result:
                print(f"\n问题: {result['question']}")
                print(f"回答: {result['answer']}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llava_model()
