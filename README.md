# MATLAB 课程专项本地 AI

本项目记录了一次从课程题库到本地离线 AI 的完整实践：把数学实验课程中的 MATLAB 题目整理成 Markdown，转换为可训练数据，进行有依据的数据增强，在 Windows CUDA 环境中微调 Qwen2.5-Coder-1.5B-Instruct，再把训练结果转换、量化并封装成可在低配 Windows 机器上运行的本地 AI。

最终便携包位于本地 `Open Mat/`。GitHub 仓库只保存源码、文档和关键小体积数据；GGUF 模型、Hugging Face 权重、KoboldCpp 可执行文件、训练输出等大文件保留在本地，不进入仓库。

## 项目结论

- 原始题库：9 个 `Cls*.md`，共抽取 49 组题目-代码配对。
- 补充样例：`supplemental/Supplemental.md`，共 10 组常见数学实验题。
- 基础样例：59 组，可用于训练增强和运行时检索。
- 最终训练集：`dataset/final_train.jsonl`，300 条。
- 最终验证集：`dataset/final_eval.jsonl`，9 条，按题目隔离。
- 微调方式：Qwen2.5-Coder-1.5B-Instruct + 4bit QLoRA。
- 训练输出：LoRA adapter、合并后的 HF 模型、F16 GGUF、Q4_K_M GGUF。
- 最终部署：低配 Windows 10 机器上使用 KoboldCpp + Q4_K_M GGUF 成功启动。

## 目标机器

最终实战机配置如下：

```text
系统：Windows 10 专业版 64 位，Version 19045
CPU：Intel Core i5-6500，4 核 4 线程，Skylake
内存：8GB RAM
显卡：NVIDIA GeForce GT 730，2GB VRAM
磁盘：HDD + SATA SSD
Python：未安装
```

训练阶段不在这台机器上完成。训练使用 Windows + NVIDIA GPU + CUDA 环境，实战机只负责离线推理。

## 目录说明

```text
.
├── Cls01.md ... Cls09.md          # 原始课程题库 Markdown
├── supplemental/                  # 补充的真实常见题型样例
├── scripts/                       # 数据准备、增强、下载和 GGUF 兼容转换脚本
├── dataset/                       # 可训练 JSONL 数据和统计文件
├── runtime/                       # 纯 Python 检索增强 prompt 构建
├── app/                           # llama.cpp 路线的便携入口脚本
├── deploy/                        # Windows llama.cpp 排障说明
├── docs/                          # 全流程复盘文档
└── Open Mat/                      # 本地最终便携包，仓库只保留 README 和启动脚本
```

以下目录或文件只保留本地，不推送到 GitHub：

```text
models/
outputs/
gguf/
Open Mat/gguf/
Open Mat/app_koboldcpp/
*.gguf
*.safetensors
*.zip
```

## 数据处理

原始题库采用统一结构：

```text
# 题目标题
## 题目
题面内容

## 代码
MATLAB 标准答案
```

运行：

```bash
python3 scripts/prepare_dataset.py
```

会生成：

```text
dataset/raw_pairs.jsonl
dataset/train.jsonl
dataset/eval.jsonl
dataset/train_alpaca.jsonl
dataset/eval_alpaca.jsonl
runtime/examples.json
dataset/summary.json
```

增强数据：

```bash
python3 scripts/augment_dataset.py
```

会生成：

```text
dataset/augmented_pairs.jsonl
dataset/final_train.jsonl
dataset/final_eval.jsonl
dataset/final_train_alpaca.jsonl
dataset/final_eval_alpaca.jsonl
runtime/final_examples.json
dataset/augmentation_summary.json
```

增强策略是保守增强：对训练题做多种中文题面改写，并补充常见数学实验算法样例；不自动替换代码中的参数，避免制造题面与答案不一致的脏数据。

## 数据可信度

这批增强数据不是编造新题，而是可追溯增强：

- `final_train.jsonl` 中每条样本都能追溯到 `raw_pairs.jsonl` 或 `supplemental/Supplemental.md` 的基础样例。
- 答案代码与基础样例完全一致。
- 改写题面包含原始题面或明确保留原始任务要求。
- 验证集按题目隔离，不让同一道题的改写同时进入训练和验证。

已做过抽查和全量校验：

```text
rows: 300
missing_base: 0
output_mismatch: 0
base_question_not_in_prompt: 0
```

## 训练

基础模型：

```text
Qwen/Qwen2.5-Coder-1.5B-Instruct
```

本地默认路径：

```text
models/Qwen2.5-Coder-1.5B-Instruct
```

如需重新下载：

```bash
.venv-download/bin/python scripts/download_model.py
```

Windows CUDA 训练环境安装依赖：

```bash
pip install -r requirements.txt
```

如果 CUDA 版 PyTorch 已经正确安装，不建议随意重装 `torch`，可只安装其余依赖：

```bash
pip install transformers datasets peft accelerate trl bitsandbytes safetensors
```

开始训练：

```bash
python train.py
```

默认训练配置：

```text
4bit NF4 + double quant
LoRA rank = 8
max_seq_length = 2048
per_device_train_batch_size = 1
gradient_accumulation_steps = 8
epoch = 3
output_dir = outputs/qwen_matlab_lora
```

测试 LoRA：

```bash
python test_infer.py --load_in_4bit --question "用二分法求 x^3-x-1=0 在 [1,2] 内的根，输出迭代过程。"
```

合并 LoRA：

```bash
python merge_lora.py
```

合并后的完整模型位于：

```text
outputs/qwen_matlab_merged
```

## 模型转换与量化

训练结果回到 Mac 后，转换为 GGUF，再量化为低配机器更适合的 Q4_K_M。

已生成的本地产物：

```text
gguf/qwen_matlab_f16.gguf       # F16 中间文件，约 2.9GB
gguf/qwen_matlab_q4_k_m.gguf    # Q4_K_M，约 940MB，最终推荐
```

转换过程中遇到过 Homebrew `llama.cpp` 转换脚本和 PyPI `gguf` 包枚举不匹配的问题，因此保留了本地兼容脚本：

```text
scripts/convert_hf_to_gguf_compat.py
```

Mac 上测试 `llama-cli` 时使用过：

```bash
llama-cli \
  -m gguf/qwen_matlab_q4_k_m.gguf \
  --device none \
  -p "<|im_start|>system\n你是数学实验课程的 MATLAB 编程助手。请只输出完整 MATLAB 代码。<|im_end|>\n<|im_start|>user\n用二分法求 x^3-x-1=0 在 [1,2] 内的根，输出迭代过程。<|im_end|>\n<|im_start|>assistant\n" \
  -n 256 -c 2048 --temp 0.2 --no-conversation
```

## 推理器调教

最初的部署路线是 `llama.cpp + llama-cli.exe`。在目标 Windows 机器上，三类联通测试均失败：

```bat
app\llama-cli.exe
app\llama-cli.exe -h
app\llama-cli.exe --version
```

现象是立即返回命令行，无 stdout、无 stderr、无弹窗。后续进一步得到过错误码 `-1073741819`，对应 Windows `0xC0000005` Access Violation，判断重点从模型文件转向推理器二进制兼容性。

排查方向包括：

- 确认 GGUF 文件存在且大小正常。
- 确认 `llama-cli.exe` 和 DLL 存在。
- 准备更旧的 `llama.cpp` CPU x64 包。
- 尝试无 Python 的 `ask_direct_no_python.bat`。
- 检查 VC++ Redistributable。
- 考虑 AVX2、SSE42、generic x64 路线。

最后切换为 KoboldCpp + GGUF。KoboldCpp 可显示 help，说明程序本体、运行库和 CPU 兼容性更合适。最终失败点主要收束到 Windows bat 文件编码、中文输出、多行续行符和路径解析问题。

最终成功状态：

```text
Load Text Model OK: True
Starting Kobold API on port 5001
Starting OpenAI Compatible API on port 5001
Please connect to custom endpoint at http://localhost:5001
```

## 最终便携包

本地 `Open Mat/` 已精简为：

```text
Open Mat/
├── app_koboldcpp/
│   └── koboldcpp.exe
├── gguf/
│   └── qwen_matlab_q4_k_m.gguf
├── start_cpu.bat
└── README.md
```

启动方式：

1. 双击 `start_cpu.bat`。
2. 等待出现 `Load Text Model OK: True`。
3. 浏览器打开 `http://localhost:5001`。
4. 使用期间不要关闭终端窗口。

`start_cpu.bat` 采用极简策略：

- 纯英文输出。
- 不使用中文 echo。
- 不使用 `^` 多行续行。
- 不使用复杂括号块。
- 启动命令写在一行。
- 默认 CPU 保守模式：`--contextsize 2048 --port 5001 --skiplauncher --noblas`。

## 校验命令

```bash
python3 scripts/prepare_dataset.py
python3 scripts/augment_dataset.py
python3 runtime/retrieval.py --question "用二分法求方程的根，并输出迭代过程"
python3 -m py_compile scripts/prepare_dataset.py scripts/augment_dataset.py runtime/retrieval.py app/ask_code.py train.py merge_lora.py test_infer.py
```

## 外部对话记录

ChatGPT 分享链接作为过程参考：

- https://chatgpt.com/share/6a22fdbc-44f8-83ea-b15d-983388ee1106
- https://chatgpt.com/share/6a22fdd8-3318-83ea-924b-96f3bfa86303

本仓库中的确定性结论优先来自当前工作区产物和可读取的 Codex 线程记录。
