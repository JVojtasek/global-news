"""Překlad publikovaných článků do dalších jazyků.

Přeloží jen to, co ještě přeložené není. Když AI nefunguje, tiše skončí
a web zůstane v angličtině — nic se nerozbije.
"""
from __future__ import annotations

import sys

from . import ai, article, config, safety

PROMPT = (config.ROOT / "engine" / "prompts" / "translate.md").read_text(encoding="utf-8")

LANG_NAMES = {"cs": "čeština", "sk": "slovenčina", "pl": "polski", "de": "Deutsch", "es": "español"}

def run(limit: int = 6) -> int:
    site = config.site()
    master = site["languages"]["master"]
    done = 0

    # --- 1) články, které přišly v jiném jazyce, přeložíme DO hlavního jazyka ---
    master_slugs = {m.get("slug") for m, _, _ in article.load_all(master)}
    for lang in site["languages"]["translations"]:
        orphans = [
            (m, b) for m, b, _ in article.load_all(lang)
            if m.get("status") == "published" and m.get("slug") not in master_slugs
            and safety.translation_allowed(m)
        ]
        orphans.sort(key=lambda t: t[0].get("date", ""), reverse=True)
        for meta, body in orphans[:limit]:
            try:
                config.log(f"  → {master} (z {lang}): {meta['title'][:55]}")
                raw = ai.ask(
                    PROMPT + f"\n\nCÍLOVÝ JAZYK: English (kód `{master}`)",
                    article.dump(meta, body), max_tokens=9000, temperature=0.3)
                m2, b2 = article.parse(raw)
                if not m2:
                    continue
                m2.update({
                    "lang": master, "slug": meta["slug"], "date": meta["date"],
                    "status": meta["status"], "confidence": meta.get("confidence", 0),
                })
                safety.copy_provenance(meta, m2, source_lang=lang)
                article.save(m2, b2)
                master_slugs.add(meta["slug"])
                done += 1
            except ai.BudgetExceeded as e:
                config.log(f"STOP: {e}")
                return done
            except Exception as e:  # noqa: BLE001
                config.log(f"  ! překlad selhal: {str(e)[:140]}")

    # --- 2) běžný směr: z hlavního jazyka do ostatních ---

    for target in site["languages"]["translations"]:
        existing = {m.get("slug") for m, _, _ in article.load_all(target)}
        todo = [
            (m, b) for m, b, _ in article.load_all(master)
            if m.get("status") == "published" and m.get("slug") not in existing
            and safety.translation_allowed(m)
        ]
        todo.sort(key=lambda t: t[0].get("date", ""), reverse=True)

        for meta, body in todo[:limit]:
            try:
                config.log(f"  → {target}: {meta['title'][:60]}")
                raw = ai.ask(
                    PROMPT + f"\n\nCÍLOVÝ JAZYK: {LANG_NAMES.get(target, target)} (kód `{target}`)",
                    article.dump(meta, body),
                    max_tokens=9000,
                    temperature=0.3,
                )
                m2, b2 = article.parse(raw)
                if not m2:
                    config.log("  ! překlad nemá hlavičku, přeskakuji")
                    continue
                m2["lang"] = target
                m2["slug"] = meta["slug"]
                m2["date"] = meta["date"]
                m2["status"] = meta["status"]
                m2["confidence"] = meta.get("confidence", 0)
                safety.copy_provenance(meta, m2, source_lang=master)
                article.save(m2, b2)
                done += 1
            except ai.BudgetExceeded as e:
                config.log(f"STOP: {e}")
                return done
            except Exception as e:  # noqa: BLE001
                config.log(f"  ! překlad selhal: {str(e)[:160]}")

    config.log(f"Přeloženo {done} článků.")
    return done


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
