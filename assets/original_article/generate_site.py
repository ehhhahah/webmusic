import datetime
import json
import re
from pathlib import Path
from typing import Annotated

from bs4 import BeautifulSoup
from pydantic import (
    BaseModel,
    Field,
    RootModel,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

# Repo root is two levels above this file: assets/original_article/generate_site.py
ROOT = Path(__file__).resolve().parents[2]
ARTICLE_DIR = Path(__file__).resolve().parent

HTML_OUTPUT = ARTICLE_DIR / 'output.html'
TAGS = ARTICLE_DIR / 'tags.json'
DB_PATH = ARTICLE_DIR / 'db-fixed.json'
APPS_PAGE_PATH = ROOT / 'apps.html'
TAGS_PAGE_PATH = ROOT / 'tagsinfo.html'
ALL_PAGES = [ROOT / name for name in (
    'index.html', 'apps.html', 'evaluation.html', 'submit.html', 'tagsinfo.html'
)]
JS_PATH = ROOT / 'script.js'

TAGS_DESCRIPTORS = {
"12+":"For users older than 12.",

"AI":"Artificial intelligence technologies used.",

"DAW":"Digital audio workstation, a lot of audio modulation/creating functionality.",

"DIY":"Do it yourself, app made by single person and/or low-budget.",

"FreeSound":"Use of FreeSound samples library.",

"accessible":"General accessible app - for users with any impairment.",

"ambient":"Relaxing, soft or slow-paced music.",

"backgroundMuzak":"Music to be put in background, low listening effort expected.",

"bigTech":"Created by big technological company.",

"classic":"Well-known, popular project, gained huge audacity.",

"classical":"Related to classical music.",

"commercial":"App made for profit purposes.",

"composing":"Apps that allow to compose a new and unique piece of music by user.",

"descriptive":"Reading description or attached text is needed, app is mainly based on text.",

"forKids":"Good for kids in any age.",

"game":"Playful, focused on having fun.",

"learn":"App that shares some knowledge.",

"longRead":"A lot of reading is needed.",

"limitedVision": "Accessible for users with vision impairment (for example good contrast ratios, font size is big enought).",

"marpi":"With use of Marpi platform (Web3GL engine, not accessible for screen readers).",

"math":"Some math knowledge is required.",

"mustCheck":"The best apps selection.",

"noveltyArt": "New and unique piece of art, presented in a form of website.",

"openSource":"Source code is publicly available.",

"physic":"Some physic knowledge is required.",

"realTime":"Works on real time data.",

"reconstruction":"Previously published piece, reconstructed in the form of webstie.",

"seizureWarning":"May contain flashing lights.",

"sequencer":"App based on simple sound sequences.",

"smallBandwidth": "Slow network users should not have issues with opening and using the app.",

"tool":"Useful to musicians and producers.",

"visual":"Nice for people with limited hearing, focused more on visual aspect."
}

KNOWN_TAGS = frozenset(TAGS_DESCRIPTORS)


class LocalizedText(BaseModel):
    pl: str = ""
    eng: str = ""


class Author(BaseModel):
    name: str | LocalizedText
    link: str | None = None


class MoreLink(BaseModel):
    name: LocalizedText
    link: str


class App(BaseModel):
    authors: list[Author]
    title: LocalizedText
    link: str
    description: LocalizedText
    tags: list[str]
    more_links: list[MoreLink] = Field(default_factory=list)
    id: Annotated[int, Field(ge=1)]

    @field_validator("link")
    @classmethod
    def link_must_be_nonempty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("link must be non-empty")
        return value

    @field_validator("tags")
    @classmethod
    def tags_must_be_known(cls, tags: list[str]) -> list[str]:
        unknown = sorted({tag for tag in tags if tag not in KNOWN_TAGS})
        if unknown:
            raise ValueError(f"unknown tag(s): {', '.join(unknown)}")
        return tags


class Catalog(RootModel[list[App]]):
    @model_validator(mode="after")
    def ids_must_be_unique(self) -> "Catalog":
        ids = [app.id for app in self.root]
        duplicates = sorted({app_id for app_id in ids if ids.count(app_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate app id(s): {', '.join(map(str, duplicates))}")
        return self


def load_db(path: Path = DB_PATH) -> list[App]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    try:
        return Catalog.model_validate(raw).root
    except ValidationError as exc:
        raise SystemExit(f"Invalid catalog in {path}:\n{exc}") from exc


def dump_db(apps: list[App], path: Path = DB_PATH) -> None:
    payload = TypeAdapter(list[App]).dump_python(apps, exclude_none=True)
    path.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")


def localized_value(value: str | LocalizedText, lang: str) -> str:
    if isinstance(value, str):
        return value
    text = getattr(value, lang, "") or ""
    if lang == "eng" and not text:
        return value.pl
    return text


def generate_tags(apps: list[App]):
    def change_first_file_line(tags):
        with open(JS_PATH, encoding='utf-8') as f:
            lines = f.readlines()
        lines[0] = f"const CATEGORIES = {tags};\n"
        with open(JS_PATH, "w", encoding='utf-8') as f:
            f.writelines(lines)

    all_tags = {tag for app in apps for tag in app.tags}
    tags_with_description = [
        {"tag": tag, "desc": TAGS_DESCRIPTORS[tag]}
        for tag in sorted(all_tags, key=str.lower)
    ]

    with open(TAGS, 'w', encoding='utf-8') as fp:
        json.dump(tags_with_description, fp)
    change_first_file_line(tags_with_description)
    return tags_with_description

def create_html(apps: list[App], lang="eng"):
    def get_authors(authors: list[Author]):
        out = ""
        for author in authors:
            out += ", " if out != "" else ""
            author_name = localized_value(author.name, lang)

            is_link = bool(author.link)
            if is_link:
                out += f"<a href='{author.link}'>{author_name}</a>"
            else:
                out += author_name
        return out

    html_content = '<div id="webapps" class="webapps g-4">'
    for app in apps:
        tags = " ".join(app.tags)
        hashtags = " ".join(
            f"<span class='tag' title='{TAGS_DESCRIPTORS[tag]}'>#{tag}</span>"
            for tag in app.tags
        )

        more_links = """<div class="card-footer">
        <ul class="list-group list-group-flush"><li class="list-group-item">Related links:</li>""" + "".join(f"""
        <li class="list-group-item">- <a href='{link.link}'>{localized_value(link.name, lang)}</a></li>""" 
        for link in app.more_links) + "</ul></div>" if app.more_links else ""
        # TODO add collapsing with accessibility for more links https://getbootstrap.com/docs/5.1/components/collapse/

        title = app.title.eng if lang == "eng" else app.title.pl
        if lang == "eng" and not app.title.eng:
            title = "[TODO TRANSLATE] " + app.title.pl

        description = app.description.eng if lang == "eng" else app.description.pl
        if lang == "eng" and not app.description.eng:
            description = "[TODO TRANSLATE] " + app.description.pl

        html_content += f"""
        <div class="card h-100 text-center webapp {tags}" id="{app.id}">
        <div style="display: flex; justify-content: space-between;">
        <h2 class="card-title"><a href="{app.link}" target="_blank">{title}</a></h2>
        <p class="card-text idinfo"><a href="https://webmusic.pages.dev/apps#{app.id}">#{app.id}</a></p>
        </div>
        <p class="card-subtitle mb-2 text-muted">Authors: {get_authors(app.authors)}</p>
        <p class="card-text">{description}</p>
        <p class="tags">{hashtags}</p>
        {more_links}
        </div>
        """

    html_content += "</div>"
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as file:
        file.write(html_content)

def replace_tags_html(database: list[App]):
    ids_taken = []
    def get_example_tag_app(tag):
        potential_apps = [app for app in database if tag in app.tags]
            
        found_app = None
        if len(potential_apps) <= len(ids_taken):
            found_app = potential_apps[0] 
        else:
            for app in potential_apps:
                if app.id in ids_taken:
                    continue
                found_app = app
                break
        ids_taken.append(found_app.id)
        return found_app.title.eng, found_app.link

    def make_tag_html(tag_key, tag_desc):
        app_name, app_link = get_example_tag_app(tag_key)
        return f'<h3 class="info">#{tag_key} </h3> <p class="info" style="font-size: 125%;">{tag_desc}</p><p class="info">Example app: <a href={app_link}>{app_name}</a></p>'
    tags = [make_tag_html(tag, tag_desc) for tag, tag_desc in TAGS_DESCRIPTORS.items()]
    half = len(tags)//2

    tags_first_half = " ".join(tags[half:])
    tags_last_half =  " ".join(tags[:half])
    with open(TAGS_PAGE_PATH, 'r+', encoding='utf-8') as html:
        soup = BeautifulSoup(html.read(), 'html.parser')
        webapps = soup.find(class_="flex-item-left")
        webapps.replace_with(f"<div class='flex-item-left'>{tags_last_half}</div>")
        webapps = soup.find(class_="flex-item-right")
        webapps.replace_with(f"<div class='flex-item-right'>{tags_first_half}</div>")
    with open(TAGS_PAGE_PATH, 'w', encoding='utf-8') as html:
        html.write(soup.prettify(formatter=None))

def replace_apps_html():
    with open(APPS_PAGE_PATH, 'r+', encoding='utf-8') as html:
        soup = BeautifulSoup(html.read(), 'html.parser')
        with open(HTML_OUTPUT, 'r', encoding='utf-8') as file:
            webapps = soup.find(id="webapps")
            webapps.replace_with(file.read())
    with open(APPS_PAGE_PATH, 'w', encoding='utf-8') as html:
        html.write(str(soup))

def generate_navbar_and_head():
    for page in ALL_PAGES:
        with open(page, 'r+', encoding='utf-8') as html:
            soup = BeautifulSoup(html.read(), 'html.parser')

            page_name = page.name
            navbar_html = f"""
<div class="navbary is-black is-spaced has-shadow">
        <a class="onblack{' onblack-current' if page_name.startswith('apps') else ''}" href="/apps">Apps</a>
        <a class="onblack{' onblack-current' if page_name.startswith('about') or page_name.startswith('index') else ''}" href="/">About</a>
        <a class="onblack{' onblack-current' if page_name.startswith('evaluation') else ''}" href="/evaluation">Evaluate</a>
        <a class="onblack{' onblack-current' if page_name.startswith('submit') else ''}" href="/submit">Submit new</a>
    </div>"""
            header_html = """
            <header>
     <h1 id="pageTitle">
      WEB MUSIC APPS FOR EVERYBODY
     </h1>
    </header>
            """

            head_html = """
            <head>
  <!-- seo meta -->
  <meta content="music web apps kids accesible" name="keywords"/>
  <meta content="Online platform for musical apps available in the browser that lets users to filter them by its accessibility for different groups of people. Applications that fit the categories and are strictly related to creating, generating, learning or editing music." name="description"/>
  <meta content="Wojtek Węgrzyn, Dominik Oczoś" name="author"/>

  <!-- Primary Meta Tags -->
  <title>Web Music Apps For Everybody</title>
  <meta name="title" content="Web Music Apps For Everybody">
  <meta name="description" content="Online platform for musical apps available in the browser that lets users to filter them by its accessibility for different groups of people. Applications that fit the categories and are strictly related to creating, generating, learning or editing music.">

  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://webmusic.pages.dev/">
  <meta property="og:title" content="Web Music Apps For Everybody">
  <meta property="og:description" content="Online platform for musical apps available in the browser that lets users to filter them by its accessibility for different groups of people. Applications that fit the categories and are strictly related to creating, generating, learning or editing music.">
  <meta property="og:image" content="https://webmusic.pages.dev/assets/webmusic-screenshot1.png">

  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:title" content="Web Music Apps For Everybody">
  <meta property="twitter:description" content="Online platform for musical apps available in the browser that lets users to filter them by its accessibility for different groups of people. Applications that fit the categories and are strictly related to creating, generating, learning or editing music.">
  <meta property="twitter:image" content="https://webmusic.pages.dev/assets/webmusic-screenshot1.png">

  <!-- technical meta -->
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <base href="https://webmusic.pages.dev/">
  <meta charset="utf-8"/>
  <!-- representation meta -->
  <title>
   Web music apps for everybody
  </title>
  <link href="images/apple-touch-icon.png" rel="apple-touch-icon" sizes="180x180"/>
  <link href="images/favicon-32x32.png" rel="icon" sizes="32x32" type="image/png"/>
  <link href="images/favicon-16x16.png" rel="icon" sizes="16x16" type="image/png"/>
  <!-- internal hrefs -->
  <link href="styledark.css" rel="stylesheet"/>
  <link href="site.webmanifest" rel="manifest"/>
  <!-- external hrefs -->
  <link href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com" rel="preconnect"/>
  <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet"/>
 </head>
            """

            navbar = soup.find_all(class_="navbary")[0]
            navbar.replace_with(navbar_html)

            header = soup.find("header")
            header.replace_with(header_html)

            head = soup.find("head")
            head.replace_with(head_html)
        with open(page, 'w', encoding='utf-8') as html:
            html.write(soup.prettify(formatter=None))

def log_info(message):
    print(f"[INFO | {datetime.datetime.now()}] {message}")

def generate_website():
    apps = load_db()
    log_info(f"Database JSON validated. Got {len(apps)} apps")
    tags = generate_tags(apps)
    log_info(f"Generated {len(tags)} tags and saved them to {JS_PATH}")
    create_html(apps, lang="eng")
    log_info(f"Created new HTML on path: {HTML_OUTPUT}")
    replace_apps_html()
    log_info(f"Replaced apps.html path: {APPS_PAGE_PATH}")
    replace_tags_html(apps)
    log_info("Generated tagsinfo page")
    generate_navbar_and_head()
    log_info(f"Replaced the navbar and head for: {ALL_PAGES}")
    log_info("Script finished")

def prettify_db():
    apps = load_db()
    for app in apps:
        app.tags = sorted(app.tags, key=str.lower)

    apps = sorted(
        apps,
        key=lambda app: re.sub('[^A-Za-z]+', '', app.title.eng).lower()
    )
    dump_db(apps)

if __name__ == "__main__":
    prettify_db()
    generate_website()
