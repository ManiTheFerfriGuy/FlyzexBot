from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from flyzexbot.handlers.dm import DMHandlers
from flyzexbot.localization import PERSIAN_TEXTS
from flyzexbot.services.storage import ApplicationHistoryEntry


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
        self.user_data: dict[str, object] = {}


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


def test_withdraw_success() -> None:
    storage = SimpleNamespace(withdraw_application=AsyncMock(return_value=True))
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(5), effective_chat=chat)
    context = DummyContext([])

    asyncio.run(handler.withdraw(update, context))

    storage.withdraw_application.assert_awaited_once_with(5)
    assert chat.messages and chat.messages[-1]["text"] == PERSIAN_TEXTS.dm_withdraw_success


def test_withdraw_not_found() -> None:
    storage = SimpleNamespace(withdraw_application=AsyncMock(return_value=False))
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(6), effective_chat=chat)
    context = DummyContext([])

    asyncio.run(handler.withdraw(update, context))

    storage.withdraw_application.assert_awaited_once_with(6)
    assert chat.messages and chat.messages[-1]["text"] == PERSIAN_TEXTS.dm_withdraw_not_found


def test_status_without_history() -> None:
    storage = SimpleNamespace(get_application_status=lambda _: None)
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(7), effective_chat=chat)
    context = DummyContext([])

    asyncio.run(handler.status(update, context))

    assert chat.messages and chat.messages[-1]["text"] == PERSIAN_TEXTS.dm_status_none


def test_status_with_pending_history() -> None:
    history_entry = ApplicationHistoryEntry(status="pending", updated_at="2024-01-01T00:00:00", note=None)
    storage = SimpleNamespace(get_application_status=lambda _: history_entry)
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(8), effective_chat=chat)
    context = DummyContext([])

    asyncio.run(handler.status(update, context))

    assert chat.messages
    last_message = chat.messages[-1]["text"]
    assert PERSIAN_TEXTS.dm_status_pending in last_message
