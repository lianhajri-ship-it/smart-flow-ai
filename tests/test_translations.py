"""يتأكد أن كل نص في الصفحة مترجم للغتين، حتى لا ننسى ترجمة عند إضافة نص جديد."""

import re
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "src" / "smart_flow" / "web" / "static"
APP_JS = (STATIC / "app.js").read_text(encoding="utf-8")
INDEX_HTML = (STATIC / "index.html").read_text(encoding="utf-8")


def keys_of(language: str) -> set[str]:
    block = re.search(rf"^  {language}: {{\n(.*?)^  }},", APP_JS, re.M | re.S)
    assert block, f"No '{language}' block in app.js"
    return set(re.findall(r"^    (\w+):", block.group(1), re.M))


def test_both_languages_have_the_same_keys():
    arabic, english = keys_of("ar"), keys_of("en")
    assert arabic - english == set(), "Missing in English"
    assert english - arabic == set(), "Missing in Arabic"


def test_every_html_text_has_a_translation():
    used = set(re.findall(r'data-i18n="(\w+)"', INDEX_HTML))
    assert used - keys_of("ar") == set()


def test_every_server_error_has_a_message():
    for status in (413, 415, 422):
        assert f"error{status}" in keys_of("ar")
