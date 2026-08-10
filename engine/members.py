"""Členství a předčasný přístup — a poctivé hranice statického webu.

Tenhle web nemá server ani databázi a mít je nebude. Plyne z toho jedna
věc, kterou je potřeba říkat nahlas, ne ji schovávat: **na statickém
webu nejde stránku doopravdy zamknout.** Co prohlížeč jednou dostane, to
už má; text schovaný přes CSS nebo JavaScript si kdokoli přečte ve
zdrojovém kódu. Placená zeď, která žádná není, je lež na jedno kliknutí.

Proto tady žádná placená zeď není. Děláme dvě věci, které bez serveru
opravdu fungují — čas a e-mail:

1. **Čas.** Článek `access: early` se prvních `early_days` dní postaví
   jen jako shrnutí (vrstva BRIEFLY) a nabídka členství. Zbytek textu
   v HTML vůbec není, takže není co obcházet. Jakmile lhůta uplyne,
   nejbližší stavba webu ho vydá celý a je z něj normální veřejný
   článek — bez zásahu člověka a bez další stránky navíc.

2. **E-mail.** Článek `access: members` se na web nevydá vůbec. Členové
   ho dostanou celý e-mailem od poskytovatele rozesílky. Na stránce pro
   členy zůstane jen titulek a perex, aby bylo vidět, co se posílá.

Co tenhle modul nedělá a dělat nebude: nezakládá účty, nepozná, kdo je
člen, a nikam neposílá nastavení čtenáře. Kdo je člen, ví poskytovatel
rozesílky. Web to nevidí a vědět nepotřebuje — a zájmy z prohlížeče
(zvlášť ty zdravotní) zařízení neopouštějí, viz EDITORIAL-CODE, oddíl 5.

Nastavení je v `data/members.yml`.
"""
from __future__ import annotations

import datetime as dt

import yaml

from . import config

STATES = ("public", "early", "members")

_cache: dict = {}


def cfg() -> dict:
    """Nastavení z data/members.yml. Když soubor chybí, členství je vypnuté."""
    if "cfg" not in _cache:
        p = config.DATA / "members.yml"
        data = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
        _cache["cfg"] = data or {}
    return _cache["cfg"]


def enabled() -> bool:
    return bool(cfg().get("enabled"))


def early_days() -> int:
    """Kolik dní drží předčasný přístup. Nesmysl v nastavení = 7 dní."""
    try:
        return max(0, int(cfg().get("early_days", 7)))
    except (TypeError, ValueError):
        return 7


def _date(value) -> dt.date | None:
    """Datum z hlavičky. YAML ho vrací jednou jako text, jindy jako datum."""
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _today(today=None) -> dt.date:
    return _date(today) or dt.date.today()


def access(meta: dict) -> str:
    """Co je napsané v hlavičce. Chybí-li pole nebo je v něm nesmysl,
    článek je veřejný — mlčení nikdy neznamená zamčeno."""
    want = str(meta.get("access") or "public").strip().lower()
    return want if want in STATES else "public"


def opens_on(meta: dict) -> str:
    """Den, kdy se článek otevře všem (ISO). Prázdné, když se ho to netýká."""
    if access(meta) != "early" or not enabled():
        return ""
    d = _date(meta.get("date"))
    return (d + dt.timedelta(days=early_days())).isoformat() if d else ""


def state(meta: dict, today=None) -> str:
    """V jakém stavu je článek dnes: public | early | members.

    `early` se sám překlopí na `public`, jakmile je `date + early_days`
    dřív nebo dnes. Nikdo to nemusí hlídat, stačí, že web někdy vyjde
    znovu — a ten se staví každý den.
    """
    want = access(meta)
    if want == "public":
        return "public"
    if not enabled():
        # Když se členství vypne, nemá se čtenář kam přihlásit, takže
        # držet článek zpátky nedává smysl — předčasný přístup se prostě
        # nekoná. Text psaný jen pro e-mail ale na web nepustíme:
        # vypnutý přepínač nesmí zveřejnit něco, co k vydání na webu
        # nikdy určené nebylo.
        return "public" if want == "early" else "members"
    if want == "members":
        return "members"
    d = _date(meta.get("date"))
    if d is None:
        # Bez data neumíme spočítat, kdy se má otevřít. Radši ho vydáme,
        # než aby zůstal zamčený navždycky kvůli chybě v hlavičce.
        return "public"
    return "public" if d + dt.timedelta(days=early_days()) <= _today(today) else "early"


def days_left(meta: dict, today=None) -> int:
    """Kolik dní ještě zbývá, než se článek otevře všem. 0 = otevírá dnes."""
    if state(meta, today) != "early":
        return 0
    d = _date(meta.get("date"))
    if d is None:
        return 0
    return max(0, (d + dt.timedelta(days=early_days()) - _today(today)).days)


def tiers(lang: str) -> list[dict]:
    """Úrovně členství připravené pro šablonu v jednom jazyce."""
    out = []
    for tr in cfg().get("tiers", []) or []:
        out.append({
            "id": tr.get("id", ""),
            "name": tr.get(lang) or tr.get("en", ""),
            "price": tr.get("price_eur", 0),
            "blurb": tr.get(f"blurb_{lang}") or tr.get("blurb_en", ""),
            "perks": tr.get(f"perks_{lang}") or tr.get("perks_en", []) or [],
        })
    return out
