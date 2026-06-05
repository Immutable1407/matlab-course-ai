@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0\.."

if not exist "gguf\qwen_matlab_q4_k_m.gguf" (
  echo [错误] 找不到模型文件：gguf\qwen_matlab_q4_k_m.gguf
  pause
  exit /b 1
)

if not exist "runtime\final_examples.json" (
  echo [错误] 找不到检索库：runtime\final_examples.json
  pause
  exit /b 1
)

if not exist "app\llama-cli.exe" (
  echo [错误] 找不到推理程序：app\llama-cli.exe
  echo 请把 Windows 版 llama-cli.exe 以及需要的 DLL 放到 app 目录。
  pause
  exit /b 1
)

where python >nul 2>nul
if %errorlevel% equ 0 (
  python app\ask_code.py
) else (
  where py >nul 2>nul
  if %errorlevel% equ 0 (
    py -3 app\ask_code.py
  ) else (
    echo [错误] 没有找到 python 或 py。请先安装 Python 3.10/3.11。
    pause
    exit /b 1
  )
)
pause
