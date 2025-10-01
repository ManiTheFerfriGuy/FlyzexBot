from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from flyzexbot.handlers.dm import DMHandlers


class DummyChat:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    async def send_message(self, text: str, **kwargs: str) -> None:  # noqa: ANN003 - kwargs not used directly
        self.messages.append({"text": text, **kwargs})


class DummyUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class DummyContext:
    def __init__(self, args: list[str]) -> None:
        self.args = args


def test_promote_admin_invalid_identifier() -> None:
    storage = SimpleNamespace(add_admin=AsyncMock())
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(1), effective_chat=chat)
    context = DummyContext(["not-a-number"])

    asyncio.run(handler.promote_admin(update, context))

    storage.add_admin.assert_not_awaited()
    assert chat.messages and chat.messages[-1]["text"] == "شناسه باید عددی باشد."


def test_demote_admin_invalid_identifier() -> None:
    storage = SimpleNamespace(remove_admin=AsyncMock())
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(1), effective_chat=chat)
    context = DummyContext(["invalid"])

    asyncio.run(handler.demote_admin(update, context))

    storage.remove_admin.assert_not_awaited()
    assert chat.messages and chat.messages[-1]["text"] == "شناسه باید عددی باشد."
