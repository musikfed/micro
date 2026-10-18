# Micro — installation and architecture (`test_load`)

[Русский](README_RU.md) · [한국어](README_KO.md) · [中文](README_ZH.md) · [Қазақша](README_KK.md) · [日本語](README_JA.md)

## Frozen working design

`test_load` contains the integrated code, not temporary patch scripts.

```text
ESP32 (Wi‑Fi)
  -> Acer / asmicro_PC :8000
       -> VAD
       -> local Faster-Whisper small, CPU/int8 (speech -> text)
       -> wake word "Микро"
       -> local Silero TTS 24 kHz
       -> WireGuard: text/HTTP only
  -> Huananzhi 192.168.0.100
       -> asmicro_LLM :8780 (memory proxy)
       -> Ollama :11434 / qwen3:4b-instruct
       -> X79 monitor :8765
```

No remote ASR is used; port `8766` is obsolete in this branch. Application ports do not need public port forwarding; only the WireGuard endpoint should be exposed when a public endpoint is required.

## Install on Acer / Windows

Requirements: Python 3.12, `uv`, Node.js/npm.

```powershell
git clone -b test_load https://github.com/musikfed/micro.git
cd micro\asmicro_PC
Copy-Item .env.example .env
# Set DEVICE_TOKEN to the token already configured in the ESP32.

Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
```

Copy the working Silero file to:

`asmicro_PC\data\models\silero\v5_5_ru.pt`

The Faster-Whisper `small` model is downloaded locally on Acer on first use. Start:

```powershell
.\scripts\start_windows.ps1
```

## Install on Huananzhi / Linux

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

## Tests

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/wake-sound/test
.\scripts\diagnose_windows.ps1
uv run --python 3.12 python scripts\test_local_stt.py
```

Linux:

```bash
./diagnose_huananzhi.sh qwen3:4b-instruct
nvidia-smi
```

Final voice test: **“Микро, скажи привет”**.

## Contacts

- feudor.lab@ya.ru
- obzorniky@gmail.com

See [troubleshooting](docs/TROUBLESHOOTING_EN.md) and [debug screenshots](docs/SCREENSHOTS.md).
