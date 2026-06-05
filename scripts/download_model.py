#!/usr/bin/env python3
"""Download the base model from Hugging Face into the workspace."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--output-dir", default="models/Qwen2.5-Coder-1.5B-Instruct")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    path = snapshot_download(
        repo_id=args.repo_id,
        local_dir=output_dir,
        allow_patterns=[
            "*.json",
            "*.safetensors",
            "*.model",
            "*.txt",
            "*.md",
            "*.py",
        ],
    )
    print(f"Downloaded {args.repo_id} to {path}")


if __name__ == "__main__":
    main()
