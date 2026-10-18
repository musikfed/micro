from __future__ import annotations

import asyncio

from contextlib import asynccontextmanager
import io
import wave

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .audio_ingress import audio_ingress
from .config import settings
from .device import device_hub
from .dialogue import dialogue
from .earcon import wake_earcon
from .firmware import firmware_store
from .history import history
from .models import ChatRequest, FirmwareDeployRequest, RuntimeSettings, SpeakRequest
from .ollama import ollama
from .presence import presence
from .runtime import runtime
from .stt import stt
from .asr_qwen import qwen_asr
from .tts import status as tts_status, warmup as tts_warmup
from .tools import tools
from .ui import ui_hub
from .x79_monitor import x79_monitor
from .voice_log import voice_log


async def snapshot() -> dict:
    presence_state = presence.public()
    presence_state = {**presence_state, 'state': 'ignored', 'sensor_enabled': False}
    return {
        'device': device_hub.public(),
        'presence': presence_state,
        'dialogue': {**dialogue.public(), 'mic_rms': audio_ingress.last_rms},
        'audio': audio_ingress.public(),
        'stt': stt.status(),
        'voice_engine': {
            'wake': {
                'engine': 'faster-whisper-local',
                'loaded': qwen_asr.model_loaded,
                'reachable': qwen_asr.reachable,
                'model': qwen_asr.model,
                'last_text': dialogue.last_wake_candidate,
                'last_error': qwen_asr.last_error,
            },
            'asr': qwen_asr.public(),
            'tts': tts_status(),
        },
        'tools': tools.public(),
        'ollama_runtime': ollama.public(),
        'settings': runtime.public(),
        'history': history.public()[-20:],
        'firmware': firmware_store.manifest(),
        'x79': x79_monitor.public(),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    device_hub.bind(audio_ingress.push, None, ui_hub.notify)
    presence.bind(dialogue.initiative, lambda: dialogue.can_initiate() and not audio_ingress.in_speech, dialogue.last_activity_ago)
    audio_ingress.bind(dialogue.utterance)
    ui_hub.bind(snapshot)
    await x79_monitor.start()
    await tts_warmup()

    # Load/download local Faster-Whisper in the background so FastAPI and
    # ESP32 WebSocket are available immediately.
    asr_task = asyncio.create_task(qwen_asr.warmup())

    # Preload the selected Ollama model on X79 and keep it resident.
    await ollama.warmup()
    try:
        yield
    finally:
        if not asr_task.done():
            asr_task.cancel()
        await x79_monitor.close()
        await qwen_asr.close()
        await ollama.close()
        await tools.close()


app = FastAPI(title='Voice Assistant Micro', version='0.8.6-test_load', lifespan=lifespan)


@app.get('/api/status')
async def api_status():
    data = await snapshot()
    data['ollama'] = await ollama.status()
    data['voice_engine']['asr'] = await qwen_asr.status()
    return data


@app.get('/api/mic-last.wav')
async def api_mic_last_wav():
    pcm = audio_ingress.last_utterance_pcm
    if not pcm:
        raise HTTPException(404, 'No captured microphone utterance yet')

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(pcm)

    return Response(
        content=buf.getvalue(),
        media_type='audio/wav',
        headers={
            'Content-Disposition': 'attachment; filename="voice_micro_last_mic.wav"',
            'Cache-Control': 'no-store',
        },
    )


@app.get('/api/history')
async def api_history():
    return history.public()


@app.get('/api/voice-log')
async def api_voice_log(limit: int = 100):
    return voice_log.public(limit)


@app.post('/api/voice-log/clear')
async def api_voice_log_clear():
    cleared = voice_log.clear()
    return {'ok': True, 'cleared': cleared}


@app.get('/api/settings')
async def api_settings():
    return runtime.public()


@app.post('/api/history/clear')
async def api_history_clear():
    cleared = history.clear()
    dialogue.reset_session()
    audio_ingress.reset()
    await ui_hub.notify()
    return {'ok': True, 'cleared': cleared}


@app.post('/api/settings')
async def api_settings_update(patch: RuntimeSettings):
    result = runtime.update(patch)
    await ui_hub.notify()
    return result


@app.post('/api/chat')
async def api_chat(req: ChatRequest):
    try:
        answer = await dialogue.user_text(req.text, mode=req.mode, speak=req.speak, source='web')
        return {'answer': answer}
    except Exception as exc:
        raise HTTPException(500, str(exc)) from exc


@app.post('/api/wake-sound/test')
async def api_wake_sound_test():
    if not device_hub.state.connected:
        raise HTTPException(409, 'ESP32 is not connected')
    await device_hub.send_audio(wake_earcon(24000), 24000, pace=False)
    return {'ok': True, 'sample_rate': 24000}


@app.post('/api/speak')
async def api_speak(req: SpeakRequest):
    if not device_hub.state.connected:
        raise HTTPException(409, 'ESP32 is not connected')
    await dialogue.speak(req.text)
    return {'ok': True}


@app.get('/api/firmware')
async def api_firmware():
    return firmware_store.manifest()


@app.post('/api/firmware/upload')
async def api_firmware_upload(file: UploadFile = File(...), version: str = Form('custom')):
    if not file.filename or not file.filename.lower().endswith('.bin'):
        raise HTTPException(400, 'Select an ESP32 .bin firmware file')
    try:
        manifest = await firmware_store.save_upload(file, version)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    await ui_hub.notify()
    return manifest


@app.post('/api/firmware/deploy')
async def api_firmware_deploy(req: FirmwareDeployRequest):
    manifest = firmware_store.manifest()
    if not manifest.get('available'):
        raise HTTPException(404, 'No firmware .bin uploaded')
    version = (req.version or manifest.get('version') or 'custom').strip()
    try:
        await device_hub.request_ota(version=version, size=int(manifest['size']), md5=str(manifest['md5']))
    except RuntimeError as exc:
        raise HTTPException(409, str(exc)) from exc
    return {'ok': True, 'version': version}


@app.get('/api/firmware/download')
async def api_firmware_download(x_device_token: str = Header(default='')):
    if x_device_token != settings.device_token:
        raise HTTPException(403, 'Bad device token')
    if not firmware_store.bin_path.exists():
        raise HTTPException(404, 'No firmware')
    return FileResponse(
        firmware_store.bin_path,
        media_type='application/octet-stream',
        filename=settings.firmware_bin_name,
    )


@app.websocket('/ws/device')
async def ws_device(ws: WebSocket):
    token = ws.query_params.get('token', '')
    if token != settings.device_token:
        await ws.close(code=1008)
        return
    await ws.accept()
    await device_hub.attach(ws)
    try:
        while True:
            msg = await ws.receive()
            if msg.get('text') is not None:
                await device_hub.on_text(msg['text'])
            elif msg.get('bytes') is not None:
                await device_hub.on_binary(msg['bytes'])
    except WebSocketDisconnect:
        pass
    except RuntimeError as exc:
        if 'disconnect message' not in str(exc).lower():
            raise
    finally:
        await device_hub.detach(ws)


@app.websocket('/ws/ui')
async def ws_ui(ws: WebSocket):
    await ws.accept()
    await ui_hub.add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ui_hub.remove(ws)


if settings.frontend_dist.exists():
    assets = settings.frontend_dist / 'assets'
    if assets.exists():
        app.mount('/assets', StaticFiles(directory=assets), name='assets')

    @app.get('/{full_path:path}', include_in_schema=False)
    async def spa(full_path: str):
        candidate = settings.frontend_dist / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(settings.frontend_dist / 'index.html')
