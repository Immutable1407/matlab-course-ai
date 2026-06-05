#!/usr/bin/env python3
"""QLoRA fine-tuning for Qwen2.5-Coder-1.5B-Instruct on MATLAB problem data."""

from __future__ import annotations

import argparse
import json
import inspect
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)


DEFAULT_SYSTEM_PROMPT = (
    "你是数学实验课程的 MATLAB 编程助手。"
    "用户会给出数学实验题目，请输出完整、可运行的 MATLAB 代码。"
)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def row_to_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    """Support messages, instruction/input/output, and question/code style rows."""
    if isinstance(row.get("messages"), list):
        return [
            {"role": str(msg["role"]), "content": str(msg["content"])}
            for msg in row["messages"]
            if msg.get("role") and msg.get("content") is not None
        ]

    if row.get("output") is not None and (row.get("instruction") is not None or row.get("input") is not None):
        instruction = str(row.get("instruction", "")).strip()
        input_text = str(row.get("input", "")).strip()
        output = str(row.get("output", "")).strip()
        user_parts = [part for part in (instruction, input_text) if part]
        return [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": "\n\n".join(user_parts)},
            {"role": "assistant", "content": output},
        ]

    question = row.get("question") or row.get("prompt") or row.get("input")
    code = row.get("code") or row.get("answer") or row.get("output")
    if question is not None and code is not None:
        return [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": str(question).strip()},
            {"role": "assistant", "content": str(code).strip()},
        ]

    raise ValueError(f"Unsupported row format. Keys: {sorted(row.keys())}")


def split_prompt_and_full_text(row: dict[str, Any], tokenizer: AutoTokenizer) -> tuple[str, str]:
    messages = row_to_messages(row)
    assistant_indices = [idx for idx, msg in enumerate(messages) if msg["role"] == "assistant"]
    if not assistant_indices:
        raise ValueError("Each training row must contain an assistant/code answer.")

    last_assistant_idx = assistant_indices[-1]
    prompt_messages = messages[:last_assistant_idx]
    full_messages = messages[: last_assistant_idx + 1]

    prompt_text = tokenizer.apply_chat_template(
        prompt_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    full_text = tokenizer.apply_chat_template(
        full_messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    return prompt_text, full_text


def tokenize_row(row: dict[str, Any], tokenizer: AutoTokenizer, max_seq_length: int) -> dict[str, list[int]]:
    prompt_text, full_text = split_prompt_and_full_text(row, tokenizer)
    prompt_ids = tokenizer(
        prompt_text,
        truncation=True,
        max_length=max_seq_length,
        add_special_tokens=False,
    )["input_ids"]
    encoded = tokenizer(
        full_text,
        truncation=True,
        max_length=max_seq_length,
        add_special_tokens=False,
    )
    input_ids = encoded["input_ids"]
    labels = input_ids.copy()
    prompt_len = min(len(prompt_ids), len(labels))
    labels[:prompt_len] = [-100] * prompt_len

    return {
        "input_ids": input_ids,
        "attention_mask": encoded["attention_mask"],
        "labels": labels,
    }


def build_tokenized_dataset(path: str | Path, tokenizer: AutoTokenizer, max_seq_length: int) -> Dataset:
    rows = read_jsonl(path)
    records = [tokenize_row(row, tokenizer, max_seq_length) for row in rows]
    return Dataset.from_list(records)


class CausalLMCollator:
    def __init__(self, tokenizer: AutoTokenizer) -> None:
        self.tokenizer = tokenizer

    def __call__(self, features: list[dict[str, list[int]]]) -> dict[str, torch.Tensor]:
        max_len = max(len(feature["input_ids"]) for feature in features)
        pad_id = self.tokenizer.pad_token_id

        batch_input_ids = []
        batch_attention_mask = []
        batch_labels = []
        for feature in features:
            pad_len = max_len - len(feature["input_ids"])
            batch_input_ids.append(feature["input_ids"] + [pad_id] * pad_len)
            batch_attention_mask.append(feature["attention_mask"] + [0] * pad_len)
            batch_labels.append(feature["labels"] + [-100] * pad_len)

        return {
            "input_ids": torch.tensor(batch_input_ids, dtype=torch.long),
            "attention_mask": torch.tensor(batch_attention_mask, dtype=torch.long),
            "labels": torch.tensor(batch_labels, dtype=torch.long),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name_or_path", default="models/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--train_file", default="dataset/final_train.jsonl")
    parser.add_argument("--eval_file", default="dataset/final_eval.jsonl")
    parser.add_argument("--output_dir", default="outputs/qwen_matlab_lora")
    parser.add_argument("--max_seq_length", type=int, default=2048)
    parser.add_argument("--lora_rank", type=int, default=8)
    parser.add_argument("--lora_alpha", type=int, default=16)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    parser.add_argument("--num_train_epochs", type=float, default=3)
    parser.add_argument("--per_device_train_batch_size", type=int, default=1)
    parser.add_argument("--per_device_eval_batch_size", type=int, default=1)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--warmup_ratio", type=float, default=0.03)
    parser.add_argument("--logging_steps", type=int, default=10)
    parser.add_argument("--eval_steps", type=int, default=25)
    parser.add_argument("--save_steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=20260605)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name_or_path,
        trust_remote_code=True,
        use_fast=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name_or_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    model.config.use_cache = False
    model.config.pad_token_id = tokenizer.pad_token_id
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    lora_config = LoraConfig(
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )
    model = get_peft_model(model, lora_config)
    model.enable_input_require_grads()
    model.print_trainable_parameters()

    train_dataset = build_tokenized_dataset(args.train_file, tokenizer, args.max_seq_length)
    eval_dataset = build_tokenized_dataset(args.eval_file, tokenizer, args.max_seq_length)

    training_kwargs = {
        "output_dir": args.output_dir,
        "num_train_epochs": args.num_train_epochs,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "per_device_eval_batch_size": args.per_device_eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "learning_rate": args.learning_rate,
        "warmup_ratio": args.warmup_ratio,
        "lr_scheduler_type": "cosine",
        "optim": "paged_adamw_8bit",
        "fp16": True,
        "bf16": False,
        "gradient_checkpointing": True,
        "logging_steps": args.logging_steps,
        "eval_steps": args.eval_steps,
        "save_strategy": "steps",
        "save_steps": args.save_steps,
        "save_total_limit": 2,
        "report_to": "none",
        "seed": args.seed,
        "dataloader_num_workers": 0,
        "dataloader_pin_memory": False,
    }
    if "eval_strategy" in inspect.signature(TrainingArguments).parameters:
        training_kwargs["eval_strategy"] = "steps"
    else:
        training_kwargs["evaluation_strategy"] = "steps"
    training_args = TrainingArguments(**training_kwargs)

    data_collator = CausalLMCollator(tokenizer)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print(f"Saved LoRA adapter to: {args.output_dir}")


if __name__ == "__main__":
    main()
