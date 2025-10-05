"""ASGI application exposing FlyzexBot storage insights."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from flyzexbot.config import Settings
from flyzexbot.services.security import EncryptionManager
from flyzexbot.services.storage import Application, Storage

BASE_DIR = Path(__file__).resolve().parent
INDEX_PATH = BASE_DIR / "index.html"
CONFIG_PATH = Path("config/settings.yaml")
EXAMPLE_CONFIG_PATH = Path("config/settings.example.yaml")


def _resolve_config_path() -> Path:
    if CONFIG_PATH.exists():
        return CONFIG_PATH
    return EXAMPLE_CONFIG_PATH


def _application_to_dict(application: Application) -> Dict[str, Any]:
    return {
        "user_id": application.user_id,
        "full_name": application.full_name,
        "answer": application.answer,
        "created_at": application.created_at,
        "language_code": application.language_code,
        "responses": [vars(response) for response in getattr(application, "responses", [])],
    }


def _normalize_user_id(value: str) -> int | str:
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings.load(_resolve_config_path())
    encryption = EncryptionManager(settings.get_secret_key())
    storage = Storage(settings.storage.path, encryption)
    await storage.load()

    app.state.settings = settings
    app.state.storage = storage

    try:
        yield
    finally:
        await storage.save()


app = FastAPI(title="FlyzexBot WebApp", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


async def get_storage(request: Request) -> Storage:
    return request.app.state.storage  # type: ignore[return-value]


async def get_settings(request: Request) -> Settings:
    return request.app.state.settings  # type: ignore[return-value]


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return INDEX_PATH.read_text(encoding="utf-8")


@app.get("/api/applications/pending")
async def pending_applications(storage: Storage = Depends(get_storage)) -> Dict[str, Any]:
    applications = [_application_to_dict(app) for app in storage.get_pending_applications()]
    return {"total": len(applications), "applications": applications}


@app.get("/api/xp")
async def xp_leaderboard(
    chat_id: int = Query(..., description="Target chat identifier for the leaderboard."),
    limit: int | None = Query(None, ge=1, description="Maximum number of users to return."),
    storage: Storage = Depends(get_storage),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    effective_limit = limit or settings.xp.leaderboard_size
    leaderboard = [
        {"user_id": _normalize_user_id(user_id), "score": score}
        for user_id, score in storage.get_xp_leaderboard(chat_id, effective_limit)
    ]
    return {"chat_id": chat_id, "limit": effective_limit, "leaderboard": leaderboard}


@app.get("/api/cups")
async def cups(
    chat_id: int = Query(..., description="Target chat identifier for the cup history."),
    limit: int | None = Query(None, ge=1, description="Maximum number of cups to return."),
    storage: Storage = Depends(get_storage),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    effective_limit = limit or settings.cups.leaderboard_size
    cups_payload: List[Dict[str, Any]] = storage.get_cups(chat_id, effective_limit)
    return {"chat_id": chat_id, "limit": effective_limit, "cups": cups_payload}


@app.get("/api/applications/insights")
async def application_insights(storage: Storage = Depends(get_storage)) -> Dict[str, Any]:
    stats_getter = getattr(storage, "get_application_statistics", None)
    if callable(stats_getter):
        return stats_getter()
    return {
        "pending": 0,
        "status_counts": {},
        "languages": {},
        "total": 0,
        "average_pending_answer_length": 0.0,
        "recent_updates": [],
    }


__all__ = ["app"]
