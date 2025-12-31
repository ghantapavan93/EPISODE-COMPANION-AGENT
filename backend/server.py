from typing import Optional
from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from database import get_db
from orchestrator import Orchestrator
from backend.schemas import CompanionQueryRequest, CompanionQueryResponse

app = FastAPI(
    title="Kochi Episode Companion API",
    version="0.1.0",
    description="Episode-aware companion agent for Kochi.ai Interactive Mode."
)

# Mount static files
# Assuming server.py is in backend/ and static/ is in root
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
print(f"DEBUG: static_dir calculated as: {static_dir}")
print(f"DEBUG: static_dir exists: {os.path.exists(static_dir)}")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    print("WARNING: static directory not found, skipping mount.")

orchestrator = Orchestrator()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/companion/query", response_model=CompanionQueryResponse)
def companion_query(
    payload: CompanionQueryRequest,
    db: Session = Depends(get_db)
):
    raw = orchestrator.route_request(
        user_id=payload.user_id,
        text=payload.message,
        episode_id=payload.episode_id,
        mode=payload.mode,
        debug=payload.debug,
        db=db,
    )
    return raw


@app.post("/companion/speech", response_model=CompanionQueryResponse)
async def companion_speech_query(
    user_id: str,
    episode_id: Optional[str] = None,
    mode: Optional[str] = None,
    debug: bool = False,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Stub endpoint for future tap-to-speak integration.

    Intended future flow:
    1. Receive audio from client (microphone recording).
    2. Run speech-to-text (STT) to produce a text query.
    3. Route that text through the SAME orchestrator / companion agent.
    4. (Optionally) Run text-to-speech (TTS) on the answer and return audio.

    For now, we use a placeholder transcript to demonstrate the wiring.
    """
    # TODO: integrate real STT (e.g. OpenAI Whisper, local model, etc.)
    fake_transcript = "This is a placeholder transcript derived from your audio."

    raw = orchestrator.route_request(
        user_id=user_id,
        text=fake_transcript,
        episode_id=episode_id,
        mode=mode,
        debug=debug,
        db=db,
    )
    return raw

@app.get("/")
async def read_root():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(static_dir, "index.html"))
