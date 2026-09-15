import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import datetime

# Repo root is two levels above this file: assets/original_article/md_parser.py
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

def handle_set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

def generate_tags(OUTPUT):
    def change_first_file_line(tags):
        with open(JS_PATH, encoding='utf-8') as f:
            lines = f.readlines()
        lines[0] = f"const CATEGORIES = {tags};\n"
        with open(JS_PATH, "w", encoding='utf-8') as f:
            f.writelines(lines)

    all_tags = set()
    for i in OUTPUT:
        try:
            [all_tags.add(tag) for tag in i["tags"]]
        except KeyError:
            continue
        except AttributeError:
            print(f"ATTRIBUTE HERE? {i}")

    tags_with_description = []
    for tag in sorted(all_tags, key=str.lower):
        tags_with_description.append({"tag": tag, "desc": TAGS_DESCRIPTORS[tag]})

    with open(TAGS, 'w', encoding='utf-8') as fp:
        json.dump(tags_with_description, fp, default=handle_set_default)
    # with open(JS_PATH, 'w') as fp:
    #     json.dump(list(all_tags), fp, default=handle_set_default)
    change_first_file_line(tags_with_description)
    return tags_with_description

def create_html(parsed_json, lang="eng"):
    def get_authors(authors):
        out = ""
        for author in authors:
            out += ", " if out != "" else ""
            author_name = author['name'][lang] if lang in author['name'] else author['name']

            if lang == 'eng' and not author_name:
                author_name = author['name']['pl']

            is_link = 'link' in author and author['link']
            if is_link:
                out += f"<a href='{author['link']}'>{author_name}</a>"
            else:
                out += author_name
        return out

    html_content = '<main id="webapps" class="webapps g-4">'
    for app in parsed_json:
        tags = " ".join(app["tags"]) if "tags" in app else " "
        hashtags = " ".join([f"<span class='tag' title='{TAGS_DESCRIPTORS[tag]}'>#" + tag + "</span>" for tag in tags.split(" ")])

        more_links = """<div class="card-footer">
        <ul class="list-group list-group-flush"><li class="list-group-item">Related links:</li>""" + "".join(f"""
        <li class="list-group-item">- <a href='{link['link']}'>{link['name'][lang]}</a></li>""" 
        for link in app["more_links"]) + "</ul></div>" if app["more_links"] else ""
        # TODO add collapsing with accessibility for more links https://getbootstrap.com/docs/5.1/components/collapse/

        if not "link" in app or not "title" in app: continue

        title = app['title'][lang]
        if lang == "eng" and not title:
            title = "[TODO TRANSLATE] " + app['title']['pl']

        description = app['description'][lang]
        if lang == "eng" and not description:
            description = "[TODO TRANSLATE] " + app['description']['pl']

        id = app['id']

        html_content += f"""
        <div class="card h-100 text-center webapp {tags}" id="{id}">
        <div style="display: flex; justify-content: space-between;">
        <h2 class="card-title"><a href="{app['link']}" target="_blank" rel="noopener noreferrer">{title}</a></h2>
        <p class="card-text idinfo"><a href="https://webmusic.pages.dev/apps#{id}">#{id}</a></p>
        </div>
        <p class="card-subtitle mb-2 text-muted">Authors: {get_authors(app['authors'])}</p>
        <p class="card-text">{description}</p>
        <p class="tags">{hashtags}</p>
        {more_links}
        </div>
        """

    html_content += "</main>"
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as file:
        file.write(html_content)

def replace_tags_html():
    with open(DB_PATH, encoding='utf-8') as f:
        database = json.load(f)
        ids_taken = []
    def get_example_tag_app(tag):
        potential_apps = []
        for app in database:
            if tag in app["tags"]:
                potential_apps.append(app)
            
        found_app = None
        if len(potential_apps) <= len(ids_taken):
            found_app = potential_apps[0] 
        else:
            for app in potential_apps:
                if app in ids_taken:
                    continue
                found_app = app
        ids_taken.append(found_app["id"])
        return found_app["title"]["eng"], found_app["link"]

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

SITE_ORIGIN = 'https://webmusic.pages.dev'
OG_IMAGE = f'{SITE_ORIGIN}/assets/webmusic-screenshot1.png'
KEYWORDS = 'music web apps kids accessible'
AUTHOR = 'Wojtek Węgrzyn, Dominik Oczoś'

PAGE_META = {
    'index.html': {
        'title': 'About | Web Music Apps For Everybody',
        'description': (
            'Online platform for musical apps available in the browser that lets users '
            'filter them by accessibility for different groups of people. Applications '
            'strictly related to creating, generating, learning or editing music.'
        ),
        'path': '/',
    },
    'apps.html': {
        'title': 'Apps | Web Music Apps For Everybody',
        'description': (
            'Browse and filter browser-based music apps by accessibility and category '
            'tags — for kids, limited vision, open source tools, sequencers, and more.'
        ),
        'path': '/apps',
    },
    'submit.html': {
        'title': 'Submit | Web Music Apps For Everybody',
        'description': (
            'Suggest a new browser-based music app to add to the Web Music Apps For '
            'Everybody catalog.'
        ),
        'path': '/submit',
    },
    'evaluation.html': {
        'title': 'Evaluate | Web Music Apps For Everybody',
        'description': (
            'Share feedback on browser music apps to help improve accessibility for '
            'users with visual impairment and other needs.'
        ),
        'path': '/evaluation',
    },
    'tagsinfo.html': {
        'title': 'Tags info | Web Music Apps For Everybody',
        'description': (
            'Explanations of the accessibility and category tags used to filter apps '
            'on Web Music Apps For Everybody.'
        ),
        'path': '/tagsinfo',
    },
}

def make_head_html(page_name):
    meta = PAGE_META[page_name]
    title = meta['title']
    description = meta['description']
    url = f"{SITE_ORIGIN}{meta['path']}" if meta['path'] != '/' else f'{SITE_ORIGIN}/'
    return f"""
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <base href="{SITE_ORIGIN}/"/>
  <title>{title}</title>
  <meta name="description" content="{description}"/>
  <meta content="{KEYWORDS}" name="keywords"/>
  <meta content="{AUTHOR}" name="author"/>
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website"/>
  <meta property="og:url" content="{url}"/>
  <meta property="og:title" content="{title}"/>
  <meta property="og:description" content="{description}"/>
  <meta property="og:image" content="{OG_IMAGE}"/>
  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image"/>
  <meta property="twitter:url" content="{url}"/>
  <meta property="twitter:title" content="{title}"/>
  <meta property="twitter:description" content="{description}"/>
  <meta property="twitter:image" content="{OG_IMAGE}"/>
  <link href="images/apple-touch-icon.png" rel="apple-touch-icon" sizes="180x180"/>
  <link href="images/favicon-32x32.png" rel="icon" sizes="32x32" type="image/png"/>
  <link href="images/favicon-16x16.png" rel="icon" sizes="16x16" type="image/png"/>
  <!-- external hrefs -->
  <link href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com" rel="preconnect"/>
  <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet"/>
  <!-- internal hrefs (after Bulma so custom rules win) -->
  <link href="styledark.css" rel="stylesheet"/>
  <link href="site.webmanifest" rel="manifest"/>
</head>
"""

def fix_page_markup(soup, page_name):
    """Durable body/markup fixes that are not replaced by card injection."""
    if page_name == 'apps.html':
        container = soup.find(id=re.compile(r'^container'))
        if container is not None:
            # Invalid id with a space → split into id + class
            bad_id = container.get('id', '')
            if ' ' in bad_id:
                parts = bad_id.split()
                container['id'] = parts[0]
                existing = container.get('class', [])
                for cls in parts[1:]:
                    if cls not in existing:
                        existing.append(cls)
                container['class'] = existing
            elif 'has-navbar-fixed-top' not in container.get('class', []):
                classes = container.get('class', [])
                classes.append('has-navbar-fixed-top')
                container['class'] = classes

        # Avoid nested interactive controls: <a><button>…</button></a>
        for button in soup.select('a > button.button'):
            link = button.parent
            if link.name != 'a':
                continue
            link['class'] = list(dict.fromkeys(
                (link.get('class') or []) + (button.get('class') or [])
            ))
            href = link.get('href') or ''
            if not href or href.endswith('tagsinfo.html'):
                link['href'] = '/tagsinfo'
            text = button.get_text(strip=True) or 'Tags info'
            link.clear()
            link.append(text)

    if page_name == 'index.html':
        for heading in soup.find_all(['h2', 'h3'], class_='info'):
            if heading.get_text(strip=True) != 'About website':
                continue
            if heading.name != 'h2':
                heading.name = 'h2'
            sibling = heading.find_next_sibling()
            if sibling is not None and sibling.name == 'h2' and 'biginfo' in (sibling.get('class') or []):
                sibling.name = 'p'
            break

    if page_name == 'evaluation.html':
        for link in soup.find_all('a', href='/apps.html'):
            link['href'] = '/apps'

def generate_navbar_and_head():
    for page in ALL_PAGES:
        with open(page, 'r+', encoding='utf-8') as html:
            soup = BeautifulSoup(html.read(), 'html.parser')

            page_name = page.name
            navbar_html = f"""
<nav class="navbary is-black is-spaced has-shadow" aria-label="Primary">
        <a class="onblack{' onblack-current' if page_name.startswith('apps') else ''}" href="/apps">Apps</a>
        <a class="onblack{' onblack-current' if page_name.startswith('about') or page_name.startswith('index') else ''}" href="/">About</a>
        <a class="onblack{' onblack-current' if page_name.startswith('evaluation') else ''}" href="/evaluation">Evaluate</a>
        <a class="onblack{' onblack-current' if page_name.startswith('submit') else ''}" href="/submit">Submit new</a>
    </nav>"""
            header_html = """
            <header>
     <h1 id="pageTitle">
      WEB MUSIC APPS FOR EVERYBODY
     </h1>
    </header>
            """

            head_html = make_head_html(page_name)

            navbar = soup.find_all(class_="navbary")[0]
            navbar.replace_with(BeautifulSoup(navbar_html, 'html.parser'))

            header = soup.find("header")
            header.replace_with(BeautifulSoup(header_html, 'html.parser'))

            head = soup.find("head")
            head.replace_with(BeautifulSoup(head_html, 'html.parser'))

            fix_page_markup(soup, page_name)
        with open(page, 'w', encoding='utf-8') as html:
            html.write(soup.prettify(formatter=None))

def log_info(message):
    print(f"[INFO | {datetime.datetime.now()}] {message}")

def generate_website():
    with open(DB_PATH, encoding='utf-8') as f:
        OUTPUT = json.load(f)
    log_info(f"Database JSON received. Got {len(OUTPUT)} objects")
    tags = generate_tags(OUTPUT)
    log_info(f"Generated {len(tags)} tags and saved them to {JS_PATH}")
    create_html(OUTPUT, lang="eng")
    log_info(f"Created new HTML on path: {HTML_OUTPUT}")
    replace_apps_html()
    log_info(f"Replaced apps.html path: {APPS_PAGE_PATH}")
    replace_tags_html()
    log_info("Generated tagsinfo page")
    generate_navbar_and_head()
    log_info(f"Replaced the navbar and head for: {ALL_PAGES}")
    log_info("Script finished")

def prettify_db():
    with open(DB_PATH, encoding='utf-8') as f:
        json_file = json.load(f)
    for app in json_file:
        app['tags'] = sorted(app['tags'], key=str.lower)

    sorted_dict = sorted(
        json_file,
        key=lambda x: re.sub('[^A-Za-z]+', '', x["title"]["eng"]).lower()
    )

    with open(DB_PATH, 'w', encoding='utf-8') as file:
        file.write(json.dumps(sorted_dict, indent=4))

if __name__ == "__main__":
    prettify_db()
    generate_website()
