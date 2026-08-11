"""Načtení nastavení + cesty. Nic tady neměň, měň data/site.yml."""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import datetime as dt

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
PUBLIC = ROOT / "public"

_cache: dict = {}


def site() -> dict:
    if "site" not in _cache:
        _cache["site"] = yaml.safe_load((DATA / "site.yml").read_text(encoding="utf-8"))
        lens_path = DATA / "wider_lens.yml"
        if lens_path.exists():
            _cache["site"]["wider_lens"] = yaml.safe_load(
                lens_path.read_text(encoding="utf-8")
            ) or {}
        automation_path = DATA / "editorial_automation.yml"
        if automation_path.exists():
            _cache["site"]["automation"] = yaml.safe_load(
                automation_path.read_text(encoding="utf-8")
            ) or {}
    return _cache["site"]


def sources() -> list:
    return yaml.safe_load((DATA / "sources.yml").read_text(encoding="utf-8"))


def series() -> list:
    return yaml.safe_load((DATA / "series.yml").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- state
def _state_path() -> pathlib.Path:
    return DATA / "state.json"


def load_state() -> dict:
    p = _state_path()
    if not p.exists():
        return {
            "seen_urls": [],
            "done_series": [],
            "published_slugs": [],
            "spend": {},
            "last_run": {},
        }
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    state["seen_urls"] = state.get("seen_urls", [])[-4000:]
    _state_path().write_text(
        json.dumps(state, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
    )


# ------------------------------------------------- autonomní režim
def days_since_human_activity() -> int:
    """Kolik dní uplynulo od poslední změny, kterou NEUDĚLAL robot.

    Robot commituje zprávy začínající '[bot]'. Cokoli jiného = člověk.
    """
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--invert-grep", "--grep=^\\[bot\\]"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
        ts = int(out.stdout.strip())
        return int((dt.datetime.now(dt.timezone.utc).timestamp() - ts) // 86400)
    except Exception:
        return 0


def is_autonomous() -> bool:
    limit = site()["editorial"]["autonomous_after_days"]
    return days_since_human_activity() >= limit


def confidence_threshold() -> int:
    ed = site()["editorial"]
    return (
        ed["confidence_threshold_autonomous"]
        if is_autonomous()
        else ed["confidence_threshold_normal"]
    )


def origin() -> str:
    """Jen doména, bez cesty. Např. https://jvojtasek.github.io"""
    from urllib.parse import urlparse
    u = urlparse(site()["brand"]["url"].rstrip("/"))
    return f"{u.scheme}://{u.netloc}"


def base_path() -> str:
    """Podsložka, ve které web běží. Prázdné, když běží na kořeni domény.

    U GitHub Pages projektu je to '/nazev-repozitare'. Bez tohohle by
    všechny odkazy na styly a obrázky mířily mimo web.
    """
    from urllib.parse import urlparse
    return urlparse(site()["brand"]["url"].rstrip("/")).path.rstrip("/")


def today() -> str:
    return dt.date.today().isoformat()


def log(msg: str) -> None:
    stamp = dt.datetime.now().strftime("%H:%M:%S")
    print(f"[{stamp}] {msg}", flush=True)


_commit_cache: dict = {}


def first_commit_iso(path) -> str:
    """Kdy článek poprvé vyšel — čas, kdy se soubor dostal do repozitáře.

    Je to poctivější než datum v hlavičce: to říká, ke kterému dni se
    text vztahuje, tohle říká, kdy ho čtenář mohl poprvé otevřít.
    """
    key = str(path)
    if key in _commit_cache:
        return _commit_cache[key]
    out = ""
    try:
        r = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%aI", "-1", "--", key],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        out = (r.stdout or "").strip().splitlines()[0] if r.stdout.strip() else ""
    except Exception:
        out = ""
    if not out:
        try:
            import datetime as _d
            out = _d.datetime.fromtimestamp(
                pathlib.Path(key).stat().st_mtime, _d.timezone.utc).isoformat()
        except Exception:
            out = ""
    _commit_cache[key] = out
    return out
