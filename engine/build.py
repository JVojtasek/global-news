"""Postaví statický web ze složky content/ do složky public/.

Nepotřebuje server, databázi ani Node.js. Výsledek se dá nahrát kamkoli
(Cloudflare Pages, GitHub Pages, obyčejný webhosting).
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
import xml.sax.saxutils as sx

import markdown as md
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import analyst, article, config, images

STRINGS = {
    "en": {
        "briefing_title": "Today in five minutes",
        "section": "Section",
        "sources": "Sources",
        "sources_word": "sources",
        "sources_note": "We report facts from the sources above in our own words and link to the originals. "
                        "Interpretation is ours, not theirs.",
        "confidence": "Confidence",
        "confidence_help": "How strongly this piece is supported by independent sources and passed our review.",
        "nextstep_q": "Every headline has a deeper story. This is ours.",
        "nextstep_cta": "What we are doing here",
        "about": "About us",
        "empty": "Nothing here yet.",
        "footer_note": "Facts first, context second, meaning last — in that order, always. "
                       "We tell you what we know, what we do not, and where the line between them runs.",
        "forecasts_title": "Our forecasts, scored",
        "forecasts_intro": "We publish specific predictions with a probability and a deadline, "
                           "then grade ourselves in public — including when we were wrong.",
        "fc_resolved": "forecasts settled", "fc_brier": "Brier score", "fc_verdict": "verdict",
        "fc_explain": "The Brier score measures calibration. 0.00 is perfect, 0.25 is what you get "
                      "by saying 50% to everything, and anything above 0.30 means we are guessing. "
                      "Nothing is ever deleted from this page.",
        "v_none": "not yet scored", "v_strong": "clearly better than chance",
        "v_good": "better than a coin flip", "v_chance": "no better than chance",
        "v_poor": "worse than chance",
        "fc_open": "Open", "fc_done": "Settled", "fc_void": "Voided — could not be judged fairly",
        "fc_by": "resolves by", "fc_outcome": "Outcome", "fc_yes": "happened", "fc_no": "did not happen",
        "forecasts_link": "Forecasts",
        "republish_title": "Republish our work — free",
        "republish_body": """Our reporting is free to republish under a
[{license}]({license_url}) licence. We would rather our work reached your readers
than sat behind our own logo.

## What you may do

Take any article marked *Free to republish* — the block at the bottom of the page
gives you the full HTML, ready to paste. Print, online, newsletter, all fine, and
you may run advertising alongside it.

## What we ask

**Credit us and link back.** Keep the line at the bottom of the article that says
where it came from, with a working link. That line is the entire price.

**Do not edit the substance.** You may change a headline for your house style and
adjust wording for relative time and place ("yesterday" becomes "last week").
You may not add material, cut the qualifications, or change what a sentence claims.

**Do not sell the article on its own** or place it behind a paywall as a standalone
product.

**Keep the pixel.** The one-pixel image at the end of the block tells us how many
people read it. It collects no personal data and does not track anyone.

**Photographs are not included** unless we say so on the page. Most of our images
are licensed from third parties and you need your own rights to them.

## Translations

Ask us first. We will usually say yes, but we want to see the translated text
before it runs — a bad translation of a careful sentence is worse than no
translation at all.

## Anything else

Write to {email}. We answer.""",
        "related": "Keep reading",
        "newsletter_soon": "The newsletter opens shortly.",
        "republish_offer": "Free to republish",
        "republish_help": "Copy this HTML into your CMS. Credit line and licence are included.",
    },
    "cs": {
        "briefing_title": "Svět dnes za pět minut",
        "section": "Rubrika",
        "sources": "Zdroje",
        "sources_word": "zdrojů",
        "sources_note": "Fakta přebíráme z uvedených zdrojů vlastními slovy a odkazujeme na originály. "
                        "Výklad je náš, ne jejich.",
        "confidence": "Jistota",
        "confidence_help": "Nakolik je text podložen nezávislými zdroji a prošel naší kontrolou.",
        "nextstep_q": "Za každým titulkem je hlubší příběh. Tohle je ten náš.",
        "nextstep_cta": "Co tady vlastně děláme",
        "about": "O nás",
        "empty": "Tady zatím nic není.",
        "footer_note": "Nejdřív fakta, pak souvislosti, teprve pak smysl — v tomhle pořadí, vždycky. "
                       "Říkáme, co víme, co nevíme, a kde mezi tím vede hranice.",
        "forecasts_title": "Naše předpovědi a jak dopadly",
        "forecasts_intro": "Vydáváme konkrétní předpovědi s pravděpodobností a termínem "
                           "a pak si sami veřejně spočítáme, jak jsme dopadli — i když špatně.",
        "fc_resolved": "vyhodnocených", "fc_brier": "Brierovo skóre", "fc_verdict": "hodnocení",
        "fc_explain": "Brierovo skóre měří, jak dobře odhadujeme. 0,00 je dokonalé, 0,25 dostane ten, "
                      "kdo na všechno řekne 50 %, a cokoli nad 0,30 znamená, že hádáme. "
                      "Z téhle stránky se nikdy nic nemaže.",
        "v_none": "zatím nevyhodnoceno", "v_strong": "výrazně lepší než náhoda",
        "v_good": "lepší než hod mincí", "v_chance": "na úrovni náhody",
        "v_poor": "horší než náhoda",
        "fc_open": "Otevřené", "fc_done": "Vyhodnocené", "fc_void": "Zrušené — nešlo poctivě rozhodnout",
        "fc_by": "rozhodne se do", "fc_outcome": "Výsledek", "fc_yes": "stalo se", "fc_no": "nestalo se",
        "forecasts_link": "Předpovědi",
        "republish_title": "Převezměte naše články — zdarma",
        "republish_body": """Naše články jsou volně k převzetí pod licencí
[{license}]({license_url}). Radši budeme, když se dostanou k vašim čtenářům,
než aby zůstaly jen pod naším logem.

## Co smíte

Vzít kterýkoli článek označený *Volně k převzetí* — pod textem najdete blok
s hotovým HTML k vložení. Tisk, web, newsletter, všechno je v pořádku a vedle
článku můžete mít reklamu.

## Co za to chceme

**Uveďte nás a odkažte zpět.** Nechte pod článkem řádek s tím, odkud pochází,
i s funkčním odkazem. Ten řádek je celá cena.

**Neměňte obsah.** Titulek si klidně upravte do svého stylu a přepište údaje
o čase a místě („včera" na „minulý týden"). Nepřidávejte text, nevyhazujte
výhrady a neměňte, co která věta tvrdí.

**Neprodávejte článek samostatně** ani ho nedávejte za placenou zeď jako
samostatný produkt.

**Nechte tam ten pixel.** Jednopixelový obrázek na konci bloku nám říká, kolik
lidí článek četlo. Nesbírá žádné osobní údaje a nikoho nesleduje.

**Fotografie součástí nejsou**, pokud u nich nepíšeme jinak. Většina obrázků je
licencovaná od třetích stran a potřebujete k nim vlastní práva.

## Překlady

Napište nám předem. Většinou souhlasíme, ale chceme text vidět — špatný překlad
pečlivě napsané věty je horší než žádný.

## Cokoli dalšího

Pište na {email}. Odpovídáme.""",
        "related": "Čtěte dál",
        "newsletter_soon": "Odběr spouštíme zanedlouho.",
        "republish_offer": "Volně k převzetí",
        "republish_help": "Zkopírujte HTML do svého systému. Uvedení zdroje i licence je součástí.",
    },
}
STRINGS.setdefault("sk", STRINGS["cs"])

MD = md.Markdown(extensions=["extra", "sane_lists", "smarty"])


def _html(text: str) -> str:
    MD.reset()
    return MD.convert(text)


def _url(meta: dict) -> str:
    return f"/{meta['lang']}/{meta['section']}/{meta['slug']}/"


def _view(meta: dict, body: str) -> dict:
    lang = meta["lang"]
    labels = article.LAYER_LABELS.get(lang, article.LAYER_LABELS["en"])
    secs = article.sections(body)
    layers = []
    for lid in article.LAYERS:
        if lid in secs and secs[lid].strip():
            label, icon = labels[lid]
            layers.append({"id": lid, "label": label, "icon": icon, "html": _html(secs[lid])})
    section_label = next(
        (s.get(lang) or s["en"] for s in config.site()["sections"] if s["id"] == meta["section"]),
        meta["section"],
    )
    words = len(body.split())
    return {
        **meta,
        "url": _url(meta),
        "words": words,
        "reading_time": max(1, round(words / 220)),
        "layers": layers,
        "body_html": _html(body) if not layers else "",
        **({"image": (_img := images.ensure(meta))["src"], "credit": _img["credit"]}),
        "section_label": section_label,
    }


def _related(a: dict, pool: list, n: int) -> list:
    """Vybere související články: nejdřív stejná rubrika, pak společná slova."""
    import re as _re
    words = set(_re.findall(r"[a-z]{5,}", (a.get("title", "") + " " + a.get("dek", "")).lower()))
    scored = []
    for other in pool:
        if other["slug"] == a["slug"]:
            continue
        w = set(_re.findall(r"[a-z]{5,}", (other.get("title", "") + " " + other.get("dek", "")).lower()))
        score = len(words & w) * 3
        if other["section"] == a["section"]:
            score += 5
        if other.get("type") in ("daily", "feature", "demand"):
            score += 2      # hlubší články drží čtenáře déle
        if score > 0:
            scored.append((score, other))
    scored.sort(key=lambda t: (-t[0], t[1]["date"]))
    return [o for _, o in scored[:n]]


def _faq_jsonld(a: dict) -> str:
    """Otázky a odpovědi pro bohatý výsledek ve vyhledávači."""
    import re as _re
    if a.get("type") not in ("demand", "daily"):
        return ""
    qa = []
    for layer in a.get("layers", []):
        text = _re.sub(r"<[^>]+>", " ", layer["html"])
        parts = _re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
        for i, sent in enumerate(parts):
            if sent.strip().endswith("?") and 20 < len(sent) < 160 and i + 1 < len(parts):
                answer = " ".join(parts[i + 1:i + 3])[:600]
                if len(answer) > 60:
                    qa.append({"@type": "Question", "name": sent.strip(),
                               "acceptedAnswer": {"@type": "Answer", "text": answer}})
        if len(qa) >= 4:
            break
    if len(qa) < 2:
        return ""
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": qa[:5]}, ensure_ascii=False)


def _breadcrumbs(a: dict, site: dict) -> str:
    base = site["brand"]["url"]
    return json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": site["brand"]["name_en"],
             "item": f"{base}/{a['lang']}/"},
            {"@type": "ListItem", "position": 2, "name": a.get("section_label", ""),
             "item": f"{base}/{a['lang']}/{a['section']}/"},
            {"@type": "ListItem", "position": 3, "name": a.get("title", "")},
        ]}, ensure_ascii=False)


def _jsonld(a: dict, site: dict) -> str:
    brand = site["brand"]
    data = {
        "@context": "https://schema.org", "@type": "NewsArticle",
        "headline": a.get("title", "")[:110],
        "description": a.get("dek", ""),
        "datePublished": a.get("date", ""),
        "dateModified": a.get("date", ""),
        "articleSection": a.get("section_label", ""),
        "inLanguage": a.get("lang", "en"),
        "mainEntityOfPage": {"@type": "WebPage", "@id": brand["url"] + a["url"]},
        "image": [brand["url"] + a.get("image", "")],
        "author": {"@type": "Organization", "name": brand["name_en"], "url": brand["url"]},
        "publisher": {"@type": "Organization", "name": brand["name_en"], "url": brand["url"]},
        "isAccessibleForFree": True,
    }
    if a.get("origin"):
        data["author"] = {"@type": "Person", "name": brand.get("author", brand["name_en"])}
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": a["origin"]["url"]}
    elif a.get("syndicated"):
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": a["syndicated"]["url"]}
    return json.dumps(data, ensure_ascii=False)


def _republish_html(a: dict, site: dict) -> str:
    """Hotový kus HTML, který si jiné médium jen zkopíruje."""
    r = site.get("republish", {})
    brand, url = site["brand"], site["brand"]["url"] + a["url"]
    parts = [f"<h1>{a['title']}</h1>", f"<p><em>{a.get('dek', '')}</em></p>"]
    for layer in a.get("layers", []):
        parts.append(f"<h2>{layer['label']}</h2>")
        parts.append(layer["html"])
    if a.get("body_html"):
        parts.append(a["body_html"])
    parts.append(
        f'<p><em>This article was originally published by '
        f'<a href="{url}">{brand["name_en"]}</a> and is republished under a '
        f'<a href="{r.get("license_url", "")}">{r.get("license", "")}</a> licence.</em></p>'
    )
    parts.append(f'<img src="{brand["url"]}/px.gif?a={a["slug"]}" alt="" width="1" height="1">')
    return "\n".join(parts)


def _write(path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run() -> None:
    site = config.site()
    brand_key = "name_cs"
    out = config.PUBLIC
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    env = Environment(
        loader=FileSystemLoader(str(config.TEMPLATES)),
        autoescape=select_autoescape(["html"]),
    )

    langs = [site["languages"]["master"], *site["languages"]["translations"]]
    today = dt.date.today().isoformat()

    for lang in langs:
        t = STRINGS.get(lang, STRINGS["en"])
        brand = site["brand"]["name_cs"] if lang == "cs" else site["brand"]["name_en"]
        tagline = site["brand"]["tagline_cs"] if lang == "cs" else site["brand"]["tagline_en"]

        arts = [
            _view(m, b)
            for m, b, _ in article.load_all(lang)
            if m.get("status") == "published" and m.get("date", "9999") <= today
        ]
        arts.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)

        filled = {a["section"] for a in arts}
        nav = [s for s in site["sections"] if s.get("primary") or s["id"] in filled]

        common = dict(
            lang=lang, brand=brand, tagline=tagline, t=t,
            sections=nav, all_sections=site["sections"], all_langs=langs,
            site_url=site["brand"]["url"], current_section=None,
            seo=site.get("seo", {}), newsletter=site.get("newsletter", {}),
            nl_headline=(site.get("newsletter", {}).get(f"headline_{lang}")
                         or site.get("newsletter", {}).get("headline_en", "")),
            nl_text=(site.get("newsletter", {}).get(f"text_{lang}")
                     or site.get("newsletter", {}).get("text_en", "")),
            nl_button=(site.get("newsletter", {}).get(f"button_{lang}")
                       or site.get("newsletter", {}).get("button_en", "")),
        )

        # --- článek ---
        rep_cfg = site.get("republish", {})
        seo = site.get("seo", {})
        for a in arts:
            a["jsonld"] = _jsonld(a, site)
            a["faq"] = _faq_jsonld(a)
            a["crumbs"] = _breadcrumbs(a, site)
            a["related"] = _related(a, arts, int(seo.get("related_count", 3)))
            a["republish"] = (
                _republish_html(a, site)
                if rep_cfg.get("enabled") and a.get("type") in rep_cfg.get("types", [])
                and not a.get("syndicated")
                else ""
            )
            _write(out / lang / a["section"] / a["slug"] / "index.html",
                   env.get_template("article.html").render(a=a, **common))

        # --- titulní strana ---
        briefing = [a for a in arts if a["type"] == "news"][:7]
        lead = arts[0] if arts else None
        used = {lead["slug"]} if lead else set()
        rows = []
        for sec in nav:
            sub = [a for a in arts if a["section"] == sec["id"] and a["slug"] not in used][:4]
            if len(sub) >= 1:
                rows.append({
                    "id": sec["id"], "icon": sec["icon"],
                    "label": sec.get(lang) or sec["en"], "articles": sub,
                })
        _write(out / lang / "index.html",
               env.get_template("index.html").render(
                   briefing=briefing, lead=lead, articles=arts[1:9],
                   rows=rows, **common))

        # --- rubriky ---
        for s in site["sections"]:
            sub = [a for a in arts if a["section"] == s["id"]]
            _write(out / lang / s["id"] / "index.html",
                   env.get_template("section.html").render(
                       articles=sub, section_label=s.get(lang) or s["en"],
                       section_icon=s["icon"], **{**common, "current_section": s["id"]}))

        # --- stránka pro média, která chtějí naše články převzít ---
        if site.get("republish", {}).get("enabled"):
            _write(out / lang / "republish" / "index.html",
                   env.get_template("page.html").render(
                       page_title=t["republish_title"],
                       page_html=_html(t["republish_body"].format(
                           license=site["republish"]["license"],
                           license_url=site["republish"]["license_url"],
                           email=site["brand"]["email"])), **common))

        # --- statické stránky ---
        for name in ("about", "start"):
            src = config.DATA / "pages" / f"{name}.{lang}.md"
            if not src.exists():
                src = config.DATA / "pages" / f"{name}.en.md"
            if src.exists():
                raw = src.read_text(encoding="utf-8")
                title = raw.splitlines()[0].lstrip("# ").strip()
                _write(out / lang / name / "index.html",
                       env.get_template("page.html").render(
                           page_title=title,
                           page_html=_html("\n".join(raw.splitlines()[1:])), **common))

        # --- předpovědi ---
        fc = analyst.load_forecasts()["forecasts"]
        _write(out / lang / "forecasts" / "index.html",
               env.get_template("forecasts.html").render(
                   score={**(_sc := analyst.scoreboard()),
                          "verdict": t.get("v_" + _sc["verdict"], _sc["verdict"])},
                   open=[f for f in fc if f["status"] == "open"],
                   resolved=sorted([f for f in fc if f["status"] == "resolved"],
                                   key=lambda f: f.get("resolved_on", ""), reverse=True),
                   void=[f for f in fc if f["status"] == "void"], **common))

        # --- RSS ---
        _write(out / lang / "feed.xml", _feed(arts[:30], brand, tagline, site["brand"]["url"], lang))

    # --- kořen webu ---
    master = site["languages"]["master"]
    _write(out / "index.html",
           f'<!doctype html><meta charset="utf-8">'
           f'<meta http-equiv="refresh" content="0; url=/{master}/">'
           f'<link rel="canonical" href="/{master}/">'
           f'<title>{site["brand"]["name_en"]}</title>'
           f'<p>→ <a href="/{master}/">{site["brand"]["name_en"]}</a></p>')
    _write(out / "robots.txt",
           f"User-agent: *\nAllow: /\nDisallow: /admin/\n"
           f"Sitemap: {site['brand']['url']}/sitemap.xml\n")

    # admin sekce — bez tokenu je to prázdná stránka, proto může být veřejně
    admin_src = config.ROOT / "admin"
    if admin_src.exists():
        shutil.copytree(admin_src, out / "admin")
    _write(out / "sitemap-pages.xml", _sitemap(out, site["brand"]["url"]))
    _write(out / "sitemap-news.xml", _news_sitemap(site))
    base = site["brand"]["url"]
    _write(out / "sitemap.xml",
           '<?xml version="1.0" encoding="UTF-8"?>'
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f"<sitemap><loc>{base}/sitemap-pages.xml</loc></sitemap>"
           f"<sitemap><loc>{base}/sitemap-news.xml</loc></sitemap>"
           "</sitemapindex>")

    for item in config.STATIC.iterdir():
        if item.name == "covers":
            continue
        (shutil.copytree if item.is_dir() else shutil.copy2)(item, out / item.name)

    # rejstřík pro admin — díky němu si admin nemusí stahovat všechny články
    index = []
    for lang in langs:
        for m, _, path in article.load_all(lang):
            index.append({
                "lang": lang, "slug": m.get("slug", ""), "title": m.get("title", ""),
                "dek": m.get("dek", ""), "date": m.get("date", ""),
                "status": m.get("status", ""), "section": m.get("section", ""),
                "type": m.get("type", ""), "depth": m.get("depth", ""),
                "confidence": m.get("confidence", 0),
                "path": f"content/{lang}/{path.name}",
                "url": _url(m) if m.get("status") == "published" else "",
                "review": m.get("review", {}), "problems": m.get("problems", []),
            })
    index.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    (config.DATA / "admin-index.json").write_text(
        json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                    "articles": index}, ensure_ascii=False, indent=1), encoding="utf-8")

    n = sum(1 for _ in out.rglob("index.html"))
    config.log(f"Web postaven: {n} stránek → {out}")


def _feed(arts: list, brand: str, tagline: str, url: str, lang: str) -> str:
    items = "".join(
        f"<item><title>{sx.escape(a['title'])}</title>"
        f"<link>{url}{a['url']}</link><guid>{url}{a['url']}</guid>"
        f"<pubDate>{a['date']}</pubDate>"
        f"<description>{sx.escape(a.get('dek', ''))}</description></item>"
        for a in arts
    )
    return (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
            f"<title>{sx.escape(brand)}</title><link>{url}/{lang}/</link>"
            f"<description>{sx.escape(tagline)}</description>{items}</channel></rss>")


def _news_sitemap(site: dict) -> str:
    """Sitemap pro Google News — bere jen články z posledních dvou dnů."""
    cutoff = (dt.date.today() - dt.timedelta(days=2)).isoformat()
    brand = site["brand"]
    rows = []
    for lang in [site["languages"]["master"], *site["languages"]["translations"]]:
        for m, _, _ in article.load_all(lang):
            if m.get("status") != "published" or m.get("date", "") < cutoff:
                continue
            loc = f"{brand['url']}/{lang}/{m['section']}/{m['slug']}/"
            rows.append(
                f"<url><loc>{loc}</loc><news:news>"
                f"<news:publication><news:name>{sx.escape(brand['name_en'])}</news:name>"
                f"<news:language>{lang}</news:language></news:publication>"
                f"<news:publication_date>{m['date']}</news:publication_date>"
                f"<news:title>{sx.escape(m.get('title', ''))}</news:title>"
                f"</news:news></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
            + "".join(rows) + "</urlset>")


def _sitemap(out, url: str) -> str:
    urls = []
    for p in sorted(out.rglob("index.html")):
        rel = str(p.parent.relative_to(out)).replace("\\", "/")
        if rel.startswith("admin"):
            continue
        loc = f"{url}/" if rel == "." else f"{url}/{rel}/"
        urls.append(f"<url><loc>{loc}</loc></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(urls) + "</urlset>")


if __name__ == "__main__":
    run()
