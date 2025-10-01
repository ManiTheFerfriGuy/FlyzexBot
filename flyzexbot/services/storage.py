"""Encrypted JSON storage for FlyzexBot."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from aiofiles import open as aioopen

from .security import EncryptionManager


@dataclass
class Application:
    user_id: int
    full_name: str
    answer: str
    created_at: str


@dataclass
class StorageState:
    admins: List[int] = field(default_factory=list)
    applications: Dict[int, Application] = field(default_factory=dict)
    xp: Dict[str, Dict[str, int]] = field(default_factory=dict)
    cups: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "admins": self.admins,
            "applications": {
                str(k): vars(v) for k, v in self.applications.items()
            },
            "xp": self.xp,
            "cups": self.cups,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "StorageState":
        applications = {
            int(k): Application(**v) for k, v in payload.get("applications", {}).items()
        }
        return cls(
            admins=list(payload.get("admins", [])),
            applications=applications,
            xp={k: {user: int(score) for user, score in v.items()} for k, v in payload.get("xp", {}).items()},
            cups={k: list(v) for k, v in payload.get("cups", {}).items()},
        )


class Storage:
    def __init__(self, path: Path, encryption: EncryptionManager) -> None:
        self._path = path
        self._encryption = encryption
        self._lock = asyncio.Lock()
        self._state = StorageState()

    async def load(self) -> None:
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            return

        async with aioopen(self._path, "rb") as file:
            encrypted = await file.read()

        if not encrypted:
            return

        decrypted = await self._encryption.decrypt(encrypted)
        if decrypted is None:
            raise RuntimeError("Failed to decrypt storage file. Check the secret key.")

        payload = json.loads(decrypted.decode("utf-8"))
        self._state = StorageState.from_dict(payload)

    async def save(self) -> None:
        payload = json.dumps(self._state.to_dict()).encode("utf-8")
        encrypted = await self._encryption.encrypt(payload)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        async with aioopen(self._path, "wb") as file:
            await file.write(encrypted)

    # Admins
    async def add_admin(self, user_id: int) -> bool:
        async with self._lock:
            if user_id in self._state.admins:
                return False
            self._state.admins.append(user_id)
            await self.save()
            return True

    async def remove_admin(self, user_id: int) -> bool:
        async with self._lock:
            if user_id not in self._state.admins:
                return False
            self._state.admins.remove(user_id)
            await self.save()
            return True

    def is_admin(self, user_id: int) -> bool:
        return user_id in self._state.admins

    def list_admins(self) -> List[int]:
        return list(self._state.admins)

    # Applications
    async def add_application(self, user_id: int, full_name: str, answer: str) -> bool:
        async with self._lock:
            if user_id in self._state.applications:
                return False
            self._state.applications[user_id] = Application(
                user_id=user_id,
                full_name=full_name,
                answer=answer,
                created_at=datetime.utcnow().isoformat(),
            )
            await self.save()
            return True

    def has_application(self, user_id: int) -> bool:
        return user_id in self._state.applications

    def get_application(self, user_id: int) -> Optional[Application]:
        return self._state.applications.get(user_id)

    async def pop_application(self, user_id: int) -> Optional[Application]:
        async with self._lock:
            application = self._state.applications.pop(user_id, None)
            if application:
                await self.save()
            return application

    def get_pending_applications(self) -> List[Application]:
        return list(self._state.applications.values())

    # XP tracking
    async def add_xp(self, chat_id: int, user_id: int, amount: int) -> int:
        async with self._lock:
            chat_key = str(chat_id)
            user_key = str(user_id)
            self._state.xp.setdefault(chat_key, {})
            self._state.xp[chat_key][user_key] = self._state.xp[chat_key].get(user_key, 0) + amount
            await self.save()
            return self._state.xp[chat_key][user_key]

    def get_xp_leaderboard(self, chat_id: int, limit: int) -> List[tuple[str, int]]:
        chat_key = str(chat_id)
        scores = self._state.xp.get(chat_key, {})
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores[:limit]

    # Cups
    async def add_cup(self, chat_id: int, title: str, description: str, podium: List[str]) -> None:
        async with self._lock:
            chat_key = str(chat_id)
            self._state.cups.setdefault(chat_key, [])
            self._state.cups[chat_key].append(
                {
                    "title": title,
                    "description": description,
                    "podium": podium,
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            await self.save()

    def get_cups(self, chat_id: int, limit: int) -> List[Dict[str, Any]]:
        chat_key = str(chat_id)
        cups = self._state.cups.get(chat_key, [])
        cups_sorted = sorted(cups, key=lambda item: item["created_at"], reverse=True)
        return cups_sorted[:limit]

