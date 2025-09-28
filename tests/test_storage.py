from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bot.storage import Application


def test_format_for_admin_escapes_html():
    app = Application(
        user_id=123,
        username="some<user>",
        full_name="<Evil & Co>",
        answers=[
            {"question": "<script>alert('q')</script>", "answer": "Use <b>bold</b> & more"},
            {"question": "plain", "answer": "text"},
        ],
    )

    rendered = app.format_for_admin()

    assert "<script>" not in rendered
    assert "<Evil" not in rendered
    assert "some<user>" not in rendered
    assert escape("<script>alert('q')</script>") in rendered
    assert "&lt;Evil &amp; Co&gt;" in rendered
    assert "some&lt;user&gt;" in rendered
    assert escape("Use <b>bold</b> & more") in rendered
