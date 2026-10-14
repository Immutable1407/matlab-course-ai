# MATLAB 课程专项本地 AI

一个从课程题库出发的本地代码生成项目：将 MATLAB 数学实验题整理为可追溯训练数据，使用 Qwen2.5-Coder-1.5B-Instruct 进行 QLoRA 微调，再将模型合并、转换和量化，适配低配置 Windows 电脑上的离线推理。

仓库提供题库、数据、训练与推理脚本及部署复盘。模型权重和推理器二进制未随仓库提交，需要自行训练或补齐已有本地产物。

## 项目流程

```text
9 份课程 Markdown + 补充题型
  → 题目 / MATLAB 代码配对
  → 按基础题目划分训练与验证
  → 保留原题的提示改写增强
  → Qwen 1.5B + 4-bit QLoRA
  → LoRA 合并与 GGUF 转换
  → Q4_K_M 量化
  → Windows CPU 离线推理
```

项目还提供一条独立的检索辅助路线：用课程题库构造相似题 prompt，再交给 llama.cpp。它与最终 KoboldCpp 便携包是不同的使用入口。

## 数据规模与处理方式

| 数据 | 数量 |
| --- | ---: |
| 课程文件 `Cls01.md`–`Cls09.md` | 9 |
| 原始题目与代码配对 | 49 |
| 补充数学实验样例 | 10 |
| 基础题目总数 | 59 |
| 用于训练的基础题目 | 50 |
| 验证基础题目 | 9 |
| 最终训练记录 | 300 |
| 最终验证记录 | 9 |
| 最终检索库样例 | 59 |

每个训练基础题生成 6 种提示形式，包括原始题面和保留原题的指令包装；对应 MATLAB 答案保持不变。增强扩大的是表达覆盖，300 条训练记录不代表 300 道独立题目。

训练与验证先按基础题目划分，再只对训练题增强，避免同一道题的改写跨越两边。当前提交的数据可追溯到课程文件或 [`supplemental/Supplemental.md`](supplemental/Supplemental.md)。

## 仓库结构

```text
Cls01.md ... Cls09.md          # 课程题库
supplemental/                 # 额外数学实验样例
dataset/                      # 基础、增强、messages 与 Alpaca 数据
scripts/                      # 数据处理、模型下载与 GGUF 转换
train.py                      # QLoRA 训练
test_infer.py                 # 单题推理检查
merge_lora.py                 # LoRA 合并
runtime/                      # 样例库与纯 Python 检索 prompt
app/                          # llama.cpp 命令行入口
Open Mat/                     # KoboldCpp 启动脚本与便携包说明
deploy/                       # llama.cpp Windows 排障记录
docs/full_process.md          # 全流程复盘
```

## 路线一：无需模型，查看数据与检索 prompt

数据处理和检索脚本仅使用 Python 标准库。在仓库根目录运行：

```bash
python3 scripts/prepare_dataset.py
python3 scripts/augment_dataset.py
python3 runtime/retrieval.py --question "用二分法求方程的根，并输出迭代过程"
```

前两条命令会重新生成 `dataset/` 和 `runtime/` 下的对应文件。`prepare_dataset.py` 生成基础 messages / Alpaca 数据与检索库；`augment_dataset.py` 合并补充样例并生成最终数据。

`runtime/retrieval.py` 按字符、词项与双字符组合的余弦相似度检索，默认拼接 3 个参考题。它不使用 embedding 或向量数据库，也不自行生成 MATLAB 代码。

亦可仅打印应用入口的 prompt：

```bash
python3 app/ask_code.py --question "用二分法求 x^3-x-1=0 在 [1,2] 内的根" --print-prompt-only
```

最终检索库包含全部 59 个基础题，包括验证题。评估模型泛化时应将纯模型表现与检索辅助表现分开，并限制检索库范围；否则不能把检索到验证答案后的结果当作未见题能力。

## 路线二：重新微调模型

训练需要兼容的 NVIDIA GPU / CUDA、PyTorch 和 bitsandbytes 环境。原项目记录使用 Windows CUDA 训练机，低配置部署机只承担推理。依赖列于 [`requirements.txt`](requirements.txt)，当前使用最低版本约束，未锁定完整复现环境。

在项目独立 Python 环境中安装依赖并下载基础模型：

```bash
python -m pip install -r requirements.txt
python scripts/download_model.py
```

下载脚本使用 `huggingface_hub`；若环境中未安装该包，需要补装。默认模型目录为 `models/Qwen2.5-Coder-1.5B-Instruct`。

开始训练：

```bash
python train.py
```

| 配置 | 默认值 |
| --- | --- |
| 模型 | `Qwen/Qwen2.5-Coder-1.5B-Instruct` |
| 数据 | `dataset/final_train.jsonl` / `dataset/final_eval.jsonl` |
| 量化 | 4-bit NF4 + double quant |
| LoRA | rank 8、alpha 16、dropout 0.05 |
| 最大序列长度 | 2048 |
| 单设备 batch / 梯度累积 | 1 / 8 |
| 训练轮数 / 学习率 | 3 / `2e-4` |
| 输出 | `outputs/qwen_matlab_lora` |

训练使用 Transformers `Trainer`；system 和 user 部分的 labels 被设为 `-100`，主要对 assistant 答案计算 loss。脚本兼容 messages、Alpaca 和题目/答案字段格式。

检查单题推理并合并 LoRA：

```bash
python test_infer.py --load_in_4bit --question "用二分法求 x^3-x-1=0 在 [1,2] 内的根，输出迭代过程。"
python merge_lora.py
```

合并结果默认写入 `outputs/qwen_matlab_merged`。`test_infer.py` 是单题 smoke test，仓库未提供自动执行 MATLAB、汇总通过率的完整评测器。

## 路线三：GGUF 与离线部署

合并后的 Hugging Face 模型需要转换成 GGUF，并使用外部 `llama-quantize` 量化。仓库保留 [`scripts/convert_hf_to_gguf_compat.py`](scripts/convert_hf_to_gguf_compat.py)，记录当时转换脚本与 `gguf` 包的兼容处理；转换工具及相关依赖需单独准备。

历史产物命名为：

```text
gguf/qwen_matlab_f16.gguf
gguf/qwen_matlab_q4_k_m.gguf
```

全流程复盘记录 Q4_K_M 文件约 940 MB，并记录在 Windows 10、i5-6500、8 GB RAM 的电脑上成功加载 KoboldCpp。仓库未包含这些二进制与权重，因此该成功状态属于历史部署记录，不能仅克隆仓库就直接复现。

补齐便携包：

```text
Open Mat/
├── app_koboldcpp/koboldcpp.exe       # 另行准备
├── gguf/qwen_matlab_q4_k_m.gguf      # 另行准备
├── start_cpu.bat
└── README.md
```

双击 `start_cpu.bat`，等待终端出现 `Load Text Model OK: True`，再打开浏览器访问 `http://localhost:5001`。使用时保持终端窗口开启。脚本采用 CPU 路线、2048 context、`--noblas` 和单行启动命令，缺少模型或可执行文件时会明确提示。

此便携启动脚本只加载模型和服务，**没有自动调用 `runtime/retrieval.py`**。需要相似题辅助时，应另行构造 prompt 或使用下一节的 Python 入口。

## llama.cpp 检索辅助入口

准备 GGUF 模型、兼容的 `llama-cli` 和 Python 后，可运行：

```bash
python3 app/ask_code.py --question "用牛顿法求方程的根，并输出迭代过程"
```

该入口默认使用 `runtime/final_examples.json`、`gguf/qwen_matlab_q4_k_m.gguf` 与 `app/llama-cli.exe`，也会尝试系统 PATH 中的 `llama-cli`。支持 `--model`、`--llama-cli`、`--top-k` 和上下文长度参数。模型或推理器缺失时仅打印 prompt，不代表推理成功。

原目标 Windows 机上的 llama.cpp 二进制曾遇到启动即退出和 `0xC0000005`，最终便携部署因此转向 KoboldCpp。排障记录见 [Windows 部署说明](deploy/README_llama_cpp_windows.md)。

## 检查与结果边界

语法检查：

```bash
python3 -m py_compile scripts/prepare_dataset.py scripts/augment_dataset.py runtime/retrieval.py app/ask_code.py train.py merge_lora.py test_infer.py
```

当前数据结构可核验：49 组课程题、10 组补充题、300 条训练记录、9 条验证记录；增强答案保持基础答案一致，训练与验证的基础题 ID 不重叠。这证明数据处理的可追溯性，不能证明每段 MATLAB 答案都正确，也不能证明微调优于基础模型。

仓库尚未提供模型对照、未见题执行通过率、量化前后质量比较或目标机器推理速度的系统测量。完整实践过程与历史部署证据见 [全流程复盘](docs/full_process.md)。

模型权重、adapter、GGUF、推理器可执行文件和训练输出留在本地；GitHub 保存源码、文档和这批课程数据。
