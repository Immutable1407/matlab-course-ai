# Open Mat Local AI

This folder is a minimal KoboldCpp + GGUF local AI package for an old Windows 10 PC.

## Files

- `app_koboldcpp/koboldcpp.exe`
- `gguf/qwen_matlab_q4_k_m.gguf`
- `start_cpu.bat`

## Start

1. Double click `start_cpu.bat`.
2. Wait until the terminal shows:

   ```text
   Load Text Model OK: True
   ```

3. Open this URL in a browser:

   ```text
   http://localhost:5001
   ```

4. Keep the terminal window open while using the local AI.

## If It Fails

Do not close the terminal immediately.

Copy the last 20 lines of the terminal output, especially lines near:

```text
ERROR
Traceback
KoboldCpp exited with code
```

The current startup command is intentionally simple:

```bat
app_koboldcpp\koboldcpp.exe --model "gguf\qwen_matlab_q4_k_m.gguf" --contextsize 2048 --port 5001 --skiplauncher --noblas
```

It avoids Chinese console output, multiline caret continuation, and complex batch syntax.
