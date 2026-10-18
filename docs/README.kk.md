# Micro дауыстық көмекшісі

Сұлба: **ESP32 → Wi‑Fi → Acer → WireGuard → X79/RTX3060 LLM**.

Acer-де VAD, `faster-whisper small` (CPU/int8) сөйлеуді мәтінге айналдыру және Silero TTS жергілікті жұмыс істейді. VPN арқылы негізінен **мәтін** ғана өтеді. X79-де `asmicro_LLM :8780` жадты қосып, Ollama `qwen3:4b-instruct` моделіне сұрау жібереді. Монитор `:8765`. Сыртқы ASR `:8766` қолданылмайды.

## Орнату
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

## Ақаулар
| Белгі | Себеп | Шешім |
|---|---|---|
| ESP32 OFFLINE | :8000/WebSocket | backend пен token тексеру |
| ASR бос | дыбыс/VAD/STT | RMS және WAV тексеру |
| “микро” танылды, бірақ TRIGGER MISS | wake matcher | aliases/matcher тексеру |
| Ollama OFFLINE, PowerShell жұмыс істейді | Windows proxy | ішкі httpx үшін `trust_env=False` |
| X79 OFFLINE | :8765 тоқтаған | monitor қызметін іске қосу |

Байланыс: feudor.lab@ya.ru, obzorniky@gmail.com
