# m0sbee.com

Portfolio site. Sources in `src/`, built pages in `docs/` (served by GitHub Pages).

- `src/pages/home.en.html`, `src/pages/home.ru.html` — main pages, each language written by hand
- `src/cases/<slug>.json` — one file per case (texts for en and ru, images); a page is built for each
- `src/partials/` — contact block, footer, JSON-LD
- `src/static/` — css, js, images, CNAME, verification files (copied as is)
- `src/layout.html` — head, header, scripts shared by all pages

Publish: `./deploy.sh "what changed"` (runs `build.py`, commits, pushes).
