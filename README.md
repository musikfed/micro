# Микро / Micro — distributed voice assistant (`test_load`)

**Languages:** [Русский](README_RU.md) · [English](README_EN.md) · [한국어](README_KO.md) · [中文](README_ZH.md) · [Қазақша](README_KK.md) · [日本語](README_JA.md)

Ветка `test_load` фиксирует рабочую трёхзвенную схему без временных patch-файлов:

`ESP32 -> Wi‑Fi -> Acer -> WireGuard/VPN -> Huananzhi RTX 3060 / LLM`

- ESP32: микрофон INMP441 + динамик MAX98357, WebSocket-аудио.
- Acer: FastAPI/UI, VAD, **локальный Faster-Whisper**, wake «Микро», **локальный Silero TTS**.
- Huananzhi `192.168.0.100`: `asmicro_LLM :8780` + память, Ollama `:11434`, монитор X79/GPU `:8765`.
- Через VPN к LLM передаётся **текст**, а не микрофонный PCM.
- Порт `8766` в этой ветке **не используется**.

Контакты / Contacts: **feudor.lab@ya.ru**, **obzorniky@gmail.com**

См. [скриншоты диагностики и проблем](docs/SCREENSHOTS.md) и [таблицу проблем/решений](docs/TROUBLESHOOTING_RU.md).
