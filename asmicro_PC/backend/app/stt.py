from __future__ import annotations

from dataclasses import dataclass

from .asr_qwen import qwen_asr


@dataclass
class TranscriptionResult:
    text: str
    language: str = ''
    language_probability: float = 1.0
    no_speech_prob: float = 0.0
    avg_logprob: float = 0.0
    compression_ratio: float = 0.0
    duration_s: float = 0.0


class STTFacade:
    """UI compatibility facade backed by local faster-whisper on Acer."""

    async def transcribe_result(self, pcm: bytes, sample_rate: int = 16000, **_: object) -> TranscriptionResult:
        r = await qwen_asr.transcribe(pcm, sample_rate)
        return TranscriptionResult(
            text=r.text,
            language=r.language,
            duration_s=(len(pcm) / 2) / max(1, sample_rate),
        )

    async def transcribe(self, pcm: bytes, sample_rate: int = 16000) -> str:
        return (await self.transcribe_result(pcm, sample_rate)).text

    @staticmethod
    def acceptable(result: TranscriptionResult, *, wake: bool = False) -> bool:
        return bool(result.text.strip())

    def status(self) -> dict:
        a = qwen_asr.public()
        return {
            'enabled': a.get('enabled', True),
            'loaded': bool(a.get('model_loaded', False)),
            'engine': 'faster-whisper-local',
            'model': a.get('model', 'small'),
            'reachable': a.get('reachable', False),
            'error': a.get('last_error', ''),
            'wake_engine': 'faster-whisper-local',
            'wake_loaded': bool(a.get('model_loaded', False)),
            'wake_error': a.get('last_error', ''),
        }


stt = STTFacade()
