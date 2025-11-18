"""LLaVA 7B 量化加载与快速测试脚本

使用说明:
  1. 确保已下载模型目录 (例如 models/llava-1.5-7b-hf)
  2. 安装 CUDA 版 torch 与 bitsandbytes (Windows 原生可能不稳定, 若失败可用 WSL)
  3. 运行示例:
     python code/llava_quant.py --model-dir models/llava-1.5-7b-hf --quant 4bit --image data/test_images/real_face_1.jpg

若量化条件不满足会自动回退 FP16 / CPU。
"""
from __future__ import annotations
import argparse, os, sys, time
from typing import Optional

os.environ.setdefault("USE_SLOW_TOKENIZERS", "1")
os.environ.setdefault("TRANSFORMERS_USE_FAST_TOKENIZER", "0")

import torch
from PIL import Image
from transformers import (
    AutoTokenizer,
    CLIPImageProcessor,
    LlavaForConditionalGeneration,
    LlavaProcessor,
)
try:
    from transformers import BitsAndBytesConfig  # type: ignore
    BNB_AVAILABLE = True
except Exception:
    BNB_AVAILABLE = False


def load_image(path: str) -> Optional[Image.Image]:
    try:
        return Image.open(path).convert("RGB")
    except Exception as e:
        print(f"[ERR] 加载图像失败: {e}")
        return None

def build(model_dir: str, quant: str, max_new_tokens: int, force_cpu: bool):
    has_cuda = torch.cuda.is_available() and not force_cpu
    device = torch.device('cuda' if has_cuda else 'cpu')
    print(f"[INFO] 设备: {device}")
    print(f"[INFO] 模型: {model_dir}")

    quant = quant.lower()
    use4 = quant == '4bit'
    use8 = quant == '8bit'

    if use4 and use8:
        print('[WARN] 同时指定 4bit/8bit, 采用 4bit')
        use8 = False
    if (use4 or use8) and not has_cuda:
        print('[WARN] 无 GPU, 量化失效 -> 回退全精度')
        use4 = use8 = False
    if (use4 or use8) and not BNB_AVAILABLE:
        print('[WARN] bitsandbytes 不可用 -> 回退全精度')
        use4 = use8 = False

    load_kwargs = dict(low_cpu_mem_usage=True)
    dtype = torch.float16 if has_cuda else torch.float32

    if use4:
        print('[INFO] 尝试 4bit 量化 (nf4)')
        load_kwargs['quantization_config'] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True,
        )
        load_kwargs['device_map'] = 'auto'
    elif use8:
        print('[INFO] 尝试 8bit 量化')
        load_kwargs['quantization_config'] = BitsAndBytesConfig(load_in_8bit=True)
        load_kwargs['device_map'] = 'auto'
    else:
        if has_cuda:
            print('[INFO] 使用 FP16')
        else:
            print('[INFO] 使用 CPU float32 (较慢)')

    t0 = time.time()
    print('[STEP] 加载处理器 ...')
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False)
    image_processor = CLIPImageProcessor.from_pretrained(model_dir)
    processor = LlavaProcessor(image_processor=image_processor, tokenizer=tokenizer)
    print('[STEP] 加载模型 ...')
    model = LlavaForConditionalGeneration.from_pretrained(
        model_dir,
        torch_dtype=dtype,
        **load_kwargs,
    )
    if load_kwargs.get('device_map') is None:
        model.to(device)
    print(f'[OK] 模型加载完成，用时 {time.time()-t0:.1f}s')
    try:
        params = sum(p.numel() for p in model.parameters())/1e9
        print(f'[INFO] 参数量 ≈ {params:.2f}B')
    except Exception:
        pass
    return processor, model, device

def infer(processor, model, device, image: Image.Image, question: str, max_new_tokens: int):
    prompt = f"USER: <image>\n{question}\nASSISTANT:"
    # 需要使用关键字参数，避免新版 transformers 将第一个位置参数当作 images 处理
    # 正确形式: text=prompt, images=image
    inputs = processor(text=prompt, images=image, return_tensors='pt')
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=processor.tokenizer.eos_token_id,
        )
    text = processor.batch_decode(out, skip_special_tokens=True)[0]
    if 'ASSISTANT:' in text:
        text = text.split('ASSISTANT:')[-1].strip()
    return text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-dir', required=True)
    ap.add_argument('--image', default='data/test_images/real_face_1.jpg')
    ap.add_argument('--question', default='Describe the face briefly.')
    ap.add_argument('--quant', choices=['none','4bit','8bit'], default='4bit')
    ap.add_argument('--max-new-tokens', type=int, default=64)
    ap.add_argument('--force-cpu', action='store_true')
    args = ap.parse_args()

    if not os.path.isdir(args.model_dir):
        print('[ERR] 模型目录不存在')
        sys.exit(1)
    img = load_image(args.image)
    if img is None:
        sys.exit(1)

    processor, model, device = build(args.model_dir, args.quant, args.max_new_tokens, args.force_cpu)
    print('[STEP] 推理 ...')
    t0 = time.time()
    ans = infer(processor, model, device, img, args.question, args.max_new_tokens)
    dt = time.time() - t0
    print('\n==== 英文回答 ====' )
    print(ans)
    zh_q = '请判断这张人脸是否真实，仅回答: 真实 / 可疑 / 伪造'
    zh_ans = infer(processor, model, device, img, zh_q, 32)
    print('\n==== 中文回答 ====' )
    print(zh_q)
    print(zh_ans)
    print(f'\n[INFO] 生成耗时 {dt:.2f}s (不含加载)')

if __name__ == '__main__':
    main()
