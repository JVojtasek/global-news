"""Kontrola zdraví projektu. Spusť kdykoli: python -m engine.doctor

Řekne ti česky, co funguje a co ne. Nic nemění.
"""
from __future__ import annotations

import datetime as dt
import json
import os

from . import analyst, article, config, memory

OK, WARN, BAD = "✅", "⚠️ ", "❌"


def run() -> int:
    site = config.site()
    problems = 0
    print("=" * 60)
    print("  KONTROLA PROJEKTU —", dt.datetime.now().strftime("%d.%m.%Y %H:%M"))
    print("=" * 60)

    # --- klíče ---
    keys = {"ANTHROPIC_API_KEY": "Claude API", "OPENAI_API_KEY": "OpenAI API"}
    have = [n for n in keys if os.environ.get(n)]
    if have:
        print(f"{OK} API klíče: {', '.join(keys[n] for n in have)}")
    else:
        print(f"{WARN}Žádný API klíč. Systém pojede jen z článků, které dodá "
              f"naplánovaná Claude úloha do content/inbox/.")

    # --- zdroje ---
    print(f"{OK} Zdrojů zpráv v seznamu: {len(config.sources())}")

    # --- události ---
    ev = config.DATA / "events.json"
    if ev.exists():
        events = json.loads(ev.read_text(encoding="utf-8"))
        print(f"{OK} Událostí v zásobníku: {len(events)}"
              + (f"  (nejsilnější {events[0]['score']}/100)" if events else ""))
    else:
        print(f"{WARN}Zatím žádné události — spusť `python -m engine.collect`.")

    # --- obsah ---
    master = site["languages"]["master"]
    arts = article.load_all(master)
    by_status: dict = {}
    for m, _, _ in arts:
        by_status[m.get("status", "?")] = by_status.get(m.get("status", "?"), 0) + 1
    print(f"{OK} Článků celkem ({master}): {len(arts)}  {by_status or ''}")

    reserve = by_status.get("reserve", 0)
    target = site["editorial"]["reserve_target"]
    if reserve >= target:
        print(f"{OK} Zásoba delších článků: {reserve}/{target}")
    elif reserve > site["editorial"]["reserve_emergency"]:
        print(f"{WARN}Zásoba klesá: {reserve}/{target}")
    else:
        print(f"{BAD} ZÁSOBA KRITICKY NÍZKÁ: {reserve}. Web brzy nebude mít co vydávat.")
        problems += 1

    review = by_status.get("review", 0)
    if review:
        print(f"{WARN}{review} článků čeká na tvoje schválení "
              f"(otevři content/{master}/ a změň status na `published`).")

    # --- překlady ---
    for lang in site["languages"]["translations"]:
        n = len([1 for m, _, _ in article.load_all(lang) if m.get("status") == "published"])
        pub = len([1 for m, _, _ in arts if m.get("status") == "published"])
        mark = OK if pub == 0 or n >= pub * 0.8 else WARN
        print(f"{mark}Překlad {lang}: {n} z {pub} publikovaných")

    # --- paměť a analytik ---
    try:
        mem = memory.load()
        act = memory.active(days=14, min_entries=3)
        n = len(mem.get("threads", []))
        if n == 0:
            print(f"{WARN}Paměť je zatím prázdná — naplní se během prvních dnů.")
        else:
            print(f"{OK} Paměť: {n} vláken, z toho {len(act)} zralých na analýzu")
        fc = analyst.load_forecasts()["forecasts"]
        op = [f for f in fc if f["status"] == "open"]
        sc = analyst.scoreboard()
        if fc:
            print(f"{OK} Předpovědi: {len(op)} otevřených, {sc['resolved']} vyhodnocených"
                  + (f", Brier {sc['brier']:.3f} — {sc['verdict_cs']}" if sc["resolved"] else ""))
    except Exception as e:  # noqa: BLE001
        print(f"{WARN}Paměť se nepodařilo přečíst: {str(e)[:80]}")

    # --- převzaté články ---
    syn = len([1 for m, _, _ in arts if m.get("type") == "syndicated"])
    if syn:
        print(f"{OK} Převzatých článků (s uvedením licence): {syn}")

    # --- poptávaná témata ---
    tp = config.DATA / "topics.json"
    if tp.exists():
        try:
            d = json.loads(tp.read_text(encoding="utf-8"))
            n = len(d.get("topics", []))
            if n:
                print(f"{OK} Témat s doloženou poptávkou: {n} "
                      f"(nejsilnější „{d['topics'][0]['term']}“)")
            else:
                print(f"{WARN}Žádná použitelná témata — dnešní trendy byly asi samý sport.")
        except Exception:  # noqa: BLE001
            pass

    # --- vlastní import ---
    imp = len([1 for m, _, _ in arts if m.get("type") == "imported"])
    if imp:
        print(f"{OK} Vlastních článků převzatých z QMA: {imp}")

    # --- režim ---
    days = config.days_since_human_activity()
    if config.is_autonomous():
        print(f"{WARN}AUTONOMNÍ REŽIM — nikdo do projektu nesáhl {days} dní. "
              f"Systém je opatrnější (práh {config.confidence_threshold()}/100).")
    else:
        print(f"{OK} Běžný režim (poslední lidský zásah před {days} dny, "
              f"práh {config.confidence_threshold()}/100)")

    # --- útrata ---
    st = config.load_state()
    spend = st.get("spend", {})
    if spend:
        last = sorted(spend.items())[-7:]
        total = sum(v for _, v in last)
        print(f"{OK} Odhad útraty za AI (7 dní): ${total:.2f}  "
              f"(strop ${site['ai']['max_usd_per_day']}/den)")

    # --- inbox ---
    inbox = list((config.CONTENT / "inbox").glob("*.md")) if (config.CONTENT / "inbox").exists() else []
    rej = list((config.CONTENT / "inbox" / "_rejected").glob("*.md")) if (config.CONTENT / "inbox" / "_rejected").exists() else []
    if inbox:
        print(f"{WARN}V inboxu čeká {len(inbox)} nezpracovaných článků.")
    if rej:
        print(f"{WARN}{len(rej)} článků neprošlo kontrolou — viz content/inbox/_rejected/")

    print("=" * 60)
    print("HOTOVO." if not problems else f"NALEZENO {problems} VÁŽNÝCH PROBLÉMŮ.")
    return problems


if __name__ == "__main__":
    raise SystemExit(1 if run() else 0)
