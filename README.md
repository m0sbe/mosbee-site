# mosbee.ru

Portfolio site. Sources in `src/`, built pages in `docs/` (uploaded to the FirstVDS server, nginx of the ispmanager panel).

- `src/pages/home.en.html`, `src/pages/home.ru.html` — main pages, each language written by hand
- `src/cases/<slug>.json` — one file per case (texts for en and ru, images); a page is built for each
- `src/partials/` — contact block, footer, JSON-LD
- `src/static/` — css, js, images, verification files (copied as is)
- `src/layout.html` — head, header, scripts shared by all pages

Publish: `./deploy.sh "what changed"` (runs `build.py`, uploads `docs/` to the server over rsync, then commits and pushes the sources to GitHub as a backup). Server: `ssh oil-server`, folder `/var/www/oil/data/www/mosbee.ru`.

## Language of the root page

nginx decides it for `/` only (file `/etc/nginx/conf.d/mosbee-lang.conf` on the server, hooked in via
`/etc/nginx/vhosts-resources/mosbee.ru/lang.conf`): `/ru/` when the browser's first language is Russian,
`/` (en) otherwise. The en/ru switcher stores the choice in a `lang` cookie for a year, which wins over the browser language.
Search bots and link previews are never redirected.
