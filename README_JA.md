# Micro — インストールと構成 (`test_load`)

[Русский](README_RU.md) · [English](README_EN.md) · [한국어](README_KO.md) · [中文](README_ZH.md) · [Қазақша](README_KK.md)

## 固定した動作構成

`test_load` ブランチには一時 patch ではなく、統合済みの動作コードを保存します。

```text
ESP32 --Wi‑Fi--> Acer / asmicro_PC :8000
                  ├─ VAD
                  ├─ ローカル Faster-Whisper small / CPU / int8（音声→テキスト）
                  ├─ ウェイクワード «Микро»
                  └─ ローカル Silero TTS 24 kHz（テキスト→音声）
                         │
                         └─ WireGuard：テキスト/HTTPのみ
                              ↓
                    Huananzhi 192.168.0.100
                      ├─ asmicro_LLM :8780（メモリ proxy）
                      ├─ Ollama :11434 / qwen3:4b-instruct
                      └─ X79 monitor :8765
```

このブランチではリモート ASR を使わず、`8766` は不要です。アプリ用ポートをインターネットへ転送する必要はなく、必要な場合は WireGuard endpoint のみ公開します。

## Acer / Windows

必要: Python 3.12、`uv`、Node.js/npm。

```powershell
git clone -b test_load https://github.com/musikfed/micro.git
cd micro\asmicro_PC
Copy-Item .env.example .env
# DEVICE_TOKEN は ESP32 に既に保存されている値と一致させます。

Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
```

Silero モデルは git に含めません。動作確認済みの `v5_5_ru.pt` を以下へ配置します。

`asmicro_PC\data\models\silero\v5_5_ru.pt`

Faster-Whisper `small` は Acer で初回利用時にダウンロードされます。

```powershell
.\scripts\start_windows.ps1
```

## Huananzhi / Linux

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

## テスト・診断

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

最終音声テスト: **«Микро, скажи привет»**。

## 連絡先

- feudor.lab@ya.ru
- obzorniky@gmail.com

[トラブルシューティング](docs/TROUBLESHOOTING_JA.md) · [問題/診断スクリーンショット](docs/SCREENSHOTS.md)
