# Architecture / Архитектура

```mermaid
flowchart LR
  E[ESP32-S3\nINMP441 + MAX98357] <-->|Wi‑Fi PCM / audio| A[Acer asmicro_PC :8000]
  A -->|local| W[faster-whisper\nsmall CPU int8]
  W -->|text| A
  A -->|WireGuard text| M[asmicro_LLM :8780\n192.168.0.100]
  M --> O[Ollama :11434\nqwen3:4b-instruct]
  O --> M
  M -->|text| A
  A -->|local| T[Silero v5_5_ru 24 kHz]
  T -->|audio| E
  X[X79 monitor :8765] --> A
```

Design rule: audio recognition and synthesis stay on Acer; the GPU server receives text and performs memory/LLM work. This minimizes VPN audio traffic and keeps the RTX 3060 focused on inference.

Internal HTTP clients to `192.168.0.0/24` must bypass Windows proxy settings (`httpx(..., trust_env=False)`).
