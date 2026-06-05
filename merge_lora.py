#!/usr/bin/env python3
"""Merge a trained LoRA adapter into the Qwen base model."""

from __future__ import annotations

import argparse

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--lora_dir", default="outputs/qwen_matlab_lora")
    parser.add_argument("--output_dir", default="outputs/qwen_matlab_merged")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tokenizer = AutoTokenizer.from_pretrained(
        args.lora_dir,
        trust_remote_code=True,
        use_fast=True,
    )

    base_model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, args.lora_dir)
    model = model.merge_and_unload()

    model.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)

    print(f"Saved merged model to: {args.output_dir}")


if __name__ == "__main__":
    main()
