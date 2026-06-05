#!/usr/bin/env python3
"""Quick inference test for the LoRA adapter or merged model."""

from __future__ import annotations

import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


SYSTEM_PROMPT = (
    "你是数学实验课程的 MATLAB 编程助手。"
    "请根据题目输出完整、可运行的 MATLAB 代码，只输出代码，不要解释。"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--lora_dir", default="outputs/qwen_matlab_lora")
    parser.add_argument("--merged_model", default=None, help="Use a merged model directory instead of base+LoRA.")
    parser.add_argument("--question", default="用二分法求 x^3-x-1=0 在 [1,2] 内的根，输出迭代过程。")
    parser.add_argument("--max_new_tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--load_in_4bit", action="store_true", help="Use 4bit loading for low VRAM inference.")
    return parser.parse_args()


def load_model(args: argparse.Namespace) -> tuple[AutoTokenizer, AutoModelForCausalLM]:
    model_path = args.merged_model or args.base_model
    tokenizer_path = args.merged_model or args.lora_dir

    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_path,
        trust_remote_code=True,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = None
    if args.load_in_4bit:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        quantization_config=quantization_config,
    )

    if args.merged_model is None:
        model = PeftModel.from_pretrained(model, args.lora_dir)

    model.eval()
    return tokenizer, model


def main() -> None:
    args = parse_args()
    tokenizer, model = load_model(args)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": args.question},
    ]
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    do_sample = args.temperature > 0
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=do_sample,
            temperature=args.temperature if do_sample else None,
            top_p=args.top_p if do_sample else None,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated = output_ids[0][inputs["input_ids"].shape[-1] :]
    print(tokenizer.decode(generated, skip_special_tokens=True).strip())


if __name__ == "__main__":
    main()
