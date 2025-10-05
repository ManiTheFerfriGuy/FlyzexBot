from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from aiofiles import open as aioopen

from .security import EncryptionManager


LOGGER = logging.getLogger(__name__)


LOCAL_TIMEZONE = timezone(timedelta(hours=3, minutes=30))


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Return a compact, human-friendly timestamp in the local timezone."""

    moment = dt or datetime.now(LOCAL_TIMEZONE)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=LOCAL_TIMEZONE)
    moment = moment.astimezone(LOCAL_TIMEZONE)

    date_part = moment.strftime("%Y/%m/%d · %H:%M:%S")
    offset = moment.utcoffset()
    if not offset:
        return f"{date_part} UTC"

    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    hours, minutes = divmod(abs(total_minutes), 60)
    return f"{date_part} UTC{sign}{hours:02d}:{minutes:02d}"


def normalize_timestamp(value: str) -> str:
    """Convert legacy ISO timestamps to the modern display format."""

    if not value:
        return ""

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return value

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=LOCAL_TIMEZONE)
    return format_timestamp(parsed)


@dataclass
class ApplicationResponse:
    question_id: str
    question: str
    answer: str


@dataclass
class Application:
    user_id: int
    full_name: str
    username: Optional[str]
    answer: Optional[str]
    created_at: str
    language_code: Optional[str] = None
    responses: List[ApplicationResponse] = field(default_factory=list)


@dataclass
class ApplicationHistoryEntry:
    status: str
    updated_at: str
    note: Optional[str] = None
    language_code: Optional[str] = None


@dataclass
class StorageState:
    admins: List[int] = field(default_factory=list)
    admin_profiles: Dict[int, Dict[str, Optional[str]]] = field(default_factory=dict)
    applications: Dict[int, Application] = field(default_factory=dict)
    application_history: Dict[int, ApplicationHistoryEntry] = field(default_factory=dict)
    xp: Dict[str, Dict[str, int]] = field(default_factory=dict)
    cups: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "admins": self.admins,
            "admin_profiles": {
                str(user_id): {
                    key: value
                    for key, value in profile.items()
                    if value is not None
                }
                for user_id, profile in self.admin_profiles.items()
            },
            "applications": {
                str(k): {
                    **vars(v),
                    "responses": [vars(response) for response in v.responses],
                }
                for k, v in self.applications.items()
            },
            "application_history": {
                str(k): vars(v) for k, v in self.application_history.items()
            },
            "xp": self.xp,
            "cups": self.cups,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "StorageState":
        applications = {}
        for key, value in payload.get("applications", {}).items():
            responses_payload = [
                ApplicationResponse(**response)
                for response in value.get("responses", [])
                if {"question_id", "question", "answer"}.issubset(response.keys())
            ]
            applications[int(key)] = Application(
                user_id=value["user_id"],
                full_name=value.get("full_name", ""),
                username=value.get("username"),
                answer=value.get("answer"),
                created_at=normalize_timestamp(value.get("created_at", "")),
                language_code=value.get("language_code"),
                responses=responses_payload,
            )

        application_history = {}
        for key, value in payload.get("application_history", {}).items():
            application_history[int(key)] = ApplicationHistoryEntry(
                status=value.get("status", ""),
                updated_at=normalize_timestamp(value.get("updated_at", "")),
                note=value.get("note"),
                language_code=value.get("language_code"),
            )
        return cls(
            admins=list(payload.get("admins", [])),
            admin_profiles={
                int(user_id): {
                    key: value
                    for key, value in (profile or {}).items()
                    if isinstance(value, str) and value
                }
                for user_id, profile in payload.get("admin_profiles", {}).items()
            },
            applications=applications,
            application_history=application_history,
            xp={k: {user: int(score) for user, score in v.items()} for k, v in payload.get("xp", {}).items()},
            cups={
                k: [
                    {
                        **entry,
                        "created_at": normalize_timestamp(entry.get("created_at", "")),
                    }
                    for entry in v
                ]
                for k, v in payload.get("cups", {}).items()
            },
        )


class Storage:
    def __init__(
        self,
        path: Path,
        encryption: EncryptionManager,
        *,
        backup_path: Optional[Path] = None,
    ) -> None:
        self._path = path
        self._encryption = encryption
        self._lock = asyncio.Lock()
        self._state = StorageState()
        self._backup_path = backup_path

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
        LOGGER.info("storage_loaded", extra={"path": str(self._path)})

    async def save(self) -> None:
        payload = await self._snapshot()
        await self._write_snapshot(payload)
        if self._backup_path:
            try:
                await self._write_sqlite_backup(payload)
            except Exception:
                LOGGER.exception(
                    "sqlite_backup_failed", extra={"path": str(self._backup_path)}
                )

    async def add_admin(
        self,
        user_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> bool:
        normalized_username = username.strip() if isinstance(username, str) else None
        if normalized_username:
            normalized_username = normalized_username.lstrip("@") or None

        normalized_full_name = full_name.strip() if isinstance(full_name, str) else None
        async with self._lock:
            profile = self._state.admin_profiles.setdefault(user_id, {})
            changed = False

            if user_id not in self._state.admins:
                self._state.admins.append(user_id)
                changed = True

            if normalized_username and profile.get("username") != normalized_username:
                profile["username"] = normalized_username
                changed = True

            if normalized_full_name and profile.get("full_name") != normalized_full_name:
                profile["full_name"] = normalized_full_name
                changed = True

            if not profile:
                self._state.admin_profiles.pop(user_id, None)

            if not changed:
                return False

        await self.save()
        LOGGER.info("admin_added", extra={"user_id": user_id})
        return True

    async def remove_admin(self, user_id: int) -> bool:
        async with self._lock:
            if user_id not in self._state.admins:
                return False
            self._state.admins.remove(user_id)
            self._state.admin_profiles.pop(user_id, None)
        await self.save()
        LOGGER.info("admin_removed", extra={"user_id": user_id})
        return True

    def is_admin(self, user_id: int) -> bool:
        return user_id in self._state.admins

    def list_admins(self) -> List[int]:
        return list(self._state.admins)

    def get_admin_details(self) -> List[Dict[str, Optional[str]]]:
        details: List[Dict[str, Optional[str]]] = []
        for admin_id in self._state.admins:
            profile = self._state.admin_profiles.get(admin_id, {})
            username = profile.get("username")
            full_name = profile.get("full_name")

            application = self._state.applications.get(admin_id)
            if application:
                username = username or application.username
                full_name = full_name or application.full_name

            details.append(
                {
                    "user_id": admin_id,
                    "username": username,
                    "full_name": full_name,
                }
            )
        return details

    async def add_application(
        self,
        user_id: int,
        full_name: str,
        username: Optional[str],
        answer: Optional[str],
        language_code: Optional[str] = None,
        responses: Optional[List[ApplicationResponse]] = None,
    ) -> bool:
        async with self._lock:
            history_entry = self._state.application_history.get(user_id)
            if history_entry and history_entry.status == "approved":
                return False
            if user_id in self._state.applications:
                return False
            timestamp = format_timestamp()
            self._state.applications[user_id] = Application(
                user_id=user_id,
                full_name=full_name,
                username=username,
                answer=answer,
                created_at=timestamp,
                language_code=language_code,
                responses=list(responses or []),
            )
            self._state.application_history[user_id] = ApplicationHistoryEntry(
                status="pending",
                updated_at=timestamp,
                language_code=language_code,
            )
        await self.save()
        LOGGER.info("application_added", extra={"user_id": user_id})
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

    async def withdraw_application(self, user_id: int) -> bool:
        async with self._lock:
            application = self._state.applications.pop(user_id, None)
            if not application:
                return False
            timestamp = format_timestamp()
            self._state.application_history[user_id] = ApplicationHistoryEntry(
                status="withdrawn",
                updated_at=timestamp,
                language_code=getattr(application, "language_code", None),
            )
        await self.save()
        LOGGER.info("application_withdrawn", extra={"user_id": user_id})
        return True

    async def mark_application_status(
        self,
        user_id: int,
        status: str,
        note: Optional[str] = None,
        language_code: Optional[str] = None,
    ) -> None:
        async with self._lock:
            timestamp = format_timestamp()
            previous = self._state.application_history.get(user_id)
            language = language_code or getattr(previous, "language_code", None)
            self._state.application_history[user_id] = ApplicationHistoryEntry(
                status=status,
                updated_at=timestamp,
                note=note,
                language_code=language,
            )
        await self.save()
        LOGGER.info("application_status_updated", extra={"user_id": user_id, "status": status})

    def get_application_status(self, user_id: int) -> Optional[ApplicationHistoryEntry]:
        return self._state.application_history.get(user_id)

    def get_applicants_by_status(self, status: str) -> List[tuple[int, ApplicationHistoryEntry]]:
        return [
            (user_id, history)
            for user_id, history in self._state.application_history.items()
            if history.status == status
        ]

    def get_application_statistics(self) -> Dict[str, Any]:
        history = list(self._state.application_history.items())
        status_counter = Counter(entry.status for _, entry in history)
        language_counter = Counter(
            (entry.language_code or "unknown") for _, entry in history if entry.language_code
        )
        for application in self._state.applications.values():
            code = application.language_code or "unknown"
            language_counter[code] += 1

        pending_lengths = [
            sum(len(response.answer) for response in application.responses)
            or len(application.answer or "")
            for application in self._state.applications.values()
        ]
        average_response_length = (
            sum(pending_lengths) / len(pending_lengths)
            if pending_lengths
            else 0
        )

        recent_updates = sorted(
            history,
            key=lambda item: getattr(item[1], "updated_at", ""),
            reverse=True,
        )[:5]

        return {
            "total": len(history),
            "pending": len(self._state.applications),
            "status_counts": dict(status_counter),
            "languages": dict(language_counter),
            "average_pending_answer_length": average_response_length,
            "recent_updates": [
                {
                    "user_id": user_id,
                    "status": entry.status,
                    "updated_at": entry.updated_at,
                }
                for user_id, entry in recent_updates
            ],
        }

    async def add_xp(self, chat_id: int, user_id: int, amount: int) -> int:
        async with self._lock:
            chat_key = str(chat_id)
            user_key = str(user_id)
            self._state.xp.setdefault(chat_key, {})
            self._state.xp[chat_key][user_key] = self._state.xp[chat_key].get(user_key, 0) + amount
        await self.save()
        LOGGER.debug("xp_added", extra={"chat_id": chat_id, "user_id": user_id, "amount": amount})
        return self._state.xp[chat_key][user_key]

    def get_xp_leaderboard(self, chat_id: int, limit: int) -> List[tuple[str, int]]:
        chat_key = str(chat_id)
        scores = self._state.xp.get(chat_key, {})
        sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_scores[:limit]

    async def add_cup(self, chat_id: int, title: str, description: str, podium: List[str]) -> None:
        async with self._lock:
            chat_key = str(chat_id)
            self._state.cups.setdefault(chat_key, [])
            self._state.cups[chat_key].append(
                {
                    "title": title,
                    "description": description,
                    "podium": podium,
                    "created_at": format_timestamp(),
                }
            )
        await self.save()
        LOGGER.info("cup_added", extra={"chat_id": chat_id, "title": title})

    def get_cups(self, chat_id: int, limit: int) -> List[Dict[str, Any]]:
        chat_key = str(chat_id)
        cups = self._state.cups.get(chat_key, [])
        cups_sorted = sorted(cups, key=lambda item: item["created_at"], reverse=True)
        return cups_sorted[:limit]

    async def _snapshot(self) -> bytes:
        async with self._lock:
            payload = json.dumps(self._state.to_dict()).encode("utf-8")
        return payload

    async def _write_snapshot(self, payload: bytes) -> None:
        encrypted = await self._encryption.encrypt(payload)
        self._path.parent.mkdir(parents=True, exist_ok=True)

        if self._path.suffix:
            tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        else:
            tmp_path = self._path.with_name(self._path.name + ".tmp")

        try:
            async with aioopen(tmp_path, "wb") as file:
                await file.write(encrypted)
                await file.flush()
            await asyncio.to_thread(os.replace, tmp_path, self._path)
        except Exception:
            with contextlib.suppress(FileNotFoundError):
                await asyncio.to_thread(tmp_path.unlink)
            raise

        LOGGER.debug("storage_flushed", extra={"path": str(self._path)})

    async def _write_sqlite_backup(self, payload: bytes) -> None:
        if not self._backup_path:
            return

        snapshot = json.loads(payload.decode("utf-8"))
        await asyncio.to_thread(self._dump_sqlite_backup, snapshot)

    def _dump_sqlite_backup(self, snapshot: Dict[str, Any]) -> None:
        assert self._backup_path is not None
        self._backup_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self._backup_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.cursor()

            cursor.executescript(
                """
                DROP TABLE IF EXISTS admins;
                DROP TABLE IF EXISTS admin_profiles;
                DROP TABLE IF EXISTS applications;
                DROP TABLE IF EXISTS application_responses;
                DROP TABLE IF EXISTS application_history;
                DROP TABLE IF EXISTS xp;
                DROP TABLE IF EXISTS cups;
                DROP TABLE IF EXISTS metadata;

                CREATE TABLE admins (
                    user_id INTEGER PRIMARY KEY
                );

                CREATE TABLE admin_profiles (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT
                );

                CREATE TABLE applications (
                    user_id INTEGER PRIMARY KEY,
                    full_name TEXT,
                    username TEXT,
                    answer TEXT,
                    created_at TEXT,
                    language_code TEXT
                );

                CREATE TABLE application_responses (
                    user_id INTEGER,
                    position INTEGER,
                    question_id TEXT,
                    question TEXT,
                    answer TEXT,
                    PRIMARY KEY (user_id, position),
                    FOREIGN KEY (user_id) REFERENCES applications(user_id) ON DELETE CASCADE
                );

                CREATE TABLE application_history (
                    user_id INTEGER PRIMARY KEY,
                    status TEXT,
                    updated_at TEXT,
                    note TEXT,
                    language_code TEXT,
                    FOREIGN KEY (user_id) REFERENCES applications(user_id) ON DELETE CASCADE
                );

                CREATE TABLE xp (
                    chat_id TEXT,
                    user_id TEXT,
                    score INTEGER,
                    PRIMARY KEY (chat_id, user_id)
                );

                CREATE TABLE cups (
                    chat_id TEXT,
                    position INTEGER,
                    title TEXT,
                    description TEXT,
                    podium TEXT,
                    created_at TEXT,
                    PRIMARY KEY (chat_id, position)
                );

                CREATE TABLE metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
                """
            )

            admins = [(int(user_id),) for user_id in snapshot.get("admins", [])]
            if admins:
                cursor.executemany("INSERT INTO admins(user_id) VALUES (?)", admins)

            profiles = [
                (
                    int(user_id),
                    profile.get("username"),
                    profile.get("full_name"),
                )
                for user_id, profile in snapshot.get("admin_profiles", {}).items()
            ]
            if profiles:
                cursor.executemany(
                    "INSERT INTO admin_profiles(user_id, username, full_name) VALUES (?, ?, ?)",
                    profiles,
                )

            applications = []
            responses: List[tuple[int, int, Optional[str], Optional[str], Optional[str]]] = []
            for user_id, application in snapshot.get("applications", {}).items():
                int_user_id = int(user_id)
                applications.append(
                    (
                        int_user_id,
                        application.get("full_name"),
                        application.get("username"),
                        application.get("answer"),
                        application.get("created_at"),
                        application.get("language_code"),
                    )
                )
                for position, response in enumerate(application.get("responses", [])):
                    responses.append(
                        (
                            int_user_id,
                            position,
                            response.get("question_id"),
                            response.get("question"),
                            response.get("answer"),
                        )
                    )

            if applications:
                cursor.executemany(
                    """
                    INSERT INTO applications(
                        user_id, full_name, username, answer, created_at, language_code
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    applications,
                )

            if responses:
                cursor.executemany(
                    """
                    INSERT INTO application_responses(
                        user_id, position, question_id, question, answer
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    responses,
                )

            history_rows = [
                (
                    int(user_id),
                    entry.get("status"),
                    entry.get("updated_at"),
                    entry.get("note"),
                    entry.get("language_code"),
                )
                for user_id, entry in snapshot.get("application_history", {}).items()
            ]
            if history_rows:
                cursor.executemany(
                    """
                    INSERT INTO application_history(
                        user_id, status, updated_at, note, language_code
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    history_rows,
                )

            xp_rows = [
                (chat_id, user_id, int(score))
                for chat_id, scores in snapshot.get("xp", {}).items()
                for user_id, score in scores.items()
            ]
            if xp_rows:
                cursor.executemany(
                    "INSERT INTO xp(chat_id, user_id, score) VALUES (?, ?, ?)", xp_rows
                )

            cups_rows = []
            for chat_id, cups in snapshot.get("cups", {}).items():
                for position, cup in enumerate(cups):
                    cups_rows.append(
                        (
                            chat_id,
                            position,
                            cup.get("title"),
                            cup.get("description"),
                            json.dumps(cup.get("podium", []), ensure_ascii=False),
                            cup.get("created_at"),
                        )
                    )
            if cups_rows:
                cursor.executemany(
                    """
                    INSERT INTO cups(
                        chat_id, position, title, description, podium, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    cups_rows,
                )

            cursor.execute(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                ("raw_snapshot", json.dumps(snapshot, ensure_ascii=False)),
            )
            cursor.execute(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                ("exported_at", datetime.utcnow().isoformat()),
            )

