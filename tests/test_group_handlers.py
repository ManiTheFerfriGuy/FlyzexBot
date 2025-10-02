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


class DummyUser:
    def __init__(self, user_id: int = 456, language_code: str = "fa") -> None:
        self.id = user_id
        self.language_code = language_code


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
