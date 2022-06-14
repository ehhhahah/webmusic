import json
import re
from bs4 import BeautifulSoup
import datetime

HTML_OUTPUT = '/Users/Guested/Documents/GitHub/webmusic/assets/original_article/output.html'
TAGS = '/Users/Guested/Documents/GitHub/webmusic/assets/original_article/tags.json'
APPS_PAGE_PATH = 'apps.html'
TAGS_PAGE_PATH = 'tagsinfo.html'
ALL_PAGES = ['index.html', 'apps.html', 'evaluation.html', 'submit.html', 'tagsinfo.html']
JS_PATH = 'script.js'

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

"tool":"Useful to musicians and producers.",

"visual":"Nice for people with limited hearing, focused more on visual aspect.",
}

def handle_set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError

def generate_tags(OUTPUT):
    def change_first_file_line(tags):
        with open(JS_PATH) as f:
            lines = f.readlines()
        lines # ['This is the first line.\n', 'This is the second line.\n']
        lines[0] = f"const CATEGORIES = {tags};\n"
        lines # ["This is the line that's replaced.\n", 'This is the second line.\n']
        with open(JS_PATH, "w") as f:
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

    with open(TAGS, 'w') as fp:
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

            # TODO temp code
            if lang == 'eng' and not author_name:
                author_name = author['name']['pl']

            is_link = 'link' in author and author['link']
            if is_link:
                out += f"<a href='{author['link']}'>{author_name}</a>"
            else:
                out += author_name
        return out
    def get_more_links(more_links):
        # TODO ? what is this ?
        pass

    html_content = '<div id="webapps" class="webapps g-4">'
    for app in parsed_json:
        tags = " ".join(app["tags"]) if "tags" in app else " "
        hashtags = " ".join([f"<span class='tag' title='{TAGS_DESCRIPTORS[tag]}'>#" + tag + "</span>" for tag in tags.split(" ")])

        more_links = """<div class="card-footer">
        <ul class="list-group list-group-flush">Related links:""" + "".join(f"""
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
        <h5 class="card-title"><a href="{app['link']}" target="_blank">{title}</a></h5>
        <p class="card-text idinfo"><a href="https://webmusic.pages.dev/apps#{id}">#{id}</a></p>
        </div>
        <h6 class="card-subtitle mb-2 text-muted">Authors: {get_authors(app['authors'])}</h6>
        <p class="card-text">{description}</p>
        <p class="tags">{hashtags}</p>
        {more_links}
        </div>
        """

    html_content += "</div>"
    with open(HTML_OUTPUT, 'w') as file:
        file.write(html_content)

def replace_tags_html():
    with open('/Users/Guested/Documents/GitHub/webmusic/assets/original_article/db-fixed.json') as f:
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
    with open(TAGS_PAGE_PATH, 'r+') as html:
        soup = BeautifulSoup(html.read(), 'html.parser')
        webapps = soup.find(class_="flex-item-left")
        webapps.replace_with(f"<div class='flex-item-left'>{tags_last_half}</div>")
        webapps = soup.find(class_="flex-item-right")
        webapps.replace_with(f"<div class='flex-item-right'>{tags_first_half}</div>")
    with open(TAGS_PAGE_PATH, 'w', encoding='utf-8') as html:
        html.write(soup.prettify(formatter=None))

def replace_apps_html():
    with open(APPS_PAGE_PATH, 'r+') as html:
        soup = BeautifulSoup(html.read(), 'html.parser')
        with open(HTML_OUTPUT, 'r') as file:
            webapps = soup.find(id="webapps")
            webapps.replace_with(file.read())
    with open(APPS_PAGE_PATH, 'w', encoding='utf-8') as html:
        html.write(soup.prettify(formatter=None))

def generate_navbar_and_head():
    for page in ALL_PAGES:
        with open(page, 'r+') as html:
            soup = BeautifulSoup(html.read(), 'html.parser')

            navbar_html = f"""
<div class="navbary is-black is-spaced has-shadow">
        <a class="onblack{' onblack-current' if page.startswith('apps') else ''}" href="/apps">Apps</a>
        <a class="onblack{' onblack-current' if page.startswith('about') or page.startswith('index') else ''}" href="/">About</a>
        <a class="onblack{' onblack-current' if page.startswith('evaluation') else ''}" href="/evaluation">Evaluate</a>
        <a class="onblack{' onblack-current' if page.startswith('submit') else ''}" href="/submit">Submit new</a>
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
  <link href="https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css" rel="stylesheet"/>
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
    with open('/Users/Guested/Documents/GitHub/webmusic/assets/original_article/db-fixed.json') as f:
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
    with open('/Users/Guested/Documents/GitHub/webmusic/assets/original_article/db-fixed.json') as f:
        json_file = json.load(f)
    for app in json_file:
        app['tags'] = sorted(app['tags'], key=str.lower)

    sorted_dict = sorted(
        json_file,
        key=lambda x: re.sub('[^A-Za-z]+', '', x["title"]["eng"]).lower()
    )

    with open('/Users/Guested/Documents/GitHub/webmusic/assets/original_article/db-fixed.json', 'w') as file:
        file.write(json.dumps(sorted_dict, indent=4))

if __name__ == "__main__":
    prettify_db()
    generate_website()

prettify_db()