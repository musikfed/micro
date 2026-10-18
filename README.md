# Микро — локальный голосовой ассистент ESP32 + Acer + LLM по WireGuard

Ветка **`test_load`** фиксирует рабочую тестовую архитектуру без временных patch-файлов.

## Схема

```text
ESP32-S3 (микрофон INMP441 + MAX98357)
        │ Wi‑Fi, PCM16 16 kHz / audio 24 kHz
        ▼
Acer / asmicro_PC :8000
  ├─ VAD / wake «Микро»
  ├─ faster-whisper small, CPU int8  ← голос → текст локально
  ├─ Silero v5_5_ru, 24 kHz          ← текст → голос локально
  ├─ Web UI / диагностика / OTA
  │
  │ WireGuard: передаётся в основном ТЕКСТ
  ▼
Huananzhi X79 / RTX 3060 / 192.168.0.100
  ├─ asmicro_LLM :8780  ← память + proxy
  ├─ Ollama :11434      ← qwen3:4b-instruct
  └─ monitor :8765      ← CPU/RAM/GPU/VRAM/диск
```

**Порт 8766 и внешний ASR не нужны.** Распознавание речи выполняется на Acer.

## Быстрый запуск

### Acer / Windows

```powershell
cd F:\asmicro_PC
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
.\scripts\start_windows.ps1
```

Открыть: `http://127.0.0.1:8000` или IP Acer в домашней сети.

Основные настройки:

```env
APP_HOST=0.0.0.0
APP_PORT=8000
DEVICE_TOKEN=change-me

OLLAMA_BASE_URL=http://192.168.0.100:8780
OLLAMA_MODEL=qwen3:4b-instruct

STT_ENABLED=true
STT_MODEL=small
STT_DEVICE=cpu
STT_COMPUTE_TYPE=int8
STT_LANGUAGE=ru
STT_CPU_THREADS=4
STT_BEAM_SIZE=1

TTS_ENGINE=silero
TTS_SILERO_MODEL_PATH=data/models/silero/v5_5_ru.pt
TTS_SILERO_SAMPLE_RATE=24000
```

### Huananzhi / Linux

```bash
cd asmicro_LLM
chmod +x install.sh
sudo ./install.sh
curl http://192.168.0.100:8780/health
```

Для монитора:

```bash
cd voice_micro_monitor_agent
chmod +x install.sh
sudo ./install.sh --host 192.168.0.100 --port 8765 --refresh 10
curl http://192.168.0.100:8765/stats
```

## Контрольные тесты

```powershell
# Backend
Invoke-RestMethod http://127.0.0.1:8000/api/status

# Писк/динамик
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/wake-sound/test

# TTS
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/speak -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes('{"text":"Проверка голоса Микро."}'))

# LLM proxy
Invoke-RestMethod http://192.168.0.100:8780/health

# Важно: httpx должен обходить системный proxy для VPN
cd F:\asmicro_PC
uv run --python 3.12 python -c "import httpx; r=httpx.get('http://192.168.0.100:8780/api/tags',timeout=8,trust_env=False); print(r.status_code)"
```

Голосовой тест: **«Микро, скажи привет»**.

## Частые проблемы

| Симптом | Причина | Решение |
|---|---|---|
| ESP32 OFFLINE | backend :8000 не запущен / token или адрес | запустить backend, проверить WebSocket и DEVICE_TOKEN |
| ASR «ничего не распознано» | тихий звук/VAD/пустая фраза | Diagnostics → RMS/VAD, проверить last_mic WAV |
| ASR пишет «Привет, микро!», но TRIGGER MISS | wake matcher/aliases | wake_word=микро, aliases; matcher должен искать имя внутри всей фразы |
| OLLAMA OFFLINE, но PowerShell curl работает | Python httpx использует Windows proxy | для внутренних VPN-клиентов использовать `trust_env=False` |
| X79 OFFLINE | monitor :8765 не запущен | поднять monitor service; на диалог не влияет |
| TTS тест работает, голосового ответа нет | запрос не прошёл wake gate / LLM turn | смотреть «Голосовой лог» и backend stdout |
| первый запуск STT долго | скачивается faster-whisper small | дождаться первой загрузки; дальше модель локальная |
| Silero model missing | нет `v5_5_ru.pt` | положить модель в `data/models/silero/` |
| UI показывает старые подписи | frontend не пересобран / cache | `npm run build`, затем Ctrl+F5 |

Полная диагностика: [docs/DIAGNOSTICS_RU.md](docs/DIAGNOSTICS_RU.md).

Документация: [English](docs/README.en.md) · [한국어](docs/README.ko.md) · [中文](docs/README.zh.md) · [Қазақша](docs/README.kk.md) · [日本語](docs/README.ja.md)

## Контакты

- feudor.lab@ya.ru
- obzorniky@gmail.com
