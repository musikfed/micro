# Micro 语音助手

架构：**ESP32 → Wi‑Fi → Acer → WireGuard → X79/RTX3060 LLM**。

Acer 本地运行 VAD、`faster-whisper small`（CPU/int8）语音识别和 Silero TTS；通过 VPN 主要只传输**文本**。X79 上的 `asmicro_LLM :8780`负责记忆并代理 Ollama `qwen3:4b-instruct`。监控端口为 `:8765`。最终方案不使用外部 ASR `:8766`。

## 安装
Windows:
```powershell
cd F:\asmicro_PC
.\scripts\setup_windows.ps1
.\scripts\start_windows.ps1
```
X79:
```bash
cd asmicro_LLM
sudo ./install.sh
curl http://192.168.0.100:8780/health
```

## 故障排查
| 现象 | 原因 | 解决 |
|---|---|---|
| ESP32 OFFLINE | :8000/WebSocket | 启动 backend，检查 token |
| ASR 空文本 | 音量/VAD/STT | 查看 RMS 和保存的 WAV |
| 已识别“микро”但 TRIGGER MISS | 唤醒匹配 | 检查 aliases/matcher |
| Ollama OFFLINE 但 PowerShell 可访问 | Windows proxy | 内部 httpx 使用 `trust_env=False` |
| X79 OFFLINE | :8765 未运行 | 启动 monitor |

联系方式：feudor.lab@ya.ru，obzorniky@gmail.com
