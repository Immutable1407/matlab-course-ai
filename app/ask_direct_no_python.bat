@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0\.."

if not exist "gguf\qwen_matlab_q4_k_m.gguf" (
  echo [错误] 找不到模型文件：gguf\qwen_matlab_q4_k_m.gguf
  pause
  exit /b 1
)

if not exist "app\llama-cli.exe" (
  echo [错误] 找不到推理程序：app\llama-cli.exe
  echo 请把 Windows 版 llama.cpp 文件放入 app 目录。
  pause
  exit /b 1
)

echo 请输入题目（单行），然后回车：
set /p QUESTION=^> 

if "%QUESTION%"=="" (
  echo [错误] 题目为空。
  pause
  exit /b 1
)

app\llama-cli.exe ^
  -m gguf\qwen_matlab_q4_k_m.gguf ^
  --device none ^
  -c 4096 ^
  -n 1024 ^
  --temp 0.2 ^
  --no-escape ^
  --no-conversation ^
  --no-display-prompt ^
  --no-perf ^
  -p "<|im_start|>system\n你是数学实验课程的 MATLAB 编程助手。请只输出完整 MATLAB 代码，不要解释。<|im_end|>\n<|im_start|>user\n%QUESTION%<|im_end|>\n<|im_start|>assistant\n"

echo.
pause
