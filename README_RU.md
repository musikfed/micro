# Микро — установка и схема работы (`test_load`)

[English](README_EN.md) · [한국어](README_KO.md) · [中文](README_ZH.md) · [Қазақша](README_KK.md) · [日本語](README_JA.md)

## Что зафиксировано

Это рабочая конфигурация без временных патчей. ESP32 не требуется перепрошивать, если она уже знает Wi‑Fi, IP Acer, порт `8000` и `DEVICE_TOKEN`.

```text
ESP32 (192.168.1.41)
  │ Wi‑Fi: PCM16/16 kHz + speaker PCM24 kHz
  ▼
Acer / asmicro_PC (например 192.168.1.88:8000)
  ├─ FastAPI + Web UI
  ├─ VAD
  ├─ Faster-Whisper small / CPU / int8  ← голос → текст
  ├─ wake «Микро»
  └─ Silero v5_5_ru / 24 kHz            ← текст → голос
           │
           │ WireGuard: только текст/HTTP
           ▼
Huananzhi / RTX 3060 (192.168.0.100)
  ├─ asmicro_LLM :8780  ← memory proxy
  ├─ Ollama :11434
  │    └─ qwen3:4b-instruct
  └─ X79 monitor :8765
```

Если VPN имеет публичный endpoint, наружу нужен только WireGuard. `8780`, `8765` и `11434` не нужно пробрасывать в интернет.

## Структура репозитория

- `asmicro_PC/` — Acer/Windows: backend, UI, local STT, TTS, ESP32 transport.
- `asmicro_LLM/` — Huananzhi/Linux: memory proxy перед Ollama.
- `x79_monitor/` — CPU/RAM/GPU/VRAM telemetry.
- `asmicro_PC/firmware/` — исходник ESP32-S3 для справки.
- `docs/screenshots/` — реальные скриншоты отладки.
- `docs/TROUBLESHOOTING_RU.md` — таблица «симптом → причина → решение».

## Acer / Windows

Требования: Python 3.12, `uv`, Node.js/npm для сборки UI.

```powershell
git clone -b test_load https://github.com/musikfed/micro.git
cd micro\asmicro_PC

Copy-Item .env.example .env
# В .env укажи тот DEVICE_TOKEN, который уже записан в ESP32.

Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
```

Silero-файл не хранится в git. Положи рабочий `v5_5_ru.pt` сюда:

```text
asmicro_PC\data\models\silero\v5_5_ru.pt
```

Faster-Whisper `small` скачивается на Acer при первом запуске в:

```text
asmicro_PC\data\models\faster-whisper\
```

Запуск:

```powershell
.\scripts\start_windows.ps1
```

UI: `http://127.0.0.1:8000` или `http://<IP-Acer>:8000`.

## Huananzhi / Linux

Сначала Ollama и модель:

```bash
ollama pull qwen3:4b-instruct
ollama list
```

Memory/LLM proxy:

```bash
cd ~/micro/asmicro_LLM
cp .env.example .env
chmod +x install.sh
sudo ./install.sh

curl http://192.168.0.100:8780/health
systemctl status asmicro-llm --no-pager
```

Монитор X79/GPU:

```bash
cd ~/micro/x79_monitor
chmod +x install.sh
sudo ./install.sh --host 192.168.0.100 --port 8765 --refresh 10
curl http://192.168.0.100:8765/stats
```

## Быстрые проверки

На Acer:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status

# Писк ESP32:
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/wake-sound/test

# Тест речи:
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/speak `
  -ContentType "application/json; charset=utf-8" `
  -Body ([Text.Encoding]::UTF8.GetBytes('{"text":"Проверка. Микро на связи."}'))

# Полная диагностика:
.\scripts\diagnose_windows.ps1
```

Проверка LLM именно тем же Python/httpx, которым пользуется backend:

```powershell
uv run --python 3.12 python -c "import httpx; r=httpx.get('http://192.168.0.100:8780/api/tags', timeout=8, trust_env=False); print(r.status_code); print(r.text[:500])"
```

Проверка local STT по сохранённому WAV:

```powershell
uv run --python 3.12 python scripts\test_local_stt.py
```

На Huananzhi:

```bash
./diagnose_huananzhi.sh qwen3:4b-instruct
nvidia-smi
```

Финальный голосовой тест: **«Микро, скажи привет»**.

## Контакты

- feudor.lab@ya.ru
- obzorniky@gmail.com

[Проблемы и решения](docs/TROUBLESHOOTING_RU.md) · [Скриншоты](docs/SCREENSHOTS.md)
