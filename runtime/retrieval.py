#!/usr/bin/env python3
"""Pure-Python retrieval and prompt builder for the portable MATLAB code assistant."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path


SYSTEM_PROMPT = (
    "你是数学实验课程的 MATLAB 编程助手。"
    "请根据当前题目生成完整、可运行的 MATLAB 代码。"
    "参考题只用于学习风格和结构；如果当前题目的参数不同，必须以当前题目为准。"
)

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|[\u4e00-\u9fff]")


def tokenize(text: str) -> Counter[str]:
    tokens = TOKEN_RE.findall(text.lower())
    counter: Counter[str] = Counter(tokens)
    compact = "".join(tokens)
    for idx in range(max(0, len(compact) - 1)):
        counter[f"bi:{compact[idx:idx + 2]}"] += 1
    return counter


def cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(value * right.get(key, 0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def load_examples(path: Path) -> list[dict[str, str]]:
    return json.loads(path.read_text(encoding="utf-8"))


def rank_examples(question: str, examples: list[dict[str, str]], top_k: int = 3) -> list[dict]:
    query_vec = tokenize(question)
    ranked: list[dict] = []
    for example in examples:
        text = example["question"] + "\n" + example.get("title", "")
        score = cosine(query_vec, tokenize(text))
        ranked.append({"score": score, **example})
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def build_prompt(question: str, examples: list[dict[str, str]], top_k: int = 3) -> str:
    selected = rank_examples(question, examples, top_k=top_k)
    parts = [SYSTEM_PROMPT, "", "下面是相似题目和参考 MATLAB 代码："]
    for idx, example in enumerate(selected, start=1):
        parts.extend(
            [
                "",
                f"【参考题 {idx}】{example['title']}（相似度 {example['score']:.3f}）",
                "题目：",
                example["question"],
                "代码：",
                example["answer"],
            ]
        )
    parts.extend(
        [
            "",
            "当前题目：",
            question.strip(),
            "",
            "请只输出完整 MATLAB 代码，不要输出解释。",
        ]
    )
    return "\n".join(parts).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--examples", default="runtime/final_examples.json")
    parser.add_argument("--question")
    parser.add_argument("--question-file")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    if args.question_file:
        question = Path(args.question_file).read_text(encoding="utf-8")
    elif args.question:
        question = args.question
    else:
        print("请输入题目，结束后按 Ctrl-D / Ctrl-Z：")
        question = sys.stdin.read()

    examples = load_examples(Path(args.examples))
    print(build_prompt(question, examples, top_k=args.top_k))


if __name__ == "__main__":
    main()
