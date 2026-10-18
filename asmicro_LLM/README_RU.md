# asmicro_LLM — память + Ollama proxy на Huananzhi

Сервис слушает `192.168.0.100:8780`, хранит память в SQLite и проксирует Ollama на `127.0.0.1:11434`.

В ветке `test_load` аудио сюда не передаётся: Faster-Whisper работает локально на Acer, через WireGuard приходит уже текст.

```bash
cp .env.example .env
chmod +x install.sh
sudo ./install.sh

curl http://192.168.0.100:8780/health
systemctl status asmicro-llm --no-pager
```

Ollama:

```bash
ollama pull qwen3:4b-instruct
ollama list
```

Диагностика:

```bash
./diagnose_huananzhi.sh qwen3:4b-instruct
```

Контакты: feudor.lab@ya.ru, obzorniky@gmail.com
