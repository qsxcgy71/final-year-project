"""
LLaVA 模型集成模块
用于 χ²-DFD 深度伪造检测系统
"""

from __future__ import annotations

from typing import Dict, List

import torch
from transformers import LlavaForConditionalGeneration, LlavaProcessor
from PIL import Image
import warnings

warnings.filterwarnings("ignore")


class LLaVADetector:
    """LLaVA 深度伪造检测器"""

    def __init__(self, model_path: str = "llava-hf/llava-1.5-7b-hf") -> None:
        """初始化 LLaVA 模型

        Args:
            model_path: HuggingFace 模型名称或本地模型路径
        """
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")

        try:
            print("正在加载 LLaVA 模型...")
            self.processor = LlavaProcessor.from_pretrained(model_path)
            self.model = LlavaForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                low_cpu_mem_usage=True,
            )
            self.model.to(self.device)
            print("LLaVA 模型加载完成")
        except Exception as err:  # pragma: no cover
            print(f"加载 LLaVA 模型失败: {err}")
            raise

    def analyze_image(self, image: Image.Image, question: str) -> str:
        """分析图像并回答问题"""
        try:
            prompt = f"USER: <image>\n{question}\nASSISTANT:"
            inputs = self.processor(text=prompt, images=image, return_tensors="pt")
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                )

            generated_text = self.processor.decode(output[0], skip_special_tokens=True)
            if "ASSISTANT:" in generated_text:
                return generated_text.split("ASSISTANT:")[-1].strip()
            return generated_text.strip()
        except Exception as err:
            print(f"图像分析失败: {err}")
            return "分析失败"

    def detect_deepfake_basic(self, image: Image.Image | str) -> Dict[str, Dict[str, str]]:
        """执行基础深度伪造检测"""
        if isinstance(image, str):
            from .image_utils import ImageProcessor

            processor = ImageProcessor()
            image = processor.load_image(image)

        if image is None:
            return {"error": "无法加载图像"}  # type: ignore[return-value]

        questions = [
            "这张图片是真实的人脸还是人工生成的？请给出是或否的回答",
            "这张图片中的人脸有没有不自然的地方？",
            "这张图片的面部特征看起来真实吗？",
            "这张图片是否可能是深度伪造的？",
        ]

        results: Dict[str, Dict[str, str]] = {}
        for idx, question in enumerate(questions, 1):
            answer = self.analyze_image(image, question)
            results[f"question_{idx}"] = {"question": question, "answer": answer}
        return results

    def assess_features(self, image: Image.Image | str, features: List[str]) -> Dict[str, Dict[str, str]]:
        """评估图像的特定特征"""
        if isinstance(image, str):
            from .image_utils import ImageProcessor

            processor = ImageProcessor()
            image = processor.load_image(image)

        if image is None:
            return {"error": "无法加载图像"}  # type: ignore[return-value]

        feature_results: Dict[str, Dict[str, str]] = {}
        for feature in features:
            question = f"这张图片中的{feature}看起来自然吗？请给出是或否的回答并简单说明原因"
            answer = self.analyze_image(image, question)
            feature_results[feature] = {"question": question, "answer": answer}
        return feature_results


DEEPFAKE_FEATURES: List[str] = [
    "面部布局",
    "眼睛",
    "鼻子",
    "嘴巴",
    "皮肤纹理",
    "光照阴影",
    "面部边界融合",
    "面部对称性",
    "牙齿",
    "头发",
]


def test_llava_model() -> None:
    """命令行下的快速测试"""
    try:
        from image_utils import get_test_images, ImageProcessor

        print("=== 测试 LLaVA 模型 ===")
        detector = LLaVADetector()

        test_images = get_test_images()
        if not test_images:
            print("没有找到测试图像")
            return

        image_path = test_images[0]
        print(f"\n测试图像: {image_path}")

        processor = ImageProcessor()
        image = processor.load_image(image_path)
        if image is None:
            print("无法加载测试图像")
            return

        print("\n=== 基础深度伪造检测 ===")
        results = detector.detect_deepfake_basic(image)
        for item in results.values():
            if "error" in item:
                print(f"错误: {item['error']}")
            else:
                print(f"\n问题: {item['question']}")
                print(f"回答: {item['answer']}")

        print("\n测试完成")
    except Exception as err:  # pragma: no cover
        print(f"测试失败: {err}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_llava_model()
