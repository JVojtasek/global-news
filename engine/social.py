"""Sdílení článků na sociální sítě.

Publikuje se **přes oficiální rozhraní platforem**. Nic se nemaskuje a nic
se neobchází — automatické publikování je na těchhle platformách povolené
a algoritmy za něj netrestají. Co dosah opravdu snižuje, je stejný text
všude a odkaz ven; proto má každá platforma vlastní podobu příspěvku.

Co systém umí sám (zdarma, stačí přístupové údaje):
  * Bluesky  — BLUESKY_HANDLE + BLUESKY_APP_PASSWORD
  * Telegram — TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID

Co ti připraví k vložení (Facebook, Instagram, X a LinkedIn mají složitější
schvalování, takže dostaneš hotové texty do souboru):
  * data/social/k-vlozeni.md
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import textwrap

import requests

from . import article, config

OUT = config.DATA / "social"
QUEUE = OUT / "queue.json"
STATE_KEY = "posted_slugs"


def load_queue() -> dict:
    if not QUEUE.exists():
        return {"items": []}
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def save_queue(q: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")


# ------------------------------------------------------------ tvorba textů
def _first_question(body: str) -> str:
    secs = article.sections(body)
    text = secs.get("REFLECT") or secs.get("DEEPER") or ""
    for line in text.splitlines():
        line = line.strip().lstrip("-*0123456789. ")
        if line.endswith("?") and 25 < len(line) < 190:
            return line
    return ""


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[*_`#]", "", text)).strip()


def compose(meta: dict, body: str, url: str) -> dict:
    title = _clean(meta.get("title", ""))
    dek = _clean(meta.get("dek", ""))
    q = _clean(_first_question(body))
    tag = {
        "world": "#news", "business": "#business", "tech": "#technology",
        "science": "#science", "health": "#health", "culture": "#culture",
        "travel": "#travel", "motoring": "#cars", "sport": "#sport",
        "food": "#food", "goodnews": "#goodnews", "history": "#history",
        "questions": "#philosophy", "meaning": "#psychology",
    }.get(meta.get("section", "world"), "#news")

    bluesky = f"{title}\n\n{textwrap.shorten(dek, 150, placeholder='…')}\n\n{url}"
    if len(bluesky) > 295:
        bluesky = f"{textwrap.shorten(title, 180, placeholder='…')}\n\n{url}"

    telegram = f"<b>{title}</b>\n\n{dek}"
    if q:
        telegram += f"\n\n<i>{q}</i>"
    telegram += f"\n\n{url}"

    x = textwrap.shorten(f"{title} — {dek}", 240, placeholder="…") + f"\n\n{url}"

    instagram = (
        f"{title}\n\n{dek}\n\n"
        + (f"{q}\n\n" if q else "")
        + f"Full story — link in bio.\n\n{tag} #thedeeperstory #beyondtheheadline"
    )

    facebook = f"{title}\n\n{dek}\n\n" + (f"{q}\n\n" if q else "") + url

    linkedin = (
        f"{title}\n\n{dek}\n\n"
        + (f"{q}\n\n" if q else "")
        + f"We publish the facts first, the background second, and the question underneath last.\n\n{url}"
    )

    return {
        "bluesky": bluesky, "telegram": telegram, "x": x,
        "instagram": instagram, "facebook": facebook, "linkedin": linkedin,
    }


# ------------------------------------------------------------------ Bluesky
def _bluesky_facets(text: str) -> list:
    facets = []
    for m in re.finditer(r"https?://\S+", text):
        facets.append({
            "index": {
                "byteStart": len(text[: m.start()].encode()),
                "byteEnd": len(text[: m.end()].encode()),
            },
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}],
        })
    return facets


def post_bluesky(text: str) -> bool:
    handle = os.environ.get("BLUESKY_HANDLE")
    password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not handle or not password:
        return False
    try:
        s = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": handle, "password": password}, timeout=30,
        )
        if s.status_code != 200:
            config.log(f"    Bluesky přihlášení selhalo: {s.text[:120]}")
            return False
        sess = s.json()
        r = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {sess['accessJwt']}"},
            json={
                "repo": sess["did"],
                "collection": "app.bsky.feed.post",
                "record": {
                    "$type": "app.bsky.feed.post",
                    "text": text,
                    "facets": _bluesky_facets(text),
                    "createdAt": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
                    "langs": ["en"],
                },
            },
            timeout=30,
        )
        return r.status_code == 200
    except Exception as e:  # noqa: BLE001
        config.log(f"    Bluesky chyba: {str(e)[:120]}")
        return False


# ----------------------------------------------------------------- Telegram
def post_telegram(text: str) -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text, "parse_mode": "HTML",
                  "disable_web_page_preview": False},
            timeout=30,
        )
        return r.status_code == 200
    except Exception as e:  # noqa: BLE001
        config.log(f"    Telegram chyba: {str(e)[:120]}")
        return False


# --------------------------------------------------------------------- běh
def prepare() -> int:
    """Připraví příspěvky do fronty. Neodesílá nic."""
    site = config.site()
    cfg = site.get("social", {})
    base = site["brand"]["url"].rstrip("/")
    state = config.load_state()
    posted = set(state.get(STATE_KEY, []))
    lang = site["languages"]["master"]

    q = load_queue()
    queued = {i["slug"] for i in q["items"]}

    arts = [
        (m, b) for m, b, _ in article.load_all(lang)
        if m.get("status") == "published"
        and m.get("slug") not in posted
        and m.get("slug") not in queued
    ]
    # vlastní články mají přednost před převzatými
    arts.sort(key=lambda t: t[0].get("date", ""), reverse=True)
    arts.sort(key=lambda t: t[0].get("type") == "syndicated")
    arts = arts[: int(cfg.get("posts_per_day", 3))]

    if not arts:
        config.log("Nic nového k přípravě.")
        return 0

    auto = cfg.get("mode", "review") == "auto"
    for meta, body in arts:
        url = f"{base}/{lang}/{meta['section']}/{meta['slug']}/"
        q["items"].append({
            "slug": meta["slug"],
            "title": meta["title"],
            "url": url,
            "section": meta.get("section", ""),
            "created": config.today(),
            "status": "approved" if auto else "pending",
            "posts": compose(meta, body, url),
            "sent": [],
        })
    save_queue(q)
    config.log(f"Do fronty přidáno {len(arts)} příspěvků "
               f"({'rovnou schválené' if auto else 'čekají na tvoje schválení v adminu'}).")
    return len(arts)


def send() -> int:
    """Odešle to, co je ve frontě schválené. Nic jiného."""
    site = config.site()
    cfg = site.get("social", {})
    q = load_queue()
    state = config.load_state()
    posted = set(state.get(STATE_KEY, []))
    sent_total = 0
    manual_blocks = []

    for item in q["items"]:
        if item["status"] != "approved":
            continue
        posts = item["posts"]

        if "bluesky" in cfg.get("enabled", []) and "bluesky" not in item["sent"]:
            if post_bluesky(posts["bluesky"]):
                item["sent"].append("bluesky")
                config.log(f"  ✓ Bluesky: {item['title'][:50]}")
                sent_total += 1
        if "telegram" in cfg.get("enabled", []) and "telegram" not in item["sent"]:
            if post_telegram(posts["telegram"]):
                item["sent"].append("telegram")
                config.log(f"  ✓ Telegram: {item['title'][:50]}")
                sent_total += 1

        block = [f"## {item['title']}", "", f"<{item['url']}>", ""]
        for platform in cfg.get("export", []):
            block += [f"### {platform.capitalize()}", "", "```", posts.get(platform, ""), "```", ""]
        manual_blocks.append("\n".join(block))

        item["status"] = "done"
        posted.add(item["slug"])

    # hotové a odmítnuté necháme týden, ať je vidět historie
    q["items"] = [i for i in q["items"]
                  if i["status"] in ("pending", "approved") or i["created"] >= _week_ago()]
    save_queue(q)

    if manual_blocks:
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "k-vlozeni.md").write_text(
            f"# Příspěvky k ručnímu vložení — {config.today()}\n\n"
            "Zkopíruj text a vlož ho na příslušnou síť. Obrázek k článku najdeš\n"
            "ve složce `data/covers/`.\n\n---\n\n" + "\n---\n\n".join(manual_blocks),
            encoding="utf-8")

    state[STATE_KEY] = list(posted)[-500:]
    config.save_state(state)
    waiting = len([i for i in q["items"] if i["status"] == "pending"])
    config.log(f"Odesláno {sent_total} příspěvků. Ve frontě čeká na schválení: {waiting}.")
    return sent_total


def _week_ago() -> str:
    return (dt.date.today() - dt.timedelta(days=7)).isoformat()


def run() -> int:
    prepare()
    return send()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "prepare":
        prepare()
    elif cmd == "send":
        send()
    else:
        run()
