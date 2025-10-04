from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from flyzexbot.handlers.group import GroupHandlers
from flyzexbot.localization import PERSIAN_TEXTS


class DummyChat:
    def __init__(self, chat_id: int = 123) -> None:
        self.id = chat_id
        self.messages: list[str] = []

    async def send_message(self, text: str, **_: object) -> None:  # noqa: ANN003 - kwargs unused
        self.messages.append(text)


class DummyMessage:
    def __init__(self, text: str = "سلام") -> None:
        self.text = text
        self.replies: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.replies.append(text)


class DummyUser:
    def __init__(self, user_id: int = 456, language_code: str = "fa") -> None:
        self.id = user_id
        self.language_code = language_code
        self.full_name = "Test User"
        self.username = "test_user"


class DummyContext:
    def __init__(self, args: list[str]) -> None:
        self.args = args
        self.chat_data: dict[str, object] = {}


def test_add_cup_accepts_single_argument_string() -> None:
    storage = SimpleNamespace(add_cup=AsyncMock())
    handler = GroupHandlers(
        storage=storage,
        xp_reward=10,
        xp_limit=100,
        cups_limit=10,
    )
    handler._is_admin = AsyncMock(return_value=True)  # type: ignore[method-assign]

    chat = DummyChat()
    user = DummyUser()
    update = SimpleNamespace(effective_chat=chat, effective_user=user)
    context = DummyContext(["Title|Description|A,B,C"])

    asyncio.run(handler.add_cup(update, context))

    storage.add_cup.assert_awaited_once_with(chat.id, "Title", "Description", ["A", "B", "C"])
    assert PERSIAN_TEXTS.group_add_cup_usage not in chat.messages


def test_track_activity_uses_custom_milestone_interval() -> None:
    class StorageStub:
        async def add_xp(self, chat_id: int, user_id: int, amount: int) -> int:  # noqa: ANN001, ANN201
            assert chat_id == 1
            assert user_id == 2
            assert amount == 10
            return 30

    storage = StorageStub()
    handler = GroupHandlers(
        storage=storage,
        xp_reward=10,
        xp_limit=10,
        cups_limit=5,
        milestone_interval=3,
    )

    message = DummyMessage("Hello")
    chat = SimpleNamespace(id=1)
    user = SimpleNamespace(id=2, language_code="fa", full_name="Tester", username=None)
    update = SimpleNamespace(effective_message=message, effective_chat=chat, effective_user=user)
    context = SimpleNamespace(chat_data={})

    asyncio.run(handler.track_activity(update, context))

    assert message.replies, "Expected a milestone message when score matches custom interval"


def test_track_activity_skips_non_milestones_with_custom_interval() -> None:
    class StorageStub:
        async def add_xp(self, chat_id: int, user_id: int, amount: int) -> int:  # noqa: ANN001, ANN201
            return 20

    storage = StorageStub()
    handler = GroupHandlers(
        storage=storage,
        xp_reward=10,
        xp_limit=10,
        cups_limit=5,
        milestone_interval=3,
    )

    message = DummyMessage("Hello")
    chat = SimpleNamespace(id=1)
    user = SimpleNamespace(id=2, language_code="fa", full_name="Tester", username=None)
    update = SimpleNamespace(effective_message=message, effective_chat=chat, effective_user=user)
    context = SimpleNamespace(chat_data={})

    asyncio.run(handler.track_activity(update, context))

    assert not message.replies, "Milestone message should not be sent for non-matching scores"
