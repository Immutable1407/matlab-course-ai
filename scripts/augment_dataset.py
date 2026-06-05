#!/usr/bin/env python3
"""Create conservative augmented training data for MATLAB code generation."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_dataset import SYSTEM_PROMPT, parse_markdown_file  # noqa: E402


QUESTION_TEMPLATES = [
    "{question}",
    "请用 MATLAB 完成下面的数学实验题，要求代码完整、变量命名清晰，并输出必要结果。\n\n{question}",
    "下面是一道数学实验编程题。请根据题意写出可运行的 MATLAB 程序。\n\n{question}",
    "根据以下要求生成 MATLAB 脚本，代码中保留必要的计算步骤、图形绘制和结果输出。\n\n{question}",
    "请把下面题目的计算任务、误差分析或作图要求用 MATLAB 实现，直接给出完整代码。\n\n{question}",
    "为这道课程作业题编写 MATLAB 代码。若题目包含参数、区间、阈值或样本量，请以题目给出的数值为准。\n\n{question}",
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def to_base_item(row: dict) -> dict:
    return {
        "id": row["id"],
        "source_file": row.get("source_file", ""),
        "title": row.get("title", ""),
        "question": row["question"],
        "output": row["output"],
    }


def load_supplemental(markdown_path: Path) -> list[dict]:
    if not markdown_path.exists():
        return []

    items = parse_markdown_file(markdown_path)
    result = []
    for idx, item in enumerate(items, start=1):
        result.append(
            {
                "id": f"SUP-{idx:03d}",
                "source_file": markdown_path.name,
                "title": item["title"],
                "question": item["question"],
                "output": item["output"],
            }
        )
    return result


def build_augmented_items(base_items: list[dict], variants_per_item: int) -> list[dict]:
    templates = QUESTION_TEMPLATES[: max(1, variants_per_item)]
    augmented = []
    for item in base_items:
        for variant_idx, template in enumerate(templates, start=1):
            question = template.format(question=item["question"])
            augmented.append(
                {
                    "id": f"{item['id']}-v{variant_idx:02d}",
                    "base_id": item["id"],
                    "source_file": item["source_file"],
                    "title": item["title"],
                    "question": question,
                    "output": item["output"],
                    "augmentation": "original" if variant_idx == 1 else "prompt_rewrite",
                }
            )
    return augmented


def to_messages_row(item: dict) -> dict:
    return {
        "id": item["id"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": item["question"]},
            {"role": "assistant", "content": item["output"]},
        ],
    }


def to_alpaca_row(item: dict) -> dict:
    return {
        "id": item["id"],
        "instruction": "根据数学实验题目生成完整 MATLAB 代码。",
        "input": item["question"],
        "output": item["output"],
    }


def to_runtime_examples(base_items: list[dict]) -> list[dict]:
    return [
        {
            "id": item["id"],
            "source_file": item["source_file"],
            "title": item["title"],
            "question": item["question"],
            "answer": item["output"],
        }
        for item in base_items
    ]


def split_by_problem(items: list[dict], eval_ratio: float, seed: int) -> tuple[list[dict], list[dict]]:
    rng = random.Random(seed)
    shuffled = items[:]
    rng.shuffle(shuffled)

    eval_count = max(1, round(len(shuffled) * eval_ratio)) if shuffled else 0
    eval_ids = {item["id"] for item in shuffled[:eval_count]}
    train_items = [item for item in items if item["id"] not in eval_ids]
    eval_items = [item for item in items if item["id"] in eval_ids]
    return train_items, eval_items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-pairs", default="dataset/raw_pairs.jsonl")
    parser.add_argument("--supplemental", default="supplemental/Supplemental.md")
    parser.add_argument("--dataset-dir", default="dataset")
    parser.add_argument("--runtime-dir", default="runtime")
    parser.add_argument("--variants-per-item", type=int, default=6)
    parser.add_argument("--eval-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=20260605)
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir).resolve()
    runtime_dir = Path(args.runtime_dir).resolve()
    dataset_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    raw_items = [to_base_item(row) for row in read_jsonl(Path(args.raw_pairs))]
    supplemental_items = load_supplemental(Path(args.supplemental))
    base_items = raw_items + supplemental_items

    train_base, eval_base = split_by_problem(base_items, args.eval_ratio, args.seed)
    train_augmented = build_augmented_items(train_base, args.variants_per_item)
    eval_original = build_augmented_items(eval_base, 1)

    write_jsonl(dataset_dir / "augmented_pairs.jsonl", train_augmented + eval_original)
    write_jsonl(dataset_dir / "final_train.jsonl", [to_messages_row(item) for item in train_augmented])
    write_jsonl(dataset_dir / "final_eval.jsonl", [to_messages_row(item) for item in eval_original])
    write_jsonl(dataset_dir / "final_train_alpaca.jsonl", [to_alpaca_row(item) for item in train_augmented])
    write_jsonl(dataset_dir / "final_eval_alpaca.jsonl", [to_alpaca_row(item) for item in eval_original])

    final_examples_path = runtime_dir / "final_examples.json"
    final_examples_path.write_text(
        json.dumps(to_runtime_examples(base_items), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "raw_items": len(raw_items),
        "supplemental_items": len(supplemental_items),
        "base_items": len(base_items),
        "train_base_items": len(train_base),
        "eval_base_items": len(eval_base),
        "variants_per_train_item": min(args.variants_per_item, len(QUESTION_TEMPLATES)),
        "final_train_rows": len(train_augmented),
        "final_eval_rows": len(eval_original),
        "runtime_examples": str(final_examples_path),
        "method": "保守增强：训练题目改写 + 补充常见算法样例；不自动替换代码参数。",
    }

    (dataset_dir / "augmentation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
