# Screenshots / Скриншоты

В ходе отладки были зафиксированы состояния:
1. ESP32 online, Ollama/X79 offline.
2. Локальный ASR начал распознавать речь.
3. Ollama online после обхода Windows HTTP proxy для VPN-клиентов.
4. X79 monitor online с CPU/RAM/GPU/VRAM/disk.
5. Voice log с кейсом `TRIGGER MISS` при корректном ASR “Привет, микро!”.
6. Diagnostics: transport, Audio/VAD, speaker test.
7. Scenarios: wake aliases, thresholds, model.
8. Dialog: Silero voice selector and OTA.

Бинарные PNG из тестовой сессии должны храниться здесь с обезличенными секретами. Не публикуйте `.env` и реальные DEVICE_TOKEN.
