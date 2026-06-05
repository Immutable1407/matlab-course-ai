# llama.cpp Windows CPU 包替换说明

当前下载的旧版测试包：

- `llama-b8982-bin-win-cpu-x64.zip`
- 来源：官方 `ggml-org/llama.cpp` GitHub release `b8982`
- 发布时间：2026-04-30
- 用途：替换当前 `b9521` CPU x64 包，测试旧机器兼容性。

## 替换步骤

1. 在目标 Windows 电脑上备份当前目录：

   ```text
   Open Mat/app
   ```

2. 解压 `llama-b8982-bin-win-cpu-x64.zip`。

3. 把解压出来的所有 `.exe` 和 `.dll` 复制到：

   ```text
   Open Mat/app
   ```

   覆盖同名文件。

4. 先测试：

   ```bat
   app\llama-cli.exe -h
   ```

5. 如果 `-h` 能输出帮助，再测试无 Python 入口：

   ```bat
   app\ask_direct_no_python.bat
   ```

## 如果仍然没有任何输出

优先检查 VC++ 运行库：

```bat
dir C:\Windows\System32\vcruntime140.dll
dir C:\Windows\System32\vcruntime140_1.dll
```

如果不存在，安装 Microsoft Visual C++ Redistributable 2015-2022 x64。

## 注意

`ask_code.bat` 需要 Python；目标机没有 Python 时，请用：

```text
app/ask_direct_no_python.bat
```

这个入口不做题库检索，只直接调用 GGUF 模型生成 MATLAB 代码。
