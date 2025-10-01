from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

cryptography = pytest.importorskip("cryptography.fernet")

from flyzexbot.services.security import EncryptionManager
from flyzexbot.services.storage import Storage


def test_admin_management(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    encryption = EncryptionManager(key)
    storage = Storage(tmp_path / "store.enc", encryption)
    
    async def runner() -> None:
        await storage.load()

        assert not storage.list_admins()
        assert await storage.add_admin(1)
        assert not await storage.add_admin(1)
        assert storage.is_admin(1)
        assert await storage.remove_admin(1)
        assert not await storage.remove_admin(1)

    asyncio.run(runner())


def test_application_flow(tmp_path: Path) -> None:
    key = cryptography.Fernet.generate_key()
    storage = Storage(tmp_path / "store.enc", EncryptionManager(key))
    
    async def runner() -> None:
        await storage.load()

        added = await storage.add_application(10, "User", "Answer")
        assert added
        assert storage.has_application(10)
        application = storage.get_application(10)
        assert application is not None
        status = storage.get_application_status(10)
        assert status is not None
        assert status.status == "pending"
        withdrew = await storage.withdraw_application(10)
        assert withdrew
        status_after_withdraw = storage.get_application_status(10)
        assert status_after_withdraw is not None
        assert status_after_withdraw.status == "withdrawn"
        assert not storage.has_application(10)

        added_again = await storage.add_application(11, "User", "Answer 2")
        assert added_again
        popped = await storage.pop_application(11)
        assert popped is not None
        await storage.mark_application_status(11, "approved")
        status_after_review = storage.get_application_status(11)
        assert status_after_review is not None
        assert status_after_review.status == "approved"

        added_with_language = await storage.add_application(12, "User", "Answer 3", language_code="en")
        assert added_with_language
        application_with_language = storage.get_application(12)
        assert application_with_language is not None
        assert application_with_language.language_code == "en"

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
