#!/usr/bin/env python3
"""Portable command-line entry point for local MATLAB code generation."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
DEFAULT_EXAMPLES = RUNTIME_DIR / "final_examples.json"
DEFAULT_MODEL = ROOT / "gguf" / "qwen_matlab_q4_k_m.gguf"
DEFAULT_LLAMA = ROOT / "app" / "llama-cli.exe"

sys.path.insert(0, str(RUNTIME_DIR))
from retrieval import build_prompt, load_examples  # noqa: E402


def read_question() -> str:
    print("请输入题目。输入完成后，Windows 终端按 Ctrl+Z 再回车；macOS/Linux 按 Ctrl+D：")
    return sys.stdin.read().strip()


def run_llama(llama_cli: Path, model: Path, prompt: str, ctx_size: int, max_new_tokens: int) -> int:
    chat_prompt = (
        "<|im_start|>system\n"
        "你是数学实验课程的 MATLAB 编程助手。请只输出完整 MATLAB 代码。"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        f"{prompt}"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    command = [
        str(llama_cli),
        "-m",
        str(model),
        "--device",
        "none",
        "-p",
        chat_prompt,
        "-c",
        str(ctx_size),
        "-n",
        str(max_new_tokens),
        "--temp",
        "0.2",
        "--no-escape",
        "--no-conversation",
        "--no-display-prompt",
        "--no-perf",
    ]
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    output = result.stdout
    output = re.split(r"llama_perf_[a-z_]+:", output, maxsplit=1)[0]
    output = output.replace("[end of text]", "")
    print(output.strip())
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", help="Problem text. If omitted, read from stdin.")
    parser.add_argument("--examples", default=str(DEFAULT_EXAMPLES))
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--llama-cli", default=str(DEFAULT_LLAMA))
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--ctx-size", type=int, default=8192)
    parser.add_argument("--max-new-tokens", type=int, default=2048)
    parser.add_argument(
        "--print-prompt-only",
        action="store_true",
        help="Only print the retrieval-augmented prompt; useful before llama-cli/model are ready.",
    )
    args = parser.parse_args()

    question = args.question.strip() if args.question else read_question()
    examples = load_examples(Path(args.examples))
    prompt = build_prompt(question, examples, top_k=args.top_k)

    llama_cli = Path(args.llama_cli)
    if not llama_cli.exists() and args.llama_cli == str(DEFAULT_LLAMA):
        system_llama = shutil.which("llama-cli")
        if system_llama:
            llama_cli = Path(system_llama)
    model = Path(args.model)
    if args.print_prompt_only or not llama_cli.exists() or not model.exists():
        print(prompt)
        if not args.print_prompt_only:
            print("\n[提示] 尚未找到 llama-cli.exe 或 GGUF 模型，当前只输出 prompt。")
        return

    raise SystemExit(run_llama(llama_cli, model, prompt, args.ctx_size, args.max_new_tokens))


if __name__ == "__main__":
    main()
