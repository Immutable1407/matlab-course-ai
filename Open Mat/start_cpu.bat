@echo off
cd /d "%~dp0"

if not exist "app_koboldcpp\koboldcpp.exe" goto noexe
if not exist "gguf\qwen_matlab_q4_k_m.gguf" goto nomodel

echo Starting KoboldCpp CPU mode...
echo Open browser: http://localhost:5001
echo Keep this window open while using the local AI.
echo.

app_koboldcpp\koboldcpp.exe --model "gguf\qwen_matlab_q4_k_m.gguf" --contextsize 2048 --port 5001 --skiplauncher --noblas

echo.
echo KoboldCpp exited with code %ERRORLEVEL%
pause
exit /b

:noexe
echo ERROR: app_koboldcpp\koboldcpp.exe not found
pause
exit /b 1

:nomodel
echo ERROR: gguf\qwen_matlab_q4_k_m.gguf not found
pause
exit /b 1
