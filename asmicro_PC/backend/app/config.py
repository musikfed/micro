from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    app_host: str = '0.0.0.0'
    app_port: int = 8000
    device_token: str = 'change-me-please'

    ollama_base_url: str = 'http://192.168.0.100:11434'
    ollama_model: str = 'hf.co/bartowski/NousResearch_Hermes-4-14B-GGUF:Q4_K_M'
    ollama_timeout_s: float = 90.0
    ollama_num_ctx: int = 4096
    ollama_tokens_initiative: int = 100
    ollama_tokens_normal: int = 420
    ollama_tokens_explain: int = 700

    weather_enabled: bool = True
    weather_location: str = ''
    web_search_enabled: bool = True
    web_search_results: int = 3
    debug_enabled: bool = False

    x79_monitor_enabled: bool = True
    x79_monitor_url: str = 'http://192.168.0.100:8765/stats'
    x79_monitor_poll_s: float = 3.0

    # Speech recognition is local on Acer. Only recognized text crosses WireGuard.
    stt_enabled: bool = True
    stt_model: str = 'small'
    stt_device: str = 'cpu'
    stt_compute_type: str = 'int8'
    stt_language: str = 'ru'
    stt_cpu_threads: int = 4
    stt_beam_size: int = 1
    stt_download_root: Path = ROOT / 'data' / 'models' / 'faster-whisper'

    # Old Vosk/Qwen-ASR variables in a legacy .env are ignored (extra='ignore').

    # Silero TTS runs locally on Acer CPU and returns PCM in memory.
    tts_engine: str = 'silero'
    tts_target_rate: int = 24000
    tts_silero_model_path: Path = ROOT / 'data' / 'models' / 'silero' / 'v5_5_ru.pt'
    tts_silero_speaker: str = 'xenia'
    tts_silero_sample_rate: int = 24000
    tts_cpu_threads: int = 4
    tts_sapi_fallback: bool = False
    tts_rate_delta: int = 0
    tts_voice_hint: str = ''

    proactive_enabled: bool = True
    presence_max_mm: int = 1600
    near_max_mm: int = 900
    near_hold_s: float = 2.5
    initiative_cooldown_s: float = 300.0
    initiative_max_per_hour: int = 4
    reengage_after_s: float = 420.0

    vad_auto_threshold: bool = True
    vad_noise_multiplier: float = 2.15
    vad_rms_threshold: int = 6500
    vad_start_frames: int = 2
    vad_end_silence_ms: int = 550
    vad_min_speech_ms: int = 260
    vad_max_speech_ms: int = 12000
    vad_preroll_ms: int = 1200

    wake_enabled: bool = True
    wake_word: str = 'микро'
    wake_aliases: str = 'микро,эй микро,микра'
    wake_ack: str = 'Да?'
    wake_listen_s: float = 10.0
    wake_followup_s: float = 30.0
    wake_probe_enabled: bool = True
    wake_probe_min_speech_ms: int = 650
    wake_probe_interval_ms: int = 850
    wake_probe_window_ms: int = 2800

    persona_mode: str = 'friend_assistant'
    ask_followup_questions: bool = True
    dialogue_turn_timeout_s: float = 90.0

    history_messages: int = 24
    memory_recall_items: int = 4
    memory_scan_lines: int = 1200
    conversation_path: Path = ROOT / 'data' / 'conversation.jsonl'
    runtime_path: Path = ROOT / 'data' / 'runtime_settings.json'
    frontend_dist: Path = ROOT / 'frontend' / 'dist'

    firmware_dir: Path = ROOT / 'data' / 'firmware'
    firmware_bin_name: str = 'voice_micro_latest.bin'
    firmware_manifest_name: str = 'manifest.json'


settings = Settings()
