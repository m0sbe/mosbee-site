#!/usr/bin/env python3
"""Build m0sbee.com into docs/ (served by GitHub Pages).

src/layout.html          page skeleton: head, header, scripts
src/pages/home.<lang>    main page content, written by hand per language
src/partials/            contact, footer, json-ld
src/cases/<slug>.json    one file per case, texts for en and ru
src/static/              css, js, img and other files copied as is

Usage: python3 build.py [version]   (version goes into ?v= of css/js links)
"""
import html
import json
import shutil
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
SITE = "https://m0sbee.com"
LANGS = ("en", "ru")

TEXT = {
    "en": {
        "logo_label": "mosbee — home",
        "nav_label": "Navigation",
        "menu_label": "Menu",
        "back": "← all cases",
        "next": "next case",
        "view": "view case →",
        "og_locale": "en_US",
        "home_title": "Dmitry Tushnolobov — Remote Web &amp; Digital Brand Designer | mosbee",
        "home_description": "Remote digital designer: websites, UI, e-commerce and digital brand systems for B2B clients, with AI-assisted design workflows. Selected cases and contacts.",
        "home_og_description": "Remote digital designer: websites, UI, e-commerce and digital brand systems for B2B clients, with AI-assisted design workflows.",
    },
    "ru": {
        "logo_label": "mosbee — на главную",
        "nav_label": "Навигация",
        "menu_label": "Меню",
        "back": "← все кейсы",
        "next": "следующий кейс",
        "view": "смотреть кейс →",
        "og_locale": "ru_RU",
        "home_title": "Дмитрий Тушнолобов — веб-дизайн, брендинг, полиграфия | mosbee",
        "home_description": "Дизайн сайтов, фирменного стиля, упаковки и полиграфии для B2B-компаний. Кейсы, предварительное проектирование и контакты. Работаю удалённо.",
        "home_og_description": "Дизайн сайтов, фирменного стиля, упаковки и полиграфии для B2B-компаний. Работаю удалённо.",
    },
}

OG_DEFAULT = {"og_image": f"{SITE}/img/og.png", "og_image_w": "1200", "og_image_h": "630",
              "og_image_alt": "mosbee — Dmitry Tushnolobov, web &amp; digital brand designer"}

SCRIPTS_HOME = """<script src="/js/main.js?v={v}" defer></script>
<script type="module" src="/js/logo3d.js?v={v}"></script>
<script type="module" src="/js/tools3d.js?v={v}"></script>"""
SCRIPTS_PAGE = """<script src="/js/main.js?v={v}" defer></script>"""


def read(path):
    return (SRC / path).read_text(encoding="utf-8")


def fill(template, values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    if "{{" in template:
        start = template.index("{{")
        raise SystemExit(f"unfilled placeholder: {template[start:start + 40]}")
    return template


def path_for(lang, rest=""):
    """Site path of a page: en lives at the root, ru under /ru/."""
    return ("/" if lang == "en" else "/ru/") + rest


def lang_switch(paths, current):
    current_attr = ' aria-current="page"'
    links = "".join(
        f'<a href="{paths[l]}"{current_attr if l == current else ""}>{l}</a>' for l in LANGS)
    return f'<div class="lang">{links}</div>'


def page(lang, paths, main, title, description, og_description, scripts, v,
         anchor="", og_type="website", og=None, jsonld=""):
    t = TEXT[lang]
    other = "ru" if lang == "en" else "en"
    switch = lang_switch(paths, lang)
    return fill(read("layout.html"), {
        "lang": lang,
        "title": title,
        "description": description,
        "og_description": og_description,
        "url": SITE + paths[lang],
        "url_en": SITE + paths["en"],
        "url_ru": SITE + paths["ru"],
        "og_type": og_type,
        "og_locale": t["og_locale"],
        "og_locale_alt": TEXT[other]["og_locale"],
        **(og or OG_DEFAULT),
        "jsonld": jsonld,
        "v": v,
        "home": path_for(lang),
        "anchor": anchor,
        "logo_label": t["logo_label"],
        "nav_label": t["nav_label"],
        "menu_label": t["menu_label"],
        "lang_switch": switch,
        "main": main.replace("{{lang_switch}}", switch),
        "scripts": scripts.format(v=v),
    })


def case_main(lang, case, next_case):
    d = case[lang]
    t = TEXT[lang]
    home = path_for(lang)
    parts = [f"""
  <section class="section case-page" aria-labelledby="case-title">
    <a class="label case-page__back" href="{home}#cases">{t["back"]}</a>
    <p class="label case-page__label">{d["label"]}</p>
    <h1 class="h-xl case-page__title" id="case-title">{d["title"]}</h1>
    <p class="case-page__lead">{d["lead"]}</p>
    <p class="label case-page__tags">{d["tags"]}</p>
  </section>

  <section class="section case-page__cover">
    <img src="{case["cover"]}" alt="{html.escape(d["cover_alt"])}" width="{case["cover_w"]}" height="{case["cover_h"]}" style="max-width: {case["cover_w"]}px">
  </section>
"""]
    for block in d.get("sections", []):
        images = "".join(
            f'\n      <img src="{img["src"]}" alt="{html.escape(img.get("alt", ""))}" width="{img["w"]}" height="{img["h"]}" loading="lazy">'
            for img in block.get("images", []))
        heading = f'\n      <h2 class="h-lg">{block["heading"]}</h2>' if block.get("heading") else ""
        text = f'\n      <p class="text">{block["text"]}</p>' if block.get("text") else ""
        parts.append(f"""
  <section class="section case-page__block reveal">
    <div class="case-page__block-text">{heading}{text}
    </div>
    <div class="case-page__images">{images}
    </div>
  </section>
""")
    if next_case:
        n = next_case[lang]
        parts.append(f"""
  <a class="section case-page__next" href="{path_for(lang, "cases/" + next_case["slug"] + "/")}">
    <span class="label">{t["next"]} →</span>
    <span class="h-lg">{n["title"]}</span>
  </a>
""")
    parts.append("\n" + read(f"partials/contact.{lang}.html") + read(f"partials/footer.{lang}.html"))
    return "".join(parts)


def main():
    v = sys.argv[1] if len(sys.argv) > 1 else time.strftime("%Y%m%d%H%M%S")
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "static", OUT)

    cases = sorted((json.loads(p.read_text(encoding="utf-8")) for p in (SRC / "cases").glob("*.json")),
                   key=lambda c: c["order"])
    sitemap = []

    home_paths = {l: path_for(l) for l in LANGS}
    for lang in LANGS:
        t = TEXT[lang]
        main_html = read(f"pages/home.{lang}.html") + read(f"partials/contact.{lang}.html") + read(f"partials/footer.{lang}.html")
        out = page(lang, home_paths, main_html, t["home_title"], t["home_description"], t["home_og_description"],
                   SCRIPTS_HOME, v, jsonld=read("partials/jsonld.html"))
        target = OUT / home_paths[lang].lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding="utf-8")
    sitemap.append(home_paths)

    for i, case in enumerate(cases):
        next_case = cases[(i + 1) % len(cases)] if len(cases) > 1 else None
        paths = {l: path_for(l, f"cases/{case['slug']}/") for l in LANGS}
        og = {"og_image": SITE + case["cover"], "og_image_w": str(case["cover_w"]),
              "og_image_h": str(case["cover_h"]), "og_image_alt": html.escape(case["en"]["cover_alt"])}
        for lang in LANGS:
            d = case[lang]
            out = page(lang, paths, case_main(lang, case, next_case), d["meta_title"], html.escape(d["lead"]),
                       html.escape(d["lead"]), SCRIPTS_PAGE, v, anchor=path_for(lang), og_type="article", og=og)
            target = OUT / paths[lang].lstrip("/") / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(out, encoding="utf-8")
        sitemap.append(paths)

    today = date.today().isoformat()
    urls = []
    for paths in sitemap:
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE}{paths[l]}"/>' for l in LANGS)
        alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{paths["en"]}"/>'
        for l in LANGS:
            urls.append(f"  <url>\n    <loc>{SITE}{paths[l]}</loc>\n    <lastmod>{today}</lastmod>{alts}\n  </url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

    print(f"built {2 + 2 * len(cases)} pages into docs/, version {v}")


if __name__ == "__main__":
    main()
