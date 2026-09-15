# Web Music Apps For Everybody

Static catalog of browser-based music apps, filterable by accessibility tags.  
Live: [webmusic.pages.dev](https://webmusic.pages.dev/)

## Quick start

```bash
# Node 22 + Python 3.12 via mise (see .mise.toml)
mise install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

pytest -q               # unit tests for generate_site.py

cd cypress-tests && npm install
npm run serve          # http://127.0.0.1:5500  (rewrites <base> for local)
npm run test:ci        # smoke tests
npm run test:ci:all    # smoke + homepage link check
```

Regenerate HTML from the JSON DB:

```bash
source .venv/bin/activate
python assets/original_article/generate_site.py
```

CI: GitHub Actions runs `pytest` and Cypress smoke tests on every push (`.github/workflows/tests.yml`).

## Content model

- Source of truth: `assets/original_article/db-fixed.json` (93 apps)
- Generator: `assets/original_article/generate_site.py` → `apps.html`, `tagsinfo.html`, nav/head, `script.js`
- Site is plain HTML/CSS/JS; no app runtime besides Cypress (dev) and BeautifulSoup (build)

---

<details>
<summary>AI agents info dump</summary>

### What this repo is
- Static multi-page site (Cloudflare Pages): `index.html`, `apps.html`, `evaluation.html`, `submit.html`, `tagsinfo.html`
- Deployed at `https://webmusic.pages.dev/`
- Each page includes `<base href="https://webmusic.pages.dev/">` — **keep this for production**. Do not change it to `/` in committed HTML.
- Local override: `cypress-tests/local-serve.mjs` rewrites that base to `/` only in HTTP responses so assets resolve locally. `npm run serve` uses this. `npm run serve:raw` serves without rewrite.

### JSON DB schema (`db-fixed.json`)
Validated by Pydantic models in `generate_site.py` (`App`, `Catalog`) on every generate.
Array of app objects. Required keys per app:
- `id` (number, unique, ≥ 1)
- `link` (non-empty string URL)
- `title`: `{ "pl": string, "eng": string }`
- `description`: `{ "pl": string, "eng": string }`
- `authors`: `[{ "name": string | {pl, eng}, "link"?: string }]`
- `tags`: `string[]` (each must exist in `TAGS_DESCRIPTORS`)
- `more_links`: `[{ "name": {pl, eng}, "link": string }]` (may be `[]`)
- `created_at` (`YYYY-MM-DD`; missing → treated as new on generate → today; schema fallback `2022-06-01`)
- `last_verified_at` (`YYYY-MM-DD`; always set to today on each `generate_site.py` run)

Related generated files:
- `tags.json` — generated tag list with descriptions
- `output.html` — intermediate fragment injected into `apps.html`

### Generator (`generate_site.py`)
- Reads and validates `db-fixed.json` via Pydantic (`load_db`); paths are repo-relative via `Path(__file__).resolve().parents[2]`
- `prettify_db()` sorts tags + apps, then `generate_website()` rebuilds pages
- Running it rewrites HTML heads/navbars via BeautifulSoup — expect formatting churn
- Tag button data is written as first line of `script.js`: `const CATEGORIES = [...]`
- Client filtering: `script.js` (`hideShowClassElement`, `renderFilteringButtons`)

### Tooling / versions
- `.mise.toml`: `node = "22"`, `python = "3.12"`
- Python deps: `requirements.txt` → `beautifulsoup4`, `pydantic`, `pytest` (use `.venv`)
- Unit tests: `tests/` → `pytest -q`
- Cypress smoke: `cypress-tests` → `npm run test:ci`
- CI: `.github/workflows/tests.yml` runs both on every push
- Cypress lives in `cypress-tests/` only (not a monorepo app)
  - Cypress **16**, config: `cypress.config.js`
  - Specs: `cypress/e2e/smoke.cy.js`, `cypress/e2e/links.cy.js`
  - `baseUrl`: `http://127.0.0.1:5500`
  - Scripts: `test` / `test:ci` = smoke; `test:links` / `test:ci:all` = include links
- `npm audit` expected clean on current lockfile (devDependencies only)
- Pretty URLs: Cloudflare Pages serves `apps.html` at `/apps` natively — **do not** add a `_redirects` rule mapping `/apps` → `/apps.html` (that fights CF’s `/apps.html` → `/apps` redirect and causes `ERR_TOO_MANY_REDIRECTS`). Local pretty URLs are handled by `cypress-tests/local-serve.mjs` (and optional `serve.json` for the `serve` CLI only).

### Tests caveats
- **Smoke tests** assert local pages load, `#webapps` has cards, filter buttons render
- **Links test** visits homepage only (`/index.html`), requests each `<a href>`; logs 4xx as `FUCKERY` but **does not fail** the suite on bad status (legacy behavior). Ignore-list for Cloudflare/anti-bot sites lives in the spec.
- First Cypress run downloads the binary; needs network

### CDN / front-end deps
- Bulma CSS via jsDelivr (`bulma@0.9.4`) — stay on 0.9.x; 1.x is breaking
- Google Fonts: Bebas Neue
- No bundler, no framework

### Do / don’t for agents
- **Do** edit `db-fixed.json` then run `generate_site.py` to refresh listing pages
- **Do** keep production `<base href="https://webmusic.pages.dev/">` in HTML + generator template
- **Do** use `local-serve.mjs` for local verification
- **Don’t** reintroduce hardcoded `/Users/...` paths in `generate_site.py`
- **Don’t** commit `.venv/`, `node_modules/`, Cypress videos/screenshots (see `.gitignore`)
- **Don’t** “upgrade” to Bulma 1 or add a SPA stack unless explicitly asked

### Hosting notes
- Cloudflare Pages project; extensionless routes are built-in (no `_redirects` needed for `.html` pages)
- OG/Twitter meta image: `assets/webmusic-screenshot1.png`
- `robots.txt`, `site.webmanifest`, Google site verification HTML present

</details>
