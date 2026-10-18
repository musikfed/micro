from __future__ import annotations

import asyncio
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .config import ROOT


@dataclass
class ASRResult:
    text: str = ""
    language: str = "ru"
    error: str = ""


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default


class LocalWhisperASR:
    """Local STT on Acer.

    The compatibility object is still exported as qwen_asr because older
    dialogue/main code imports that name. No request is made to port 8766.
    """

    def __init__(self) -> None:
        self.enabled = _env_bool("STT_ENABLED", True)
        self.model = os.getenv("STT_MODEL", "small").strip() or "small"
        self.device = os.getenv("STT_DEVICE", "cpu").strip() or "cpu"
        self.compute_type = os.getenv("STT_COMPUTE_TYPE", "int8").strip() or "int8"
        self.language = os.getenv("STT_LANGUAGE", "ru").strip() or "ru"
        self.cpu_threads = max(1, _env_int("STT_CPU_THREADS", 4))
        self.beam_size = max(1, _env_int("STT_BEAM_SIZE", 1))
        self.download_root = ROOT / "data" / "models" / "faster-whisper"

        self._model = None
        self._load_lock = asyncio.Lock()
        self.reachable = self.enabled
        self.model_loaded = False
        self.loading = False
        self.last_error = ""
        self.last_text = ""
        self.last_latency_ms = 0

    async def close(self) -> None:
        return None

    def _load_sync(self):
        from faster_whisper import WhisperModel
        self.download_root.mkdir(parents=True, exist_ok=True)
        return WhisperModel(
            self.model,
            device=self.device,
            compute_type=self.compute_type,
            cpu_threads=self.cpu_threads,
            num_workers=1,
            download_root=str(self.download_root),
        )

    async def warmup(self) -> bool:
        if not self.enabled:
            self.reachable = False
            self.last_error = "Local STT disabled"
            return False
        if self._model is not None:
            self.model_loaded = True
            self.reachable = True
            return True
        async with self._load_lock:
            if self._model is not None:
                return True
            self.loading = True
            self.last_error = ""
            try:
                self._model = await asyncio.to_thread(self._load_sync)
                self.model_loaded = True
                self.reachable = True
                return True
            except Exception as exc:
                self._model = None
                self.model_loaded = False
                self.reachable = False
                self.last_error = str(exc)
                return False
            finally:
                self.loading = False

    def _transcribe_sync(self, pcm: bytes, sample_rate: int) -> tuple[str, str]:
        if self._model is None:
            raise RuntimeError("Local faster-whisper model is not loaded")
        if sample_rate != 16000:
            raise ValueError(f"Expected PCM16 mono 16000 Hz, got {sample_rate} Hz")
        audio = np.frombuffer(pcm, dtype=np.int16)
        if audio.size == 0:
            return "", self.language
        waveform = audio.astype(np.float32) / 32768.0
        segments, info = self._model.transcribe(
            waveform,
            language=self.language or None,
            beam_size=self.beam_size,
            best_of=1,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=False,
            without_timestamps=True,
        )
        text = " ".join(
            seg.text.strip() for seg in segments
            if getattr(seg, "text", "").strip()
        ).strip()
        return text, str(getattr(info, "language", "") or self.language or "ru")

    async def transcribe(self, pcm: bytes, sample_rate: int = 16000) -> ASRResult:
        started = time.perf_counter()
        try:
            if not await self.warmup():
                return ASRResult(error=self.last_error or "Local ASR failed to load")
            text, lang = await asyncio.to_thread(self._transcribe_sync, pcm, sample_rate)
            self.last_latency_ms = int((time.perf_counter() - started) * 1000)
            self.last_text = text
            self.last_error = "" if text else "Local ASR returned empty text"
            self.reachable = True
            return ASRResult(text=text, language=lang, error=self.last_error)
        except Exception as exc:
            self.last_latency_ms = int((time.perf_counter() - started) * 1000)
            self.last_text = ""
            self.last_error = str(exc)
            self.reachable = False
            return ASRResult(error=self.last_error)

    def public(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "reachable": self.reachable,
            "model_loaded": self.model_loaded,
            "loading": self.loading,
            "engine": "faster-whisper-local",
            "model": self.model,
            "device": self.device,
            "compute_type": self.compute_type,
            "url": "local://acer/faster-whisper",
            "last_text": self.last_text,
            "last_error": self.last_error,
            "last_latency_ms": self.last_latency_ms,
        }

    async def status(self) -> dict[str, Any]:
        return self.public()


qwen_asr = LocalWhisperASR()
