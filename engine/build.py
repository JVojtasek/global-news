"""Postaví statický web ze složky content/ do složky public/.

Nepotřebuje server, databázi ani Node.js. Výsledek se dá nahrát kamkoli
(Cloudflare Pages, GitHub Pages, obyčejný webhosting).
"""
from __future__ import annotations

import datetime as dt
import html as _html_mod
import json
import shutil
import xml.sax.saxutils as sx

import markdown as md
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import analyst, article, config, images, interests, quotes, reader

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
        "today": "",
        "theme": "Light / dark",
        "weather_title": "Weather",
        "weather_intro": "Pick your place once and it stays. Seven-day forecast and live rain radar.",
        "weather_ph": "Town or city…",
        "weather_find": "Find",
        "weather_here": "Use my location",
        "weather_hint": "Type a place, or let the browser find you. Your choice is stored on this device only.",
        "weather_radar": "Rain radar — where the storm is heading",
        "weather_credit": "Forecast: Open-Meteo · Radar: RainViewer · Air and pollen: Open-Meteo · Map: OpenStreetMap contributors",
        "weather_feels": "Feels like",
        "weather_wind": "Wind",
        "weather_hum": "Humidity",
        "weather_rainc": "Rain",
        "weather_now": "Now",
        "weather_play": "Play",
        "weather_pause": "Pause",
        "weather_past": "Past two hours",
        "weather_soon": "Next 30 minutes",
        "weather_nowcast_dry": "No rain expected in the next two hours.",
        "weather_nowcast_start": "Rain starts in about %d min",
        "weather_nowcast_stop": "Rain should stop in about %d min",
        "weather_nowcast_now": "It is raining now",
        "weather_hours": "Next 24 hours",
        "weather_best": "Best window today",
        "weather_best_none": "No clearly better window today — it looks much the same all day.",
        "weather_best_txt": "%s to %s looks driest and calmest.",
        "weather_air": "Air and pollen",
        "weather_aqi": "Air quality",
        "weather_pollen": "Pollen",
        "weather_uv": "UV",
        "weather_sun": "Sun",
        "weather_aqi_labels": ["Good", "Fair", "Moderate", "Poor", "Very poor", "Extremely poor"],
        "weather_low": "low", "weather_med": "moderate", "weather_high": "high",
        "weather_days": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "weather_codes": {"0": "Clear sky", "1": "Mainly clear", "2": "Partly cloudy", "3": "Overcast", "45": "Fog", "48": "Freezing fog", "51": "Light drizzle", "53": "Drizzle", "55": "Heavy drizzle", "61": "Light rain", "63": "Rain", "65": "Heavy rain", "66": "Freezing rain", "67": "Heavy freezing rain", "71": "Light snow", "73": "Snow", "75": "Heavy snow", "77": "Snow grains", "80": "Rain showers", "81": "Heavy showers", "82": "Violent showers", "85": "Snow showers", "86": "Heavy snow showers", "95": "Thunderstorm", "96": "Thunderstorm with hail", "99": "Severe thunderstorm"},
        "thought_title": "Thought for the day",
        "wit_title": "Last word",
        "ticker_title": "Live now",
        "ticker_note": "Headlines gathered from our sources every three hours. Links go to the original reporting.",
        "reader_open": "Reading balance",
        "reader_title": "Your reading balance",
        "reader_intro": "You decide how much news you get and how hard it lands. Nothing is deleted — heavy stories are shortened to a calm summary you can open in full whenever you want.",
        "reader_amount": "How much",
        "reader_amount_1": "Overview only",
        "reader_amount_2": "Balanced",
        "reader_amount_3": "Everything",
        "reader_amount_help": "Overview keeps you in the picture with about a dozen stories a day.",
        "reader_tone": "How hard it lands",
        "reader_tone_1": "Gentle",
        "reader_tone_2": "Balanced",
        "reader_tone_3": "Unfiltered",
        "reader_tone_help": "Gentle shows heavy stories as a summary — what happened, what it means, what the risks are, what can be done.",
        "reader_mute": "Keep these out",
        "reader_brake": "Remind me to take a break",
        "reader_brake_msg": "That is five heavy stories in a row. The world will still be there in ten minutes.",
        "reader_brake_ok": "Carry on",
        "reader_brake_alt": "Show me something good",
        "reader_topics": {"war": "War and conflict", "crime": "Crime and courts",
                          "disaster": "Disasters", "politics": "Politics",
                          "health": "Illness and medicine", "money": "Money and markets",
                          "tech": "Technology"},
        "reader_full": "Read the whole article",
        "reader_calm": "Shown as a summary because of your reading settings.",
        "reader_hidden_1": "1 story is hidden by your settings.",
        "reader_hidden_n": "%d stories are hidden by your settings.",
        "reader_show": "Show them anyway",
        "reader_privacy": "Saved on this device only. We do not profile you and nothing is sent anywhere.",
        "reader_save": "Save",
        "reader_reset": "Reset",
        "ob_title": "Make this your paper",
        "ob_intro": "Thirty seconds, and the front page starts with what matters to you. You can change it any time, and you can skip this entirely.",
        "ob_skip": "Skip",
        "ob_next": "Next",
        "ob_back": "Back",
        "ob_done": "Done",
        "ob_step": "Step %d of 3",
        "ob_sections": "Which sections should come first?",
        "ob_interests": "And more precisely?",
        "ob_balance": "How much, and how hard?",
        "ob_privacy": "Everything you tick stays in this browser. There is no account, nothing is sent anywhere, and we cannot see it. Clearing your browser data clears this too.",
        "foryou": "For you",
        "foryou_title": "Chosen for you",
        "foryou_intro": "Ranked in your browser from your own settings. We never see them.",
        "foryou_empty": "Tell us what interests you and this page fills up.",
        "foryou_setup": "Set up my paper",
        "foryou_outside": "Outside your circle — on purpose",
        "foryou_outside_help": "A newspaper that only ever agreed with you would be a mirror, not a newspaper. These are picked from everything else.",
        "foryou_health_note": "Health is a topic here, not advice. We report what research shows, name the source, and say what is still unknown. For anything about your own health, ask a doctor.",
        "picked": "Picked for you",
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
        "today": "",
        "theme": "Světlý / tmavý režim",
        "weather_title": "Počasí",
        "weather_intro": "Vyber si místo jednou a zůstane ti. Předpověď na sedm dní a živý srážkový radar.",
        "weather_ph": "Město nebo obec…",
        "weather_find": "Najít",
        "weather_here": "Moje poloha",
        "weather_hint": "Napiš místo, nebo nech prohlížeč, ať tě najde. Volba se ukládá jen do tvého zařízení.",
        "weather_radar": "Srážkový radar — kam se bouřka posouvá",
        "weather_credit": "Předpověď: Open-Meteo · Radar: RainViewer · Ovzduší a pyl: Open-Meteo · Mapa: přispěvatelé OpenStreetMap",
        "weather_feels": "Pocitově",
        "weather_wind": "Vítr",
        "weather_hum": "Vlhkost",
        "weather_rainc": "Déšť",
        "weather_now": "Teď",
        "weather_play": "Přehrát",
        "weather_pause": "Pauza",
        "weather_past": "Poslední dvě hodiny",
        "weather_soon": "Nejbližší půlhodina",
        "weather_nowcast_dry": "V nejbližších dvou hodinách se déšť nečeká.",
        "weather_nowcast_start": "Déšť začne asi za %d min",
        "weather_nowcast_stop": "Déšť by měl ustat asi za %d min",
        "weather_nowcast_now": "Právě prší",
        "weather_hours": "Nejbližších 24 hodin",
        "weather_best": "Nejlepší okno dne",
        "weather_best_txt": "Nejsušeji a nejklidněji bude mezi %s a %s.",
        "weather_best_none": "Dnes není výrazně lepší okno — celý den vypadá podobně.",
        "weather_air": "Ovzduší a pyl",
        "weather_aqi": "Kvalita ovzduší",
        "weather_pollen": "Pyl",
        "weather_uv": "UV",
        "weather_sun": "Slunce",
        "weather_aqi_labels": ["Dobrá", "Slušná", "Střední", "Špatná", "Velmi špatná", "Extrémně špatná"],
        "weather_low": "nízký", "weather_med": "střední", "weather_high": "vysoký",
        "weather_days": ["Ne", "Po", "Út", "St", "Čt", "Pá", "So"],
        "weather_codes": {"0": "Jasno", "1": "Skoro jasno", "2": "Polojasno", "3": "Zataženo", "45": "Mlha", "48": "Mrznoucí mlha", "51": "Slabé mrholení", "53": "Mrholení", "55": "Silné mrholení", "61": "Slabý déšť", "63": "Déšť", "65": "Silný déšť", "66": "Mrznoucí déšť", "67": "Silný mrznoucí déšť", "71": "Slabé sněžení", "73": "Sněžení", "75": "Silné sněžení", "77": "Sněhová zrna", "80": "Přeháňky", "81": "Silné přeháňky", "82": "Prudké přeháňky", "85": "Sněhové přeháňky", "86": "Silné sněhové přeháňky", "95": "Bouřka", "96": "Bouřka s krupobitím", "99": "Silná bouřka"},
        "thought_title": "Myšlenka dne",
        "wit_title": "Poslední slovo",
        "ticker_title": "Právě se děje",
        "ticker_note": "Titulky z našich zdrojů, aktualizované každé tři hodiny. Odkazy vedou na původní zpravodajství.",
        "reader_open": "Nastavení čtení",
        "reader_title": "Kolik toho na tebe má web pustit",
        "reader_intro": "Ty rozhoduješ, kolik zpráv dostaneš a jak natvrdo. Nic se nemaže — těžké zprávy se zkrátí na klidné shrnutí, které si kdykoli rozklikneš celé.",
        "reader_amount": "Kolik toho",
        "reader_amount_1": "Jen přehled",
        "reader_amount_2": "Vyváženě",
        "reader_amount_3": "Všechno",
        "reader_amount_help": "Přehled ti nechá zhruba tucet zpráv denně, ale o nic důležitého nepřijdeš.",
        "reader_tone": "Jak natvrdo",
        "reader_tone_1": "Šetrně",
        "reader_tone_2": "Vyváženě",
        "reader_tone_3": "Bez filtru",
        "reader_tone_help": "Šetrný režim ukáže u těžkých zpráv jen shrnutí: co se stalo, co to znamená, jaká jsou rizika a co se s tím dá dělat.",
        "reader_mute": "Tohle mi sem nedávej",
        "reader_brake": "Připomeň mi pauzu",
        "reader_brake_msg": "To je pět těžkých zpráv za sebou. Svět tu za deset minut pořád bude.",
        "reader_brake_ok": "Pokračovat",
        "reader_brake_alt": "Ukaž mi něco dobrého",
        "reader_topics": {"war": "Válka a konflikty", "crime": "Kriminalita a soudy",
                          "disaster": "Katastrofy", "politics": "Politika",
                          "health": "Nemoci a medicína", "money": "Peníze a trhy",
                          "tech": "Technologie"},
        "reader_full": "Číst celý článek",
        "reader_calm": "Zobrazeno jako shrnutí podle tvého nastavení čtení.",
        "reader_hidden_1": "Podle tvého nastavení je skrytá 1 zpráva.",
        "reader_hidden_n": "Podle tvého nastavení jsou skryté %d zprávy.",
        "reader_show": "Přesto zobrazit",
        "reader_privacy": "Uloženo jen v tomhle zařízení. Nesledujeme tě a nikam se nic neposílá.",
        "reader_save": "Uložit",
        "reader_reset": "Zpět na výchozí",
        "ob_title": "Udělej si z toho svoje noviny",
        "ob_intro": "Třicet vteřin a titulní strana začne tím, co zajímá tebe. Kdykoli to změníš a klidně to celé přeskoč.",
        "ob_skip": "Přeskočit",
        "ob_next": "Dál",
        "ob_back": "Zpět",
        "ob_done": "Hotovo",
        "ob_step": "Krok %d ze 3",
        "ob_sections": "Které rubriky mají být první?",
        "ob_interests": "A přesněji?",
        "ob_balance": "Kolik toho a jak natvrdo?",
        "ob_privacy": "Všechno, co zaškrtneš, zůstane v tomhle prohlížeči. Žádný účet, nic se nikam neposílá a my se to nedozvíme. Když si smažeš data prohlížeče, smaže se i tohle.",
        "foryou": "Pro tebe",
        "foryou_title": "Vybráno pro tebe",
        "foryou_intro": "Seřazeno přímo v tvém prohlížeči podle tvého nastavení. My ho nevidíme.",
        "foryou_empty": "Řekni nám, co tě zajímá, a tahle stránka se naplní.",
        "foryou_setup": "Nastavit si noviny",
        "foryou_outside": "Mimo tvůj okruh — schválně",
        "foryou_outside_help": "Noviny, které by ti jen přitakávaly, jsou zrcadlo, ne noviny. Tohle je vybrané ze všeho ostatního.",
        "foryou_health_note": "Zdraví je tady téma, ne rada. Píšeme, co ukazuje výzkum, uvádíme zdroj a říkáme, co se zatím neví. Na cokoli ohledně svého zdraví se ptej lékaře.",
        "picked": "Vybráno pro tebe",
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
    return f"{config.base_path()}/{meta['lang']}/{meta['section']}/{meta['slug']}/"


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
    # převzaté texty občas nesou HTML entity (&#160;, &amp;) — v perexu
    # by se pak ukázaly jako text
    for _k in ("title", "dek"):
        if isinstance(meta.get(_k), str) and "&" in meta[_k]:
            meta[_k] = _html_mod.unescape(meta[_k])
    words = len(body.split())
    w = reader.weigh(meta, body)
    return {
        **meta,
        "url": _url(meta),
        "words": words,
        "reading_time": max(1, round(words / 220)),
        "layers": layers,
        "has_brief": any(l["id"] == "BRIEFLY" for l in layers),
        "load": w["load"],
        "band": reader.band(w["load"]),
        "topics_csv": ",".join(w["topics"]),
        "tags_csv": ",".join(interests.tags(meta, body)),
        "body_html": _html(body) if not layers else "",
        **({"image": (_img := images.ensure(meta))["src"], "credit": _img["credit"]}),
        "section_label": section_label,
    }


def _ticker(site: dict, lang: str, limit: int = 14) -> list:
    """Rychlé zprávy do postranního sloupce.

    Systém posbírá 300 událostí denně, ale článků napíše pár. Zbytek
    by se jinak zahodil — tady z něj děláme živý proužek toho, co se
    právě děje, s odkazem vždy na původní zdroj.
    """
    p = config.DATA / "events.json"
    if not p.exists():
        return []
    try:
        events = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []

    labels = {s["id"]: (s.get(lang) or s["en"]) for s in site["sections"]}
    out, seen = [], set()
    for e in events:
        head = e.get("headline", "").strip()
        key = head.lower()[:60]
        if not head or key in seen or len(head) < 25:
            continue
        item = (e.get("items") or [{}])[0]
        if not item.get("url"):
            continue
        seen.add(key)
        out.append({
            "headline": head[:130],
            "url": item["url"],
            "source": item.get("source", ""),
            "section": labels.get(e.get("section", ""), ""),
            "sources_count": e.get("sources_count", 1),
            "hot": e.get("score", 0) >= 70,
        })
        if len(out) >= limit:
            break
    return out


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
    base = config.origin() + config.base_path() + "/"
    return json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": site["brand"]["name_en"],
             "item": f"{base}{a['lang']}/"},
            {"@type": "ListItem", "position": 2, "name": a.get("section_label", ""),
             "item": f"{base}{a['lang']}/{a['section']}/"},
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
        "mainEntityOfPage": {"@type": "WebPage", "@id": config.origin() + a["url"]},
        **({"image": [config.origin() + a["image"]]} if a.get("image") else {}),
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
    brand, url = site["brand"], config.origin() + a["url"]
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
    parts.append(f'<img src="{config.origin()}{config.base_path()}/px.gif?a={a["slug"]}" alt="" width="1" height="1">')
    return "\n".join(parts)


MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
    "cs": ["ledna", "února", "března", "dubna", "května", "června", "července",
           "srpna", "září", "října", "listopadu", "prosince"],
}
DAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "cs": ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"],
}


def _date_label(lang: str) -> str:
    d = dt.date.today()
    days, months = DAYS.get(lang, DAYS["en"]), MONTHS.get(lang, MONTHS["en"])
    if lang == "cs":
        return f"{days[d.weekday()]} {d.day}. {months[d.month - 1]} {d.year}"
    return f"{days[d.weekday()]}, {d.day} {months[d.month - 1]} {d.year}"


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
            site_url=config.origin(), base=config.base_path(), current_section=None,
            seo=site.get("seo", {}), newsletter=site.get("newsletter", {}),
            wit=quotes.wit(),
            interest_groups=interests.catalogue(),
            today_label=_date_label(lang),
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
        briefing = [a for a in arts if a["type"] in ("news", "daily", "demand")][:7]
        # v čele webu má stát náš vlastní článek dne, ne převzatý text
        prio = {"daily": 0, "feature": 1, "demand": 2, "analysis": 3, "news": 4,
                "syndicated": 8, "imported": 9}
        lead = min(
            arts,
            key=lambda a: (a["date"] < today, prio.get(a.get("type"), 5), -a.get("words", 0)),
        ) if arts else None
        used = {lead["slug"]} if lead else set()
        rows = []
        for sec in nav:
            sub = [a for a in arts if a["section"] == sec["id"] and a["slug"] not in used][:4]
            if len(sub) >= 1:
                rows.append({
                    "id": sec["id"],
                    "label": sec.get(lang) or sec["en"], "articles": sub,
                })
        _write(out / lang / "index.html",
               env.get_template("index.html").render(
                   briefing=briefing, lead=lead, articles=arts[1:9],
                   rows=rows, ticker=_ticker(site, lang),
                   thought=quotes.thought(), **common))

        # --- rubriky ---
        for s in site["sections"]:
            sub = [a for a in arts if a["section"] == s["id"]]
            _write(out / lang / s["id"] / "index.html",
                   env.get_template("section.html").render(
                       articles=sub, section_label=s.get(lang) or s["en"],
                       **{**common, "current_section": s["id"]}))

        # --- stránka pro média, která chtějí naše články převzít ---
        if site.get("republish", {}).get("enabled"):
            _write(out / lang / "republish" / "index.html",
                   env.get_template("page.html").render(
                       page_title=t["republish_title"],
                       page_html=_html(t["republish_body"].format(
                           license=site["republish"]["license"],
                           license_url=site["republish"]["license_url"],
                           email=site["brand"]["email"])), **common))

        # --- počasí ---
        # výchozí místo, dokud si čtenář nevybere svoje
        wx_default = {"cs": {"name": "Praha", "country": "", "admin": "", "lat": 50.08, "lon": 14.44}}.get(
            lang, {"name": "London", "country": "", "admin": "", "lat": 51.51, "lon": -0.13})
        _write(out / lang / "weather" / "index.html",
               env.get_template("weather.html").render(
                   weather_default=json.dumps(wx_default, ensure_ascii=False), **common))

        # --- seznam všech článků pro prohlížeč ------------------------
        # Web nemá server ani databázi, takže osobní výběr musí sestavit
        # prohlížeč sám. Dostane k tomu tenhle seznam — je pro všechny
        # stejný, nikdo se z něj nedozví, co koho zajímá.
        index = [{
            "u": a["url"], "t": a["title"], "d": (a.get("dek") or "")[:180],
            "s": a["section"], "sl": a["section_label"], "dt": a["date"],
            "g": a.get("tags_csv", ""), "p": a.get("topics_csv", ""),
            "l": a.get("load", 0), "b": a.get("band", "mid"),
            "i": a.get("image") or "", "y": a.get("type", ""),
        } for a in arts]
        _write(out / lang / "articles.json",
               json.dumps(index, ensure_ascii=False, separators=(",", ":")))

        # --- osobní výběr ---------------------------------------------
        _write(out / lang / "foryou" / "index.html",
               env.get_template("foryou.html").render(**common))

        # --- statické stránky ---
        for name in ("about", "start", "privacy"):
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
    bp = config.base_path()
    _write(out / "index.html",
           f'<!doctype html><meta charset="utf-8">'
           f'<meta http-equiv="refresh" content="0; url={bp}/{master}/">'
           f'<link rel="canonical" href="{bp}/{master}/">'
           f'<title>{site["brand"]["name_en"]}</title>'
           f'<p>→ <a href="{bp}/{master}/">{site["brand"]["name_en"]}</a></p>')
    _write(out / "robots.txt",
           f"User-agent: *\nAllow: /\nDisallow: {config.base_path()}/admin/\n"
           f"Sitemap: {site['brand']['url']}/sitemap.xml\n")

    # admin sekce — bez tokenu je to prázdná stránka, proto může být veřejně
    admin_src = config.ROOT / "admin"
    if admin_src.exists():
        shutil.copytree(admin_src, out / "admin")
    _write(out / "sitemap-pages.xml", _sitemap(out, config.origin() + config.base_path()))
    _write(out / "sitemap-news.xml", _news_sitemap(site))
    base = config.origin() + config.base_path()
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
            loc = f"{config.origin()}{config.base_path()}/{lang}/{m['section']}/{m['slug']}/"
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
