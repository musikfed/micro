# Micro — орнату және жұмыс сұлбасы (`test_load`)

[Русский](README_RU.md) · [English](README_EN.md) · [한국어](README_KO.md) · [中文](README_ZH.md) · [日本語](README_JA.md)

## Бекітілген архитектура

`test_load` тармағында уақытша patch емес, бірден біріктірілген жұмыс коды сақталады.

```text
ESP32 --Wi‑Fi--> Acer / asmicro_PC :8000
                  ├─ VAD
                  ├─ жергілікті Faster-Whisper small / CPU / int8 (дауыс→мәтін)
                  ├─ «Микро» ояту сөзі
                  └─ жергілікті Silero TTS 24 kHz (мәтін→дауыс)
                         │
                         └─ WireGuard: тек мәтін/HTTP
                              ↓
                    Huananzhi 192.168.0.100
                      ├─ asmicro_LLM :8780 (жад proxy)
                      ├─ Ollama :11434 / qwen3:4b-instruct
                      └─ X79 monitor :8765
```

Бұл тармақта қашықтағы ASR жоқ, `8766` порты қолданылмайды. Қолданба порттарын интернетке ашудың қажеті жоқ; қажет болса тек WireGuard endpoint ашылады.

## Acer / Windows орнату

Қажет: Python 3.12, `uv`, Node.js/npm.

```powershell
git clone -b test_load https://github.com/musikfed/micro.git
cd micro\asmicro_PC
Copy-Item .env.example .env
# DEVICE_TOKEN ESP32-де бұрын сақталған токенмен бірдей болуы керек.

Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_windows.ps1
```

Silero моделі git-те сақталмайды. Жұмыс істейтін `v5_5_ru.pt` файлын мына жерге көшіріңіз:

`asmicro_PC\data\models\silero\v5_5_ru.pt`

Faster-Whisper `small` моделі Acer-де бірінші іске қосылғанда жүктеледі.

```powershell
.\scripts\start_windows.ps1
```

## Huananzhi / Linux орнату

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

## Тест және диагностика

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

Соңғы дауыс тесті: **«Микро, скажи привет»**.

## Байланыс

- feudor.lab@ya.ru
- obzorniky@gmail.com

[Ақауларды шешу](docs/TROUBLESHOOTING_KK.md) · [Скриншоттар](docs/SCREENSHOTS.md)
