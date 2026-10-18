# Micro — 설치 및 구조 (`test_load`)

[Русский](README_RU.md) · [English](README_EN.md) · [中文](README_ZH.md) · [Қазақша](README_KK.md) · [日本語](README_JA.md)

## 고정된 동작 구조

`test_load` 브랜치는 임시 패치가 아니라 통합된 최종 코드입니다.

```text
ESP32 --Wi‑Fi--> Acer / asmicro_PC :8000
                  ├─ VAD
                  ├─ Faster-Whisper small (CPU/int8, 음성→텍스트)
                  ├─ 웨이크 워드 «Микро»
                  └─ Silero TTS 24 kHz
                         │
                         └─ WireGuard: 텍스트/HTTP만 전송
                              ↓
                    Huananzhi 192.168.0.100
                      ├─ asmicro_LLM :8780 (메모리 프록시)
                      ├─ Ollama :11434 / qwen3:4b-instruct
                      └─ X79 monitor :8765
```

원격 ASR은 사용하지 않으며 `8766` 포트는 이 브랜치에서 필요하지 않습니다. 외부에 애플리케이션 포트를 포워딩할 필요가 없고, 필요한 경우 WireGuard endpoint만 공개합니다.

## Acer / Windows 설치

필수: Python 3.12, `uv`, Node.js/npm.

```powershell
git clone -b test_load https://github.com/musikfed/micro.git
cd micro\asmicro_PC
Copy-Item .env.example .env
# DEVICE_TOKEN은 ESP32에 이미 저장된 값과 동일하게 설정합니다.

Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
```

Silero 모델은 git에 포함하지 않습니다. 다음 위치에 `v5_5_ru.pt`를 복사합니다:

`asmicro_PC\data\models\silero\v5_5_ru.pt`

Faster-Whisper `small` 모델은 Acer에서 첫 실행 시 다운로드됩니다.

```powershell
.\scripts\start_windows.ps1
```

## Huananzhi / Linux 설치

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

## 테스트/진단

Acer:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/wake-sound/test
.\scripts\diagnose_windows.ps1
uv run --python 3.12 python scripts\test_local_stt.py
```

Huananzhi:

```bash
./diagnose_huananzhi.sh qwen3:4b-instruct
nvidia-smi
```

최종 음성 테스트: **«Микро, скажи привет»**.

## 연락처

- feudor.lab@ya.ru
- obzorniky@gmail.com

[문제 해결 표](docs/TROUBLESHOOTING_KO.md) · [문제/진단 스크린샷](docs/SCREENSHOTS.md)
