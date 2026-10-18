# Micro — 安装与工作架构 (`test_load`)

[Русский](README_RU.md) · [English](README_EN.md) · [한국어](README_KO.md) · [Қазақша](README_KK.md) · [日本語](README_JA.md)

## 已固定的工作方案

`test_load` 分支保存的是已经整合好的代码，不需要再应用临时 patch。

```text
ESP32 --Wi‑Fi--> Acer / asmicro_PC :8000
                  ├─ VAD
                  ├─ 本地 Faster-Whisper small / CPU / int8（语音→文本）
                  ├─ 唤醒词 «Микро»
                  └─ 本地 Silero TTS 24 kHz（文本→语音）
                         │
                         └─ WireGuard：只传文本/HTTP
                              ↓
                    Huananzhi 192.168.0.100
                      ├─ asmicro_LLM :8780（记忆代理）
                      ├─ Ollama :11434 / qwen3:4b-instruct
                      └─ X79 monitor :8765
```

本分支不使用远端 ASR，`8766` 端口已不需要。应用端口无需映射到公网；如需公网入口，只暴露 WireGuard endpoint。

## Acer / Windows 安装

需要 Python 3.12、`uv`、Node.js/npm。

```powershell
git clone -b test_load https://github.com/musikfed/micro.git
cd micro\asmicro_PC
Copy-Item .env.example .env
# DEVICE_TOKEN 必须与 ESP32 中已经保存的 token 一致。

Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
```

Silero 模型不提交到 git。把可用的 `v5_5_ru.pt` 放到：

`asmicro_PC\data\models\silero\v5_5_ru.pt`

Faster-Whisper `small` 会在 Acer 首次使用时本地下载。

```powershell
.\scripts\start_windows.ps1
```

## Huananzhi / Linux 安装

```bash
ollama pull qwen3:4b-instruct

cd ~/micro/asmicro_LLM
cp .env.example .env
chmod +x install.sh
sudo ./install.sh
curl http://192.168.0.100:8780/health

cd ~/micro/x79_monitor
chmod +x install.sh
sudo ./install.sh --host 192.168.0.100 --port 8765 --refresh 10
curl http://192.168.0.100:8765/stats
```

## 测试与诊断

Acer：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/wake-sound/test
.\scripts\diagnose_windows.ps1
uv run --python 3.12 python scripts\test_local_stt.py
```

Huananzhi：

```bash
./diagnose_huananzhi.sh qwen3:4b-instruct
nvidia-smi
```

最终语音测试：**«Микро, скажи привет»**。

## 联系方式

- feudor.lab@ya.ru
- obzorniky@gmail.com

[故障排查](docs/TROUBLESHOOTING_ZH.md) · [问题与诊断截图](docs/SCREENSHOTS.md)
