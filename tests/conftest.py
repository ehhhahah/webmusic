"""Shared fixtures for generate_site unit tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_DIR = ROOT / "assets" / "original_article"

if str(GENERATOR_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATOR_DIR))

import generate_site as gs  # noqa: E402


MINIMAL_PAGE = """\
<!DOCTYPE html>
<html lang="en">
 <head>
  <title>placeholder</title>
 </head>
 <body>
  <div class="navbary is-black is-spaced has-shadow">
   <a class="onblack" href="/apps">Apps</a>
  </div>
  <header>
   <h1 id="pageTitle">OLD TITLE</h1>
  </header>
  <div id="webapps" class="webapps g-4">OLD WEBAPPS</div>
  <div class="flex-container">
   <div class="flex-item-left">OLD LEFT</div>
   <div class="flex-item-right">OLD RIGHT</div>
  </div>
 </body>
</html>
"""


@pytest.fixture
def sample_apps() -> list[gs.App]:
    return [
        gs.App(
            id=1,
            link="https://example.com/alpha",
            title=gs.LocalizedText(pl="Alfa", eng="Alpha"),
            description=gs.LocalizedText(pl="Opis alfa", eng="Alpha desc"),
            authors=[
                gs.Author(name="Ada", link="https://ada.example"),
                gs.Author(name=gs.LocalizedText(pl="Beata", eng="Betty")),
            ],
            tags=["game", "forKids"],
            more_links=[
                gs.MoreLink(
                    name=gs.LocalizedText(pl="Więcej", eng="More"),
                    link="https://example.com/more",
                )
            ],
        ),
        gs.App(
            id=2,
            link="https://example.com/beta",
            title=gs.LocalizedText(pl="Beta PL", eng=""),
            description=gs.LocalizedText(pl="Opis beta", eng=""),
            authors=[gs.Author(name="No Link Author")],
            tags=["tool"],
        ),
    ]


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Temp site layout + monkeypatched module paths used by generate_site."""
    article = tmp_path / "assets" / "original_article"
    article.mkdir(parents=True)

    js_path = tmp_path / "script.js"
    js_path.write_text("const CATEGORIES = [];\nfunction noop() {}\n", encoding="utf-8")

    tags_json = article / "tags.json"
    html_output = article / "output.html"
    db_path = article / "db-fixed.json"

    page_names = (
        "index.html",
        "apps.html",
        "evaluation.html",
        "submit.html",
        "tagsinfo.html",
    )
    pages = []
    for name in page_names:
        page = tmp_path / name
        page.write_text(MINIMAL_PAGE, encoding="utf-8")
        pages.append(page)

    monkeypatch.setattr(gs, "ROOT", tmp_path)
    monkeypatch.setattr(gs, "ARTICLE_DIR", article)
    monkeypatch.setattr(gs, "HTML_OUTPUT", html_output)
    monkeypatch.setattr(gs, "TAGS", tags_json)
    monkeypatch.setattr(gs, "DB_PATH", db_path)
    monkeypatch.setattr(gs, "APPS_PAGE_PATH", tmp_path / "apps.html")
    monkeypatch.setattr(gs, "TAGS_PAGE_PATH", tmp_path / "tagsinfo.html")
    monkeypatch.setattr(gs, "ALL_PAGES", pages)
    monkeypatch.setattr(gs, "JS_PATH", js_path)

    # Keep replace_tags_html fast and independent of the full tag catalog.
    small_descriptors = {
        "game": "Playful, focused on having fun.",
        "forKids": "Good for kids in any age.",
        "tool": "Useful to musicians and producers.",
    }
    monkeypatch.setattr(gs, "TAGS_DESCRIPTORS", small_descriptors)
    monkeypatch.setattr(gs, "KNOWN_TAGS", frozenset(small_descriptors))

    return tmp_path
