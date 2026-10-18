# Micro Voice Assistant

Working topology: **ESP32 → Wi‑Fi → Acer → WireGuard → X79/RTX3060 LLM**.

Acer performs local VAD, `faster-whisper small` speech-to-text (CPU/int8) and Silero TTS. Only text is sent over the VPN to `asmicro_LLM :8780`, which injects memory and proxies Ollama `qwen3:4b-instruct`. X79 telemetry is served on `:8765`. External ASR `:8766` is not used.

## Install

Windows/Acer:
```powershell
cd F:\asmicro_PC
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
.\scripts\start_windows.ps1
```

Linux/X79:
```bash
cd asmicro_LLM
chmod +x install.sh
sudo ./install.sh
curl http://192.168.0.100:8780/health
```

## Key checks

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod http://192.168.0.100:8780/health
uv run --python 3.12 python -c "import httpx; print(httpx.get('http://192.168.0.100:8780/api/tags',timeout=8,trust_env=False).status_code)"
```

Say: **“Микро, скажи привет”**.

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| ESP32 offline | backend/WebSocket unavailable | start :8000, verify token/network |
| ASR empty | low audio/VAD/model issue | inspect RMS and saved WAV |
| transcript contains “микро” but TRIGGER MISS | wake matcher | verify wake aliases and matcher |
| Ollama offline while PowerShell works | Windows proxy used by httpx | use `trust_env=False` for VPN clients |
| X79 offline | monitor :8765 stopped | start monitor service |
| TTS test works but voice turn does not | wake/LLM turn blocked | inspect Voice Log |

Contacts: feudor.lab@ya.ru, obzorniky@gmail.com
