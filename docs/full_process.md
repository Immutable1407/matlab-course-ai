# 全流程复盘：从课程题库到离线便携 AI

本文记录 `matlab-course-ai` 的完整实践过程。它不是单纯训练一个模型，而是一次包含数据整理、训练、转换、实战机推理器调教和最终封装的端到端本地 AI 工程。

## 1. 数据处理

项目起点是 9 个数学实验课程 Markdown 题库文件：`Cls01.md` 到 `Cls09.md`。每道题按照标题、`## 题目`、`## 代码` 的结构组织。

`scripts/prepare_dataset.py` 的任务是把这些 Markdown 转换成训练数据：

- 扫描根目录下的课程 Markdown。
- 按一级标题切分题目块。
- 提取 `## 题目` 到 `## 代码` 之间的题面。
- 提取 `## 代码` 之后的 MATLAB 标准答案。
- 优先保留 fenced code block 中的 MATLAB 代码。
- 输出 messages 格式和 Alpaca 格式两类 JSONL。
- 生成运行时检索库 `runtime/examples.json`。

第一轮结果：

```text
Markdown 源文件：9 个
题目-代码配对：49 组
初始训练集：42 条
初始验证集：7 条
```

当时测试发现，积分、脑网络等题型可以检索到合适参考题；但“二分法”没有命中，因为原始题库确实没有二分法样例。这成为后续补题和增强的直接动机。

## 2. 有依据的数据增强

增强目标不是编造新题，而是在不破坏题面与代码一致性的前提下扩大表达覆盖。

`supplemental/Supplemental.md` 补充了 10 个数学实验常见题型，包括：

- 二分法
- 牛顿法
- 割线法
- 插值
- 最小二乘拟合
- 数值微分
- 常微分方程
- Jacobi 迭代
- Runge-Kutta

`scripts/augment_dataset.py` 的增强策略：

- 合并 49 个原始样例和 10 个补充样例。
- 对训练题生成多种中文题面改写。
- 验证集只保留原始题面。
- 按题目切分训练/验证，避免同一道题的改写进入两边。
- 不自动替换代码中的参数，避免生成参数不一致的数据。

最终结果：

```text
基础样例：59 组
最终训练集：300 条
最终验证集：9 条
运行时检索样例：59 条
```

后续抽查和全量校验确认：

```text
rows: 300
missing_base: 0
output_mismatch: 0
base_question_not_in_prompt: 0
```

这说明增强数据的答案不是临时生成或臆造的，而是能回到基础样例。

## 3. 训练环境与 QLoRA

训练模型选择：

```text
Qwen/Qwen2.5-Coder-1.5B-Instruct
```

这个选择兼顾代码能力、中文题面理解、模型规模和后续低配 CPU 推理可行性。

最初计划是在 Windows + CUDA 训练机下载模型。后来为了避免训练机重复联网，先在 Mac 上创建 `.venv-download`，安装 `huggingface_hub`，把基础模型下载到：

```text
models/Qwen2.5-Coder-1.5B-Instruct
```

随后把 `train.py`、`merge_lora.py`、`test_infer.py` 的默认基础模型路径改成本地目录，使 Windows 训练阶段可以直接使用本地模型。

训练脚本 `train.py` 的关键配置：

```text
4bit NF4
double quant
LoRA rank = 8
LoRA alpha = 16
max_seq_length = 2048
per_device_train_batch_size = 1
gradient_accumulation_steps = 8
epoch = 3
gradient checkpointing = true
output_dir = outputs/qwen_matlab_lora
```

训练数据格式兼容：

- `messages`
- `instruction/input/output`
- `question/code`
- `question/output`
- `question/answer`

训练时只对 assistant 的代码答案计算 loss，system prompt 和用户题面被 mask 掉。这比整段文本都参与 loss 更符合“输入题目，输出代码”的目标。

Windows 训练阶段流程：

```bash
pip install -r requirements.txt
python train.py
python test_infer.py --load_in_4bit --question "用二分法求 x^3-x-1=0 在 [1,2] 内的根，输出迭代过程。"
python merge_lora.py
```

训练完成后得到：

```text
outputs/qwen_matlab_lora
outputs/qwen_matlab_merged
```

其中 `qwen_matlab_lora` 是 LoRA adapter，`qwen_matlab_merged` 是合并后的完整 Hugging Face 模型。

## 4. 转换、量化与本地测试

训练结果拷回 Mac 后，目标变成把 HF 模型变成低配 Windows 可跑的 GGUF。

先尝试获取 `llama.cpp` 工具链。过程中遇到过 GitHub clone/zip 下载缓慢、Homebrew 安装等待等问题；最终 Homebrew 版 `llama.cpp` 提供了 `convert_hf_to_gguf.py` 和 `llama-quantize`。

转换脚本依赖方面出现一个版本不匹配：Homebrew 的转换脚本引用了 PyPI `gguf` 包中不存在的枚举。由于本次只转换文本模型，最终复制转换脚本为：

```text
scripts/convert_hf_to_gguf_compat.py
```

并做了最小兼容补丁。

转换结果：

```text
gguf/qwen_matlab_f16.gguf
```

量化结果：

```text
gguf/qwen_matlab_q4_k_m.gguf
```

Q4_K_M 模型约 940MB，适合 8GB RAM 的低配 CPU 机器。

Mac 本地测试中还遇到 Metal 后端初始化问题，最终通过 `--device none` 强制 CPU 路线解决。随后又对 `app/ask_code.py` 做了多轮调教：

- 自动使用 Qwen ChatML 模板。
- 加入 `--device none`。
- 加入 `--no-escape`，防止 prompt 中 MATLAB 字符串反斜杠被错误处理。
- 加入 `--no-conversation`。
- 捕获 stdout 并清理 `llama_perf_*` 和 `[end of text]`。
- 在缺少模型或推理器时支持只打印 prompt。

这一路线在 Mac 上可以打通，但目标 Windows 机上仍然需要解决 `llama-cli.exe` 兼容性。

## 5. 实战机推理器调教

目标机配置较弱：

```text
Windows 10 19045
Intel i5-6500
8GB RAM
GT 730 2GB
Python 未安装
```

最初部署包包含：

```text
Open Mat/
├── app/
│   ├── ask_code.bat
│   ├── ask_code.py
│   ├── llama-cli.exe
│   └── DLL
├── gguf/
│   └── qwen_matlab_q4_k_m.gguf
└── runtime/
```

在目标机上，`llama.cpp` 三类联通测试失败：

```bat
app\llama-cli.exe
app\llama-cli.exe -h
app\llama-cli.exe --version
```

表现为立即返回命令行，无输出。后续错误码 `-1073741819` 指向 `0xC0000005` Access Violation。结合 `-h` 都无法输出，问题基本锁定在 Windows 二进制或运行库兼容性，而不是 GGUF 模型。

当时准备过的排查路线包括：

- 确认模型文件大小和路径。
- 检查 `llama-cli.exe` 与 DLL 是否齐全。
- 下载旧版 `llama.cpp` CPU x64 包。
- 准备无 Python 的 `ask_direct_no_python.bat`。
- 检查 VC++ Redistributable。
- 考虑 AVX2、SSE42、generic x64 多套构建。

后来切换到 KoboldCpp。第一次测试确认 `koboldcpp.exe` 能显示 help，说明它在目标机上的兼容性更好。

KoboldCpp 启动脚本也经历了失败：复杂 bat 中的中文 echo、多行 `^` 续行、括号和路径处理容易被 Windows cmd 误解析，出现“不是内部或外部命令”“找不到路径”等错误。

最终通过手动命令验证 KoboldCpp 可以加载模型：

```text
Load Text Model OK: True
Starting Kobold API on port 5001
Starting OpenAI Compatible API on port 5001
Please connect to custom endpoint at http://localhost:5001
```

这证明目标机可以运行本地 AI，失败点不是模型训练成果，而是推理器和启动脚本的适配。

## 6. 最终封装

最终把 `Open Mat` 精简为最小可运行包：

```text
Open Mat/
├── app_koboldcpp/
│   └── koboldcpp.exe
├── gguf/
│   └── qwen_matlab_q4_k_m.gguf
├── start_cpu.bat
└── README.md
```

`start_cpu.bat` 的设计原则：

- 输出使用英文。
- 不使用中文 echo。
- 不使用多行续行符。
- 不使用复杂括号。
- 启动命令单行。
- 保留 `pause`，方便查看错误。
- 使用 CPU 保守参数。

最终启动命令核心为：

```bat
app_koboldcpp\koboldcpp.exe --model "gguf\qwen_matlab_q4_k_m.gguf" --contextsize 2048 --port 5001 --skiplauncher --noblas
```

用户只需要双击 `start_cpu.bat`，等待模型加载成功，再访问：

```text
http://localhost:5001
```

## 7. 工程经验

这次实践的关键价值不只在于微调模型，而在于把整个本地 AI 链路跑通：

- 数据要可追溯，不能为了数量制造脏样本。
- 小模型训练要服从目标硬件，而不是只看训练机能力。
- 训练结果需要经过合并、转换、量化，才能进入真实部署。
- 目标机的失败常常不在模型，而在运行库、CPU 指令集、Windows 批处理和推理器二进制。
- 最终封装要服务于真实用户环境：少依赖、少脚本复杂度、少路径假设。

最终项目可以概括为四阶段：

```text
数据处理 -> 模型训练 -> 实地测试 -> 离线封装
```

它是一份完整的课程专项本地 AI 模型训练部署案例。
