# Микро — документация на русском

Рабочая схема ветки `test_load`:

```text
ESP32-S3
   │ Wi‑Fi
   ▼
Acer / asmicro_PC :8000
   ├─ VAD
   ├─ faster-whisper small CPU/int8 (голос → текст)
   ├─ wake «Микро»
   └─ Silero v5_5_ru 24 kHz (текст → голос)
          │
          │ WireGuard — в LLM уходит текст
          ▼
Huananzhi X79 / RTX3060 / 192.168.0.100
   ├─ asmicro_LLM :8780
   ├─ Ollama :11434 / qwen3:4b-instruct
   └─ monitor :8765
```

Внешний ASR `:8766` в финальной схеме не используется.

## Установка Acer
```powershell
cd F:\asmicro_PC
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
.\scripts\start_windows.ps1
```

## Установка X79
```bash
cd asmicro_LLM
chmod +x install.sh
sudo ./install.sh
curl http://192.168.0.100:8780/health
```

Monitor:
```bash
cd voice_micro_monitor_agent
chmod +x install.sh
sudo ./install.sh --host 192.168.0.100 --port 8765 --refresh 10
```

## Проверка
```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod http://192.168.0.100:8780/health
Invoke-RestMethod http://192.168.0.100:8765/stats
.\scripts\diagnose_windows.ps1
.\scripts\test_voice_pipeline.ps1
```

Ключевой голосовой тест: **«Микро, скажи привет»**.

Подробная таблица ошибок: [DIAGNOSTICS_RU.md](DIAGNOSTICS_RU.md).

Контакты: feudor.lab@ya.ru · obzorniky@gmail.com
