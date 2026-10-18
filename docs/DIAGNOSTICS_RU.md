# Диагностика — Микро

Проверяем цепочку по одному звену, не меняя ESP32 без необходимости.

## 1. ESP32 ↔ Acer

В UI должны быть:
- ESP32 ONLINE;
- MIC packets/bytes растут;
- AC RMS меняется при речи;
- speaker test слышен.

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/wake-sound/test
```

## 2. Локальный ASR Acer

```powershell
cd F:\asmicro_PC
uv run --python 3.12 python scripts\test_local_stt.py
```

Ожидается непустой `text`. Для реального голоса проверять в UI вкладку «Голосовой лог».

## 3. Wake

Контрольные фразы:
- «Микро, скажи привет»
- «Привет, Микро»
- «Эй Микро, как дела?»

Если ASR распознал «микро», но стоит `TRIGGER MISS`, проблема только в wake matcher/aliases, не в LLM.

## 4. VPN + LLM

```powershell
Test-NetConnection 192.168.0.100 -Port 8780
Invoke-RestMethod http://192.168.0.100:8780/health
uv run --python 3.12 python -c "import httpx; r=httpx.get('http://192.168.0.100:8780/api/tags',timeout=8,trust_env=False); print(r.status_code); print(r.text[:300])"
```

Если PowerShell работает, а обычный httpx без `trust_env=False` зависает и traceback содержит `http_proxy.py`, виноват системный proxy Windows.

## 5. Реальный запрос LLM

```powershell
$body = @{text="Ответь одной фразой: тест связи."; mode="normal"; speak=$false} | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/chat -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

## 6. TTS → ESP32

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/speak -ContentType "application/json; charset=utf-8" -Body ([Text.Encoding]::UTF8.GetBytes('{"text":"Проверка динамика. Я на связи."}'))
```

## 7. X79 monitor

```powershell
Test-NetConnection 192.168.0.100 -Port 8765
Invoke-RestMethod http://192.168.0.100:8765/stats
```

На Huananzhi:
```bash
nvidia-smi
curl http://192.168.0.100:8780/health
curl http://192.168.0.100:8765/stats
systemctl status asmicro-llm --no-pager
```

## Быстрая локализация

| До какого этапа дошло | Что это доказывает |
|---|---|
| RMS меняется | ESP32 mic → Acer работает |
| ASR дал текст | faster-whisper работает |
| TRIGGER OK | wake работает |
| OLLAMA ONLINE | Acer → VPN → asmicro_LLM → Ollama работает |
| чат отвечает | LLM pipeline исправен |
| /api/speak слышен | Silero → ESP32 speaker исправен |
| monitor online | телеметрия X79 исправна |
