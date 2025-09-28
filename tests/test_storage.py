from bot.storage import Application


def _build_application(**kwargs):
    base = dict(
        user_id=123,
        username="flyer",
        full_name="Test Pilot",
        answers=[{"question": "Why join?", "answer": "For fun"}],
    )
    base.update(kwargs)
    return Application(**base)


def test_format_for_admin_includes_human_readable_timestamp():
    application = _build_application(submitted_at="2024-05-20T12:34:56+00:00")

    formatted = application.format_for_admin()

    assert "Submitted at: 2024-05-20 12:34:56 UTC" in formatted


def test_format_for_admin_handles_unparseable_timestamp():
    application = _build_application(submitted_at="not-a-timestamp")

    formatted = application.format_for_admin()

    assert "Submitted at: not-a-timestamp" in formatted


def test_format_for_admin_sanitises_newlines_in_timestamp():
    application = _build_application(submitted_at="2024-05-20T12:34:56+00:00\nMALICIOUS")

    formatted = application.format_for_admin()

    assert "MALICIOUS" not in formatted
    assert "Submitted at: 2024-05-20 12:34:56 UTC" in formatted
