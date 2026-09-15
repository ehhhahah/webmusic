"""Unit tests for assets/original_article/generate_site.py."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import generate_site as gs


# --- models / validation -----------------------------------------------------


def test_app_rejects_empty_link():
    with pytest.raises(ValidationError, match="link must be non-empty"):
        gs.App(
            id=1,
            link="   ",
            title=gs.LocalizedText(eng="T"),
            description=gs.LocalizedText(eng="D"),
            authors=[gs.Author(name="A")],
            tags=["game"],
        )


def test_app_rejects_unknown_tags():
    with pytest.raises(ValidationError, match="unknown tag"):
        gs.App(
            id=1,
            link="https://example.com",
            title=gs.LocalizedText(eng="T"),
            description=gs.LocalizedText(eng="D"),
            authors=[gs.Author(name="A")],
            tags=["game", "notARealTag"],
        )


def test_app_rejects_id_below_one():
    with pytest.raises(ValidationError):
        gs.App(
            id=0,
            link="https://example.com",
            title=gs.LocalizedText(eng="T"),
            description=gs.LocalizedText(eng="D"),
            authors=[gs.Author(name="A")],
            tags=["game"],
        )


def test_catalog_rejects_duplicate_ids(sample_apps):
    twin = sample_apps[0].model_copy(update={"id": sample_apps[1].id})
    with pytest.raises(ValidationError, match="duplicate app id"):
        gs.Catalog.model_validate([sample_apps[1], twin])


def test_catalog_accepts_unique_ids(sample_apps):
    catalog = gs.Catalog.model_validate(sample_apps)
    assert len(catalog.root) == 2


def test_app_defaults_legacy_dates():
    app = gs.App(
        id=1,
        link="https://example.com",
        title=gs.LocalizedText(eng="T"),
        description=gs.LocalizedText(eng="D"),
        authors=[gs.Author(name="A")],
        tags=["game"],
    )
    assert app.created_at == gs.LEGACY_CATALOG_DATE
    assert app.last_verified_at == gs.LEGACY_CATALOG_DATE


# --- helpers -----------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "lang", "expected"),
    [
        ("plain", "eng", "plain"),
        ("plain", "pl", "plain"),
        (gs.LocalizedText(pl="PL", eng="EN"), "eng", "EN"),
        (gs.LocalizedText(pl="PL", eng="EN"), "pl", "PL"),
        (gs.LocalizedText(pl="PL", eng=""), "eng", "PL"),
        (gs.LocalizedText(pl="PL", eng=""), "pl", "PL"),
    ],
)
def test_localized_value(value, lang, expected):
    assert gs.localized_value(value, lang) == expected


def test_stamp_app_dates_sets_missing_created_and_always_verifies():
    today = datetime.date(2026, 9, 15)
    raw = [
        {"id": 1, "title": "new"},
        {"id": 2, "created_at": "2020-01-01", "title": "old"},
    ]
    stamped = gs.stamp_app_dates(raw, today=today)
    assert stamped[0]["created_at"] == "2026-09-15"
    assert stamped[0]["last_verified_at"] == "2026-09-15"
    assert stamped[1]["created_at"] == "2020-01-01"
    assert stamped[1]["last_verified_at"] == "2026-09-15"


def test_stamp_app_dates_backfills_undated_catalog_with_legacy():
    today = datetime.date(2026, 9, 15)
    raw = [{"id": 1, "title": "a"}, {"id": 2, "title": "b"}]
    stamped = gs.stamp_app_dates(raw, today=today)
    assert stamped[0]["created_at"] == "2022-06-01"
    assert stamped[1]["created_at"] == "2022-06-01"
    assert stamped[0]["last_verified_at"] == "2026-09-15"
    assert stamped[1]["last_verified_at"] == "2026-09-15"


# --- load / dump -------------------------------------------------------------


def test_load_db_validates_and_returns_apps(workspace, sample_apps):
    gs.dump_db(sample_apps)
    loaded = gs.load_db()
    assert [app.id for app in loaded] == [1, 2]
    assert loaded[0].title.eng == "Alpha"
    assert gs.DB_PATH.exists()


def test_load_db_exits_on_invalid_catalog(workspace):
    gs.DB_PATH.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "link": "https://example.com",
                    "title": {"pl": "", "eng": "T"},
                    "description": {"pl": "", "eng": "D"},
                    "authors": [{"name": "A"}],
                    "tags": ["notARealTag"],
                }
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="Invalid catalog"):
        gs.load_db()


def test_dump_db_roundtrip_excludes_none_and_pretty_prints(workspace, sample_apps):
    gs.dump_db(sample_apps)
    raw = json.loads(gs.DB_PATH.read_text(encoding="utf-8"))
    assert raw[0]["authors"][0]["link"] == "https://ada.example"
    assert "link" not in raw[1]["authors"][0]
    assert gs.DB_PATH.read_text(encoding="utf-8").endswith("\n")
    assert "created_at" in raw[0]
    assert "last_verified_at" in raw[0]


def test_real_db_fixed_json_loads():
    apps = gs.load_db(
        Path(__file__).resolve().parents[1]
        / "assets"
        / "original_article"
        / "db-fixed.json"
    )
    assert len(apps) >= 1
    assert all(app.id >= 1 for app in apps)


# --- generate_tags / create_html ---------------------------------------------


def test_generate_tags_writes_json_and_script_js(workspace, sample_apps):
    tags = gs.generate_tags(sample_apps)
    assert [t["tag"] for t in tags] == ["forKids", "game", "tool"]
    assert tags[0]["desc"] == gs.TAGS_DESCRIPTORS["forKids"]

    saved = json.loads(gs.TAGS.read_text(encoding="utf-8"))
    assert saved == tags

    first_line = gs.JS_PATH.read_text(encoding="utf-8").splitlines()[0]
    assert first_line.startswith("const CATEGORIES = ")
    assert "forKids" in first_line
    assert gs.JS_PATH.read_text(encoding="utf-8").splitlines()[1] == "function noop() {}"


def test_create_html_english(workspace, sample_apps):
    gs.create_html(sample_apps, lang="eng")
    html = gs.HTML_OUTPUT.read_text(encoding="utf-8")

    assert 'id="webapps"' in html
    assert 'id="1"' in html
    assert "Alpha" in html
    assert "Alpha desc" in html
    assert "<a href='https://ada.example'>Ada</a>" in html
    assert "Betty" in html
    assert "No Link Author" in html
    assert "#game" in html
    assert "Related links:" in html
    assert "https://example.com/more" in html
    assert "[TODO TRANSLATE] Beta PL" in html
    assert "[TODO TRANSLATE] Opis beta" in html


def test_create_html_polish(workspace, sample_apps):
    gs.create_html(sample_apps, lang="pl")
    html = gs.HTML_OUTPUT.read_text(encoding="utf-8")
    assert "Alfa" in html
    assert "Opis alfa" in html
    assert "Beta PL" in html
    assert "[TODO TRANSLATE]" not in html


# --- HTML replacement --------------------------------------------------------


def test_replace_apps_html_injects_output_fragment(workspace, sample_apps):
    gs.create_html(sample_apps, lang="eng")
    gs.replace_apps_html()
    apps_html = gs.APPS_PAGE_PATH.read_text(encoding="utf-8")
    assert "OLD WEBAPPS" not in apps_html
    assert 'id="1"' in apps_html
    assert "Alpha" in apps_html


def test_replace_tags_html_writes_examples(workspace, sample_apps):
    gs.replace_tags_html(sample_apps)
    page = gs.TAGS_PAGE_PATH.read_text(encoding="utf-8")
    assert "OLD LEFT" not in page
    assert "OLD RIGHT" not in page
    assert "#game" in page
    assert "#forKids" in page
    assert "#tool" in page
    assert "Example app:" in page
    assert "Alpha" in page


def test_generate_navbar_and_head_marks_current_page(workspace, sample_apps):
    sample_apps[0].last_verified_at = datetime.date(2026, 9, 15)
    sample_apps[1].last_verified_at = datetime.date(2024, 1, 2)
    gs.generate_navbar_and_head(sample_apps)

    apps = (workspace / "apps.html").read_text(encoding="utf-8")
    index = (workspace / "index.html").read_text(encoding="utf-8")

    assert 'class="onblack onblack-current" href="/apps"' in apps
    assert 'class="onblack onblack-current" href="/"' in index
    assert "WEB MUSIC APPS FOR EVERYBODY" in apps
    assert "webmusic.pages.dev" in apps
    assert "Last updated: 15 September 2026" in apps
    assert "Last updated: 15 September 2026" in index
    assert 'class="site-footer"' in apps


# --- higher-level flows ------------------------------------------------------


def test_prettify_db_sorts_tags_and_titles(workspace, monkeypatch):
    today = datetime.date(2026, 9, 15)
    raw = [
        {
            "id": 10,
            "link": "https://example.com/z",
            "title": {"pl": "", "eng": "Zebra App"},
            "description": {"pl": "", "eng": "z"},
            "authors": [{"name": "Z"}],
            "tags": ["tool", "game"],
            "created_at": "2020-01-01",
        },
        {
            "id": 11,
            "link": "https://example.com/a",
            "title": {"pl": "", "eng": "!!!Apple!!"},
            "description": {"pl": "", "eng": "a"},
            "authors": [{"name": "A"}],
            "tags": ["forKids"],
        },
    ]
    gs.DB_PATH.write_text(json.dumps(raw), encoding="utf-8")

    original_stamp = gs.stamp_app_dates

    def stamp_fixed(apps, *, today=None):
        return original_stamp(apps, today=datetime.date(2026, 9, 15))

    monkeypatch.setattr(gs, "stamp_app_dates", stamp_fixed)
    gs.prettify_db()

    loaded = gs.load_db()
    assert [app.title.eng for app in loaded] == ["!!!Apple!!", "Zebra App"]
    assert loaded[1].tags == ["game", "tool"]
    assert loaded[0].created_at == today
    assert loaded[0].last_verified_at == today
    assert loaded[1].created_at == datetime.date(2020, 1, 1)
    assert loaded[1].last_verified_at == today


def test_generate_website_end_to_end(workspace, sample_apps, capsys):
    gs.dump_db(sample_apps)
    gs.generate_website()

    assert gs.TAGS.exists()
    assert gs.HTML_OUTPUT.exists()
    assert "Alpha" in gs.APPS_PAGE_PATH.read_text(encoding="utf-8")
    assert "#game" in gs.TAGS_PAGE_PATH.read_text(encoding="utf-8")
    assert "const CATEGORIES =" in gs.JS_PATH.read_text(encoding="utf-8")
    apps_html = (workspace / "apps.html").read_text(encoding="utf-8")
    assert "onblack-current" in apps_html
    assert "Last updated:" in apps_html
    assert 'class="site-footer"' in apps_html

    out = capsys.readouterr().out
    assert "Database JSON validated" in out
    assert "Script finished" in out
