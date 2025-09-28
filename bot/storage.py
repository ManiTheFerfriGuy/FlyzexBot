"""Utilities for persisting guild applications."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, Iterable, List, MutableMapping, Optional
from datetime import datetime, timezone


@dataclass(slots=True)
class Application:
    user_id: int
    username: Optional[str]
    full_name: str
    answers: List[Dict[str, str]]
    submitted_at: str = field(
        default_factory=lambda: datetime.now(tz=timezone.utc).isoformat()
    )

    def format_for_admin(self) -> str:
        """Render the application so that admins can review it."""

        header = [
            f"New application from {self.full_name}",
            f"User ID: {self.user_id}",
        ]
        if self.username:
            header.append(f"Username: @{self.username}")
        header.append("")

        qa_lines = [f"Q: {item['question']}\nA: {item['answer']}" for item in self.answers]
        return "\n".join(header + qa_lines)


class ApplicationStore:
    """Simple JSON backed storage for guild applications."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write({"pending": {}, "history": {}})

    # ------------------------------------------------------------------
    # JSON helpers
    # ------------------------------------------------------------------
    def _read(self) -> MutableMapping[str, MutableMapping[str, dict]]:
        with self._path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, payload: MutableMapping[str, MutableMapping[str, dict]]) -> None:
        with self._path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_pending(self, application: Application) -> None:
        data = self._read()
        data.setdefault("pending", {})[str(application.user_id)] = application.__dict__
        self._write(data)

    def pop_pending(self, user_id: int) -> Optional[Application]:
        data = self._read()
        entry = data.setdefault("pending", {}).pop(str(user_id), None)
        if entry is None:
            return None
        application = Application(**entry)
        history = data.setdefault("history", {})
        history[str(user_id)] = entry
        self._write(data)
        return application

    def get_pending(self, user_id: int) -> Optional[Application]:
        data = self._read()
        entry = data.setdefault("pending", {}).get(str(user_id))
        return Application(**entry) if entry else None

    def list_pending(self) -> Iterable[Application]:
        data = self._read()
        for entry in data.setdefault("pending", {}).values():
            yield Application(**entry)

    def get_history(self, user_id: int) -> Optional[Application]:
        data = self._read()
        entry = data.setdefault("history", {}).get(str(user_id))
        return Application(**entry) if entry else None


__all__ = ["Application", "ApplicationStore"]
