# Micro 음성 비서

구성: **ESP32 → Wi‑Fi → Acer → WireGuard → X79/RTX3060 LLM**.

Acer에서 VAD, `faster-whisper small`(CPU/int8) STT, Silero TTS를 로컬로 실행합니다. VPN으로는 주로 **텍스트만** 전송합니다. X79의 `asmicro_LLM :8780`이 메모리를 주입하고 Ollama `qwen3:4b-instruct`를 호출합니다. 모니터링은 `:8765`입니다. 외부 ASR `:8766`은 사용하지 않습니다.

## 설치
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

## 문제 해결
| 증상 | 원인 | 해결 |
|---|---|---|
| ESP32 OFFLINE | :8000/WebSocket 문제 | backend와 token 확인 |
| ASR 빈 결과 | 음량/VAD/STT 문제 | RMS와 WAV 확인 |
| “микро” 인식 후 TRIGGER MISS | wake matcher | alias/matcher 확인 |
| Ollama OFFLINE, curl은 정상 | Windows proxy | 내부 httpx에 `trust_env=False` |
| X79 OFFLINE | :8765 monitor 중지 | monitor service 시작 |

연락처: feudor.lab@ya.ru, obzorniky@gmail.com
