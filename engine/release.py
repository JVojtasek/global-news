"""Vydávání ze zásoby.

Web nikdy nesmí být závislý na tom, jestli dnes AI něco stihla.
Proto se biblické články vyrábějí dopředu do zásoby (status: reserve)
a tenhle modul je vydává podle plánu.

Publikační dny biblických článků: pondělí, středa, pátek.
"""
from __future__ import annotations

import datetime as dt

from . import article, config

DAY_NAMES = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def _bible_days() -> set:
    names = config.site()["editorial"].get("bible_days", ["mon", "wed", "fri"])
    return {DAY_NAMES[n.lower()[:3]] for n in names if n.lower()[:3] in DAY_NAMES}


def run() -> int:
    today = dt.date.today()
    lang = config.site()["languages"]["master"]
    arts = article.load_all(lang)

    published_today = [
        m for m, _, _ in arts
        if m.get("status") == "published" and m.get("date") == today.isoformat() and m.get("type") == "feature"
    ]
    if today.weekday() not in _bible_days():
        config.log("Dnes není den pro delší článek.")
        return 0
    if published_today:
        config.log("Delší článek už dnes vyšel.")
        return 0

    reserve = sorted(
        [(m, b, p) for m, b, p in arts if m.get("status") == "reserve" and m.get("type") == "feature"],
        key=lambda t: t[0].get("date", ""),
    )
    if not reserve:
        config.log("⚠️  Zásoba delších článků je prázdná.")
        return 0

    meta, body, path = reserve[0]
    old_path = path
    meta["status"] = "published"
    meta["date"] = today.isoformat()
    new_path = article.save(meta, body)
    if old_path != new_path and old_path.exists():
        old_path.unlink()
    config.log(f"Vydáno ze zásoby: {meta['title']}  (zbývá {len(reserve) - 1})")

    if len(reserve) - 1 <= config.site()["editorial"]["reserve_emergency"]:
        config.log("⚠️  ZÁSOBA DOCHÁZÍ – systém si příště vyžádá víc delších článků.")
    return 1


if __name__ == "__main__":
    run()
