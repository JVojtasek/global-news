"""IndexNow — ohlášení nově vydaných článků vyhledávačům.

Google si web projde sám, když se mu chce. Bing, Seznam a Yandex umí
něco lepšího: pošle se jim seznam adres a mají ho do pár minut. Účet
ani registrace k tomu nejsou potřeba, stačí klíč z `data/site.yml`
(`seo_plus.indexnow_key`) a soubor s tím klíčem na webu — tím se
prokazuje, že web opravdu patří tomu, kdo hlásí.

Co se odesílá: **výhradně adresy našich vlastních článků.** Nic o
čtenářích, žádné identifikátory, žádná návštěvnost. Ta hranice je
záměrná a platí i tady, viz `data/EDITORIAL-CODE.md`, oddíl 5.

Spouští se samo po publikaci webu:

    python -m engine.seo

Když se ohlášení nepovede, nic se nerozbije — zapíše se to do logu
a web jede dál. Vyhledávače si nový článek stejně najdou samy, tohle
je jen zkratka.
"""
from __future__ import annotations

import datetime as dt
import re
from urllib.parse import urlparse

from . import config

ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10_000          # víc jich rozhraní v jednom volání nebere
TIMEOUT = 20               # vteřin; publikace kvůli tomuhle čekat nebude


# ------------------------------------------------------------------ klíč
def key() -> str:
    """Klíč z data/site.yml. Prázdný = IndexNow se nepoužívá."""
    cfg = config.site().get("seo_plus") or {}
    return str(cfg.get("indexnow_key") or "").strip()


def key_location() -> str:
    """Adresa souboru s klíčem tak, jak ji uvidí vyhledávač."""
    return f"{config.origin()}{config.base_path()}/{key()}.txt"


def write_key_file(out_dir) -> bool:
    """Položí `<klíč>.txt` do kořene webu. Bez něj ohlášení neprojde."""
    k = key()
    if not k or not re.fullmatch(r"[A-Za-z0-9-]{8,128}", k):
        return False
    path = out_dir / f"{k}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(k, encoding="utf-8")
    return True


# --------------------------------------------------------------- ohlášení
def ping_indexnow(urls) -> bool:
    """Ohlásí seznam adres. Nikdy nevyhodí výjimku — vrací True/False.

    Delší seznam se rozdělí po `MAX_URLS`. Vrací True, jen když prošlo
    všechno; jinak se důvod zapíše do logu.
    """
    k = key()
    if not k:
        config.log("IndexNow: klíč není vyplněný, přeskakuji.")
        return False

    host = urlparse(config.origin()).netloc
    clean, seen = [], set()
    for u in urls or []:
        u = str(u or "").strip()
        # Cizí adresa by celé volání shodila — rozhraní chce jeden web.
        if not u or u in seen or urlparse(u).netloc != host:
            continue
        seen.add(u)
        clean.append(u)
    if not clean:
        config.log("IndexNow: není co hlásit.")
        return False

    try:
        import requests
    except Exception as e:  # noqa: BLE001
        config.log(f"IndexNow: chybí knihovna requests ({e}).")
        return False

    ok = True
    for i in range(0, len(clean), MAX_URLS):
        chunk = clean[i:i + MAX_URLS]
        payload = {
            "host": host,
            "key": k,
            "keyLocation": key_location(),
            "urlList": chunk,
        }
        try:
            r = requests.post(
                ENDPOINT, json=payload, timeout=TIMEOUT,
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
            # 200 = přijato, 202 = přijato, klíč se teprve ověřuje
            if r.status_code in (200, 202):
                config.log(f"IndexNow: ohlášeno {len(chunk)} adres ({r.status_code}).")
            else:
                ok = False
                config.log(f"IndexNow: odmítnuto, stav {r.status_code} {r.text[:200]}")
        except Exception as e:  # noqa: BLE001
            ok = False
            config.log(f"IndexNow: ohlášení se nepovedlo ({e}).")
    return ok


# ------------------------------------------------------- co vlastně hlásit
def _from_news_sitemap(cutoff: dt.datetime) -> list[str]:
    """Adresy ze zpravodajské sitemapy, novější než `cutoff`."""
    p = config.PUBLIC / "sitemap-news.xml"
    if not p.exists():
        return []
    xml = p.read_text(encoding="utf-8")
    out = []
    for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
        loc = re.search(r"<loc>(.*?)</loc>", block, re.S)
        when = re.search(r"<news:publication_date>(.*?)</news:publication_date>", block, re.S)
        if not loc:
            continue
        if when and _stamp(when.group(1).strip()) < cutoff:
            continue
        out.append(loc.group(1).strip())
    return out


def _from_articles(cutoff: dt.datetime) -> list[str]:
    """Náhradní cesta, když sitemapa chybí: seznam článků ze souborů."""
    from . import article, members
    site = config.site()
    out = []
    for lang in [site["languages"]["master"], *site["languages"]["translations"]]:
        for m, _b, _p in article.load_all(lang):
            if m.get("status") != "published" or members.state(m) != "public":
                continue
            if _stamp(str(m.get("published_at") or m.get("date") or "")) < cutoff:
                continue
            out.append(f"{config.origin()}{config.base_path()}"
                       f"/{lang}/{m['section']}/{m['slug']}/")
    return out


def _stamp(value: str) -> dt.datetime:
    """Datum nebo čas z hlavičky na porovnatelný okamžik v UTC."""
    try:
        d = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d


def recent_urls(hours: int = 48) -> list[str]:
    """Adresy článků vydaných v posledních `hours` hodinách."""
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    urls = _from_news_sitemap(cutoff) or _from_articles(cutoff)
    return sorted(set(urls))


def main() -> None:
    urls = recent_urls(48)
    config.log(f"IndexNow: nových adres za posledních 48 hodin: {len(urls)}")
    ping_indexnow(urls)


if __name__ == "__main__":
    main()
