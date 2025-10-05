from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path

import pytest

import flyzexbot.services.storage as storage_module

cryptography = pytest.importorskip("cryptography.fernet")

from flyzexbot.services.security import EncryptionManager
from flyzexbot.services.storage import ApplicationResponse, Storage


def test_admin_management(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    encryption = EncryptionManager(key)
    storage = Storage(tmp_path / "store.enc", encryption)
    
    async def runner() -> None:
        await storage.load()

        assert not storage.list_admins()
        assert await storage.add_admin(1, username="@founder", full_name="Founder")
        details = storage.get_admin_details()
        assert details == [
            {"user_id": 1, "username": "founder", "full_name": "Founder"}
        ]
        assert not await storage.add_admin(1)
        assert storage.is_admin(1)
        assert await storage.remove_admin(1)
        assert storage.get_admin_details() == []
        assert not await storage.remove_admin(1)

    asyncio.run(runner())


def test_application_flow(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    storage = Storage(tmp_path / "store.enc", EncryptionManager(key))
    
    async def runner() -> None:
        await storage.load()

        added = await storage.add_application(10, "User", None, "Answer")
        assert added
        assert storage.has_application(10)
        application = storage.get_application(10)
        assert application is not None
        assert application.responses == []
        status = storage.get_application_status(10)
        assert status is not None
        assert status.status == "pending"
        assert status.language_code is None
        withdrew = await storage.withdraw_application(10)
        assert withdrew
        status_after_withdraw = storage.get_application_status(10)
        assert status_after_withdraw is not None
        assert status_after_withdraw.status == "withdrawn"
        assert status_after_withdraw.language_code is None
        assert not storage.has_application(10)

        added_again = await storage.add_application(11, "User", None, "Answer 2")
        assert added_again
        popped = await storage.pop_application(11)
        assert popped is not None
        await storage.mark_application_status(11, "approved")
        status_after_review = storage.get_application_status(11)
        assert status_after_review is not None
        assert status_after_review.status == "approved"
        reapply_after_approval = await storage.add_application(11, "User", None, "New Answer")
        assert not reapply_after_approval

        added_with_language = await storage.add_application(12, "User", None, "Answer 3", language_code="en")
        assert added_with_language
        application_with_language = storage.get_application(12)
        assert application_with_language is not None
        assert application_with_language.language_code == "en"
        stats = storage.get_application_statistics()
        assert "pending" in stats
        assert isinstance(stats.get("languages"), dict)

    asyncio.run(runner())


def test_xp_and_cups(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    storage = Storage(tmp_path / "store.enc", EncryptionManager(key))

    async def runner() -> None:
        await storage.load()

        score = await storage.add_xp(100, 1, 5)
        assert score == 5
        score = await storage.add_xp(100, 1, 5)
        assert score == 10
        leaderboard = storage.get_xp_leaderboard(100, 5)
        assert leaderboard == [("1", 10)]

        await storage.add_cup(100, "Cup", "Desc", ["A", "B", "C"])
        cups = storage.get_cups(100, 5)
        assert len(cups) == 1
        assert cups[0]["title"] == "Cup"

    asyncio.run(runner())


def test_application_question_overrides(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    storage = Storage(tmp_path / "store.enc", EncryptionManager(key))

    async def runner() -> None:
        await storage.load()

        assert storage.get_application_questions("fa") == {}

        await storage.set_application_question(
            "role_prompt",
            "Custom role?",
            language_code="fa",
        )
        prompts_fa = storage.get_application_questions("fa")
        assert prompts_fa["role_prompt"] == "Custom role?"

        await storage.set_application_question("goals_prompt", "Shared goals")
        prompts_default = storage.get_application_questions("fa")
        assert prompts_default["goals_prompt"] == "Shared goals"
        prompts_en = storage.get_application_questions("en")
        assert prompts_en["goals_prompt"] == "Shared goals"

        await storage.set_application_question(
            "role_prompt",
            None,
            language_code="fa",
        )
        prompts_after_reset = storage.get_application_questions("fa")
        assert "role_prompt" not in prompts_after_reset

    asyncio.run(runner())


def test_snapshot_write_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    key = cryptography.Fernet.generate_key()
    storage = Storage(tmp_path / "store.enc", EncryptionManager(key))

    async def runner() -> None:
        await storage.load()
        await storage.add_admin(1)

        original_snapshot = storage._path.read_bytes()

        if storage._path.suffix:
            temp_path = storage._path.with_suffix(storage._path.suffix + ".tmp")
        else:
            temp_path = storage._path.with_name(storage._path.name + ".tmp")

        class FailingAsyncFile:
            def __init__(self, path: Path | str, mode: str, *args, **kwargs) -> None:
                self._file = open(path, mode)

            async def __aenter__(self) -> "FailingAsyncFile":
                return self

            async def __aexit__(self, exc_type, exc, tb) -> None:
                self._file.close()

            async def write(self, data: bytes) -> None:
                portion = max(1, len(data) // 2)
                self._file.write(data[:portion])
                self._file.flush()
                raise RuntimeError("Simulated write failure")

            async def flush(self) -> None:
                self._file.flush()

        real_aioopen = storage_module.aioopen

        def failing_aioopen(path, mode="r", *args, **kwargs):
            if Path(path) == temp_path and "w" in mode:
                return FailingAsyncFile(path, mode, *args, **kwargs)
            return real_aioopen(path, mode, *args, **kwargs)

        monkeypatch.setattr(storage_module, "aioopen", failing_aioopen)

        with pytest.raises(RuntimeError, match="Simulated write failure"):
            await storage.add_admin(2)

        assert storage._path.read_bytes() == original_snapshot
        assert not temp_path.exists()

    asyncio.run(runner())


def test_sqlite_backup(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    backup_path = tmp_path / "backup.sqlite"
    storage = Storage(
        tmp_path / "store.enc",
        EncryptionManager(key),
        backup_path=backup_path,
    )

    async def runner() -> None:
        await storage.load()
        await storage.add_admin(1, username="founder", full_name="Founder")
        await storage.add_application(
            2,
            "Applicant",
            "applicant",
            "Answer",
            responses=[
                ApplicationResponse(
                    question_id="q1",
                    question="Why?",
                    answer="Because",
                )
            ],
            language_code="fa",
        )
        await storage.mark_application_status(2, "review", note="Checking", language_code="fa")
        await storage.add_xp(100, 1, 7)
        await storage.add_cup(100, "Cup", "Desc", ["A", "B"])
        await storage.set_application_question(
            "role_prompt",
            "Custom role?",
            language_code="fa",
        )

    asyncio.run(runner())

    assert backup_path.exists()
    connection = sqlite3.connect(backup_path)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM admins")
        assert cursor.fetchall() == [(1,)]

        cursor.execute("SELECT COUNT(*) FROM application_responses")
        assert cursor.fetchone() == (1,)

        cursor.execute("SELECT score FROM xp WHERE chat_id = ? AND user_id = ?", ("100", "1"))
        assert cursor.fetchone() == (7,)

        cursor.execute(
            "SELECT prompt FROM application_questions WHERE language_code = ? AND question_id = ?",
            ("fa", "role_prompt"),
        )
        assert cursor.fetchone() == ("Custom role?",)

        cursor.execute("SELECT value FROM metadata WHERE key = 'raw_snapshot'")
        snapshot_row = cursor.fetchone()
        assert snapshot_row is not None
        raw_snapshot = json.loads(snapshot_row[0])
        assert "2" in raw_snapshot.get("applications", {})
    finally:
        connection.close()
