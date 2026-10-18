# Micro 音声アシスタント

構成: **ESP32 → Wi‑Fi → Acer → WireGuard → X79/RTX3060 LLM**。

Acer 側で VAD、`faster-whisper small`（CPU/int8）の音声認識、Silero TTS をローカル実行します。VPN では主に**テキストだけ**を送ります。X79 の `asmicro_LLM :8780` がメモリを付加し、Ollama `qwen3:4b-instruct` を呼び出します。監視は `:8765`。外部 ASR `:8766` は最終構成では使いません。

## インストール
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

## トラブルシュート
| 症状 | 原因 | 対処 |
|---|---|---|
| ESP32 OFFLINE | :8000/WebSocket | backend と token を確認 |
| ASR が空 | 音量/VAD/STT | RMS と WAV を確認 |
| “микро” 認識後も TRIGGER MISS | wake matcher | aliases/matcher を確認 |
| Ollama OFFLINE だが PowerShell は成功 | Windows proxy | 内部 httpx に `trust_env=False` |
| X79 OFFLINE | :8765 停止 | monitor service を開始 |

連絡先: feudor.lab@ya.ru, obzorniky@gmail.com
