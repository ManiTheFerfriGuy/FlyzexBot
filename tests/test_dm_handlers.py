from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from flyzexbot.handlers.dm import DMHandlers
from flyzexbot.localization import ENGLISH_TEXTS, PERSIAN_TEXTS
from flyzexbot.services.storage import Application, ApplicationHistoryEntry


class DummyChat:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    async def send_message(self, text: str, **kwargs: str) -> None:  # noqa: ANN003 - kwargs not used directly
        self.messages.append({"text": text, **kwargs})


class DummyCallbackMessage:
    def __init__(self, chat_id: int = 111, message_id: int = 222) -> None:
        self.chat_id = chat_id
        self.message_id = message_id
        self.edits: list[dict[str, str | None]] = []

    async def edit_text(self, text: str, parse_mode: str | None = None) -> None:
        self.edits.append({"text": text, "parse_mode": parse_mode})


class DummyIncomingMessage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.replies: list[str] = []

    async def reply_text(self, text: str) -> None:
        self.replies.append(text)


class DummyUser:
    def __init__(self, user_id: int, language_code: str = "fa") -> None:
        self.id = user_id
        self.language_code = language_code


class DummyContext:
    def __init__(self, args: list[str], bot: object | None = None) -> None:
        self.args = args
        self.user_data: dict[str, object] = {}
        self.bot = bot or SimpleNamespace(
            edit_message_text=AsyncMock(),
            send_message=AsyncMock(),
        )
        self.bot_data: dict[str, object] = {}
        self.application = None


def test_promote_admin_invalid_identifier() -> None:
    storage = SimpleNamespace(add_admin=AsyncMock())
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(1), effective_chat=chat)
    context = DummyContext(["not-a-number"])

    asyncio.run(handler.promote_admin(update, context))

    storage.add_admin.assert_not_awaited()
    assert chat.messages and chat.messages[-1]["text"] == PERSIAN_TEXTS.dm_admin_invalid_user_id


def test_demote_admin_invalid_identifier() -> None:
    storage = SimpleNamespace(remove_admin=AsyncMock())
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(1), effective_chat=chat)
    context = DummyContext(["invalid"])

    asyncio.run(handler.demote_admin(update, context))

    storage.remove_admin.assert_not_awaited()
    assert chat.messages and chat.messages[-1]["text"] == PERSIAN_TEXTS.dm_admin_invalid_user_id


def test_promote_admin_invalid_identifier_english() -> None:
    storage = SimpleNamespace(add_admin=AsyncMock())
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(1, language_code="en"), effective_chat=chat)
    context = DummyContext(["oops"])

    asyncio.run(handler.promote_admin(update, context))

    storage.add_admin.assert_not_awaited()
    assert chat.messages and chat.messages[-1]["text"] == ENGLISH_TEXTS.dm_admin_invalid_user_id


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


def test_status_with_approved_history_english() -> None:
    history_entry = ApplicationHistoryEntry(status="approved", updated_at="2024-01-01T00:00:00", note=None)
    storage = SimpleNamespace(get_application_status=lambda _: history_entry)
    handler = DMHandlers(storage=storage, owner_id=1)
    chat = DummyChat()
    update = SimpleNamespace(effective_user=DummyUser(9, language_code="en"), effective_chat=chat)
    context = DummyContext([])

    asyncio.run(handler.status(update, context))

    assert chat.messages
    message = chat.messages[-1]["text"]
    assert ENGLISH_TEXTS.dm_status_approved in message
    assert context.user_data.get("preferred_language") == "en"


def test_admin_handles_note_for_approval() -> None:
    application = Application(
        user_id=42,
        full_name="Tester",
        answer="I'd love to help",
        created_at="2024-05-01T12:00:00",
        language_code="en",
    )
    storage = SimpleNamespace(
        pop_application=AsyncMock(return_value=application),
        mark_application_status=AsyncMock(),
        is_admin=lambda _: True,
    )
    handler = DMHandlers(storage=storage, owner_id=1)
    message = DummyCallbackMessage()
    admin_user = DummyUser(100, language_code="en")
    query = SimpleNamespace(
        data=f"application:{application.user_id}:approve",
        from_user=admin_user,
        message=message,
        answer=AsyncMock(),
    )
    update = SimpleNamespace(callback_query=query)
    context = DummyContext([])

    asyncio.run(handler.handle_application_action(update, context))

    assert context.user_data.get("pending_review_note")
    assert message.edits
    prompt_text = message.edits[-1]["text"]
    assert "SKIP" in prompt_text

    note_message = DummyIncomingMessage("Welcome to the team!")
    update_note = SimpleNamespace(message=note_message, effective_user=admin_user)

    asyncio.run(handler.receive_application(update_note, context))

    storage.pop_application.assert_awaited_once_with(application.user_id)
    storage.mark_application_status.assert_awaited_once_with(
        application.user_id, "approved", note="Welcome to the team!"
    )
    send_kwargs = context.bot.send_message.await_args.kwargs
    assert send_kwargs["chat_id"] == application.user_id
    assert "Welcome to the team!" in send_kwargs["text"]
    assert ENGLISH_TEXTS.dm_application_note_label in send_kwargs["text"]
    edit_kwargs = context.bot.edit_message_text.await_args.kwargs
    assert "Welcome to the team!" in edit_kwargs["text"]
    assert ENGLISH_TEXTS.dm_application_note_label in edit_kwargs["text"]
    assert "pending_review_note" not in context.user_data


def test_admin_handles_skip_for_denial() -> None:
    application = Application(
        user_id=77,
        full_name="کاربر",
        answer="",
        created_at="2024-05-02T12:00:00",
        language_code="fa",
    )
    storage = SimpleNamespace(
        pop_application=AsyncMock(return_value=application),
        mark_application_status=AsyncMock(),
        is_admin=lambda _: True,
    )
    handler = DMHandlers(storage=storage, owner_id=1)
    message = DummyCallbackMessage()
    admin_user = DummyUser(200, language_code="fa")
    query = SimpleNamespace(
        data=f"application:{application.user_id}:deny",
        from_user=admin_user,
        message=message,
        answer=AsyncMock(),
    )
    update = SimpleNamespace(callback_query=query)
    context = DummyContext([])

    asyncio.run(handler.handle_application_action(update, context))

    note_message = DummyIncomingMessage("SkIp")
    update_note = SimpleNamespace(message=note_message, effective_user=admin_user)

    asyncio.run(handler.receive_application(update_note, context))

    storage.mark_application_status.assert_awaited_once_with(
        application.user_id, "denied", note=None
    )
    send_kwargs = context.bot.send_message.await_args.kwargs
    assert send_kwargs["chat_id"] == application.user_id
    assert PERSIAN_TEXTS.dm_application_note_label not in send_kwargs["text"]
    edit_kwargs = context.bot.edit_message_text.await_args.kwargs
    assert PERSIAN_TEXTS.dm_application_note_label not in edit_kwargs["text"]
