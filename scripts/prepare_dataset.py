#!/usr/bin/env python3
"""Build training and runtime data from the Markdown problem bank."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Iterable


SYSTEM_PROMPT = (
    "你是数学实验课程的 MATLAB 编程助手。"
    "用户会给出数学实验题目，请输出可直接运行或稍作保存即可运行的完整 MATLAB 代码。"
    "优先使用清晰变量名、必要注释和题目要求中的参数。"
)

CONTENT_REF_RE = re.compile(r"\s*:contentReference\[[^\n]*")
FENCE_RE = re.compile(r"```(?:matlab|MATLAB|m)?\s*\n(.*?)```", re.DOTALL)
TOP_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$")
QUESTION_HEADING_RE = re.compile(r"^##\s*题目\s*$")
CODE_HEADING_RE = re.compile(r"^##\s*代码\s*$")


def clean_text(text: str) -> str:
    text = CONTENT_REF_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def extract_code_output(answer_md: str) -> str:
    """Prefer fenced MATLAB code while keeping multi-file answers together."""
    blocks = [block.strip() for block in FENCE_RE.findall(answer_md) if block.strip()]
    if blocks:
        return "\n\n".join(blocks).strip()
    return answer_md.strip()


def split_problem_chunks(lines: list[str]) -> Iterable[tuple[str, list[str]]]:
    starts: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        match = TOP_HEADING_RE.match(line)
        if match:
            starts.append((idx, match.group(1).strip()))

    for pos, (start, title) in enumerate(starts):
        end = starts[pos + 1][0] if pos + 1 < len(starts) else len(lines)
        yield title, lines[start:end]


def parse_markdown_file(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    items: list[dict[str, str]] = []

    for title, chunk in split_problem_chunks(lines):
        question_idx = None
        code_idx = None
        for idx, line in enumerate(chunk):
            if question_idx is None and QUESTION_HEADING_RE.match(line):
                question_idx = idx
                continue
            if question_idx is not None and CODE_HEADING_RE.match(line):
                code_idx = idx
                break

        if question_idx is None or code_idx is None:
            continue

        question = clean_text("\n".join(chunk[question_idx + 1 : code_idx]))
        answer_md = clean_text("\n".join(chunk[code_idx + 1 :]))
        output = extract_code_output(answer_md)

        if question and output:
            items.append(
                {
                    "source_file": path.name,
                    "title": title,
                    "question": question,
                    "answer_md": answer_md,
                    "output": output,
                }
            )

    return items


def discover_markdown_files(source_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in source_dir.glob("*.md")
        if path.name.lower() not in {"readme.md"} and path.is_file()
    )


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def to_messages_row(item: dict[str, str]) -> dict:
    return {
        "id": item["id"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": item["question"]},
            {"role": "assistant", "content": item["output"]},
        ],
    }


def to_alpaca_row(item: dict[str, str]) -> dict:
    return {
        "id": item["id"],
        "instruction": "根据数学实验题目生成完整 MATLAB 代码。",
        "input": item["question"],
        "output": item["output"],
    }


def build_examples(items: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "id": item["id"],
            "source_file": item["source_file"],
            "title": item["title"],
            "question": item["question"],
            "answer": item["output"],
        }
        for item in items
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default=".", help="Directory containing Markdown files.")
    parser.add_argument("--dataset-dir", default="dataset", help="Output directory for train/eval files.")
    parser.add_argument("--runtime-dir", default="runtime", help="Output directory for retrieval data.")
    parser.add_argument("--eval-ratio", type=float, default=0.15, help="Held-out eval ratio.")
    parser.add_argument("--seed", type=int, default=20260605)
    args = parser.parse_args()

    source_dir = Path(args.source_dir).resolve()
    dataset_dir = Path(args.dataset_dir).resolve()
    runtime_dir = Path(args.runtime_dir).resolve()
    dataset_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, str]] = []
    for path in discover_markdown_files(source_dir):
        items.extend(parse_markdown_file(path))

    for idx, item in enumerate(items, start=1):
        cls = Path(item["source_file"]).stem
        item["id"] = f"{cls}-{idx:03d}"

    rng = random.Random(args.seed)
    shuffled = items[:]
    rng.shuffle(shuffled)
    eval_count = max(1, round(len(shuffled) * args.eval_ratio)) if shuffled else 0
    eval_items = sorted(shuffled[:eval_count], key=lambda item: item["id"])
    train_items = sorted(shuffled[eval_count:], key=lambda item: item["id"])

    write_jsonl(dataset_dir / "raw_pairs.jsonl", items)
    write_jsonl(dataset_dir / "train.jsonl", [to_messages_row(item) for item in train_items])
    write_jsonl(dataset_dir / "eval.jsonl", [to_messages_row(item) for item in eval_items])
    write_jsonl(dataset_dir / "train_alpaca.jsonl", [to_alpaca_row(item) for item in train_items])
    write_jsonl(dataset_dir / "eval_alpaca.jsonl", [to_alpaca_row(item) for item in eval_items])

    examples_path = runtime_dir / "examples.json"
    examples_path.write_text(
        json.dumps(build_examples(items), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "source_dir": str(source_dir),
        "markdown_files": [path.name for path in discover_markdown_files(source_dir)],
        "total_pairs": len(items),
        "train_pairs": len(train_items),
        "eval_pairs": len(eval_items),
        "dataset_dir": str(dataset_dir),
        "runtime_examples": str(examples_path),
    }
    (dataset_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
