"""Příjem hotových článků ze složky content/inbox/.

Sem odkládá články naplánovaná Claude úloha (nebo ty ručně).
Tenhle modul je BEZPEČNOSTNÍ SÍTO a nestojí ani korunu — funguje
na pravidlech, ne na AI. Kontroluje:
  * formát a úplnost všech pěti vrstev
  * přítomnost zdrojů u zpravodajství
  * zakázané formulace (proroctví, zbožné fráze místo argumentu)
  * duplicity

Co projde → content/<lang>/.  Co neprojde → content/inbox/_rejected/
s vysvětlením, proč.
"""
from __future__ import annotations

import re
import shutil

from . import article, config

INBOX = config.CONTENT / "inbox"
REJECTED = INBOX / "_rejected"

# Formulace, které v tomhle projektu nesmí projít. Regulární výrazy.
BANNED = [
    (r"\bfulfil(?:l|ls|led|ling|ment)\b[^.]{0,60}\bprophec", "označuje událost za naplnění proroctví"),
    (r"\bnapl(ňuje|nění)\b[^.]{0,60}\bproroctv", "označuje událost za naplnění proroctví"),
    (r"\bthis is (?:a )?(?:sign|warning|judgment) from god\b", "tvrdí, že zná Boží úmysl"),
    (r"\bgod is (?:clearly|obviously) (?:judging|punishing)\b", "tvrdí, že zná Boží úmysl"),
    (r"\bthe bible predicted\b", "tvrdí, že Bible předpověděla konkrétní událost"),
    (r"\bend times are here\b", "senzacechtivá eschatologie"),
    (r"\bwe must (?:all )?repent\b", "moralizování / výzva místo otázky"),
    (r"\bas christians,? we (?:must|should|need to)\b", "moralizování"),
]

MIN_WORDS = 500


def _rule_check(meta: dict, body: str) -> list[str]:
    problems = article.validate(meta, body)

    words = len(body.split())
    if words < MIN_WORDS:
        problems.append(f"článek je příliš krátký ({words} slov, minimum {MIN_WORDS})")

    low = body.lower()
    for pattern, why in BANNED:
        m = re.search(pattern, low)
        if m:
            problems.append(f"zakázaná formulace ({why}): „…{low[max(0, m.start()-40):m.end()+40]}…“")

    # zpravodajský článek musí mít funkční odkazy na zdroje
    if meta.get("type") == "news":
        urls = [s.get("url", "") for s in (meta.get("sources") or []) if isinstance(s, dict)]
        if len([u for u in urls if u.startswith("http")]) < 2:
            problems.append("zpravodajský článek má méně než 2 zdroje s odkazem")

    # čitelnost — zeď textu a souvětí na pět řádků nikdo nečte
    paras = [x for x in body.split("\n\n") if len(x.split()) > 15 and not x.startswith(("#", ">", "-"))]
    if paras:
        longest = max(len(x.split()) for x in paras)
        if longest > 190:
            problems.append(f"nejdelší odstavec má {longest} slov — je to zeď textu")
        sentences = [x for x in re.split(r"[.!?]+", " ".join(paras)) if len(x.split()) > 2]
        if sentences:
            avg = sum(len(x.split()) for x in sentences) / len(sentences)
            if avg > 32:
                problems.append(f"průměrná věta má {avg:.0f} slov — příliš složité souvětí")

    # článek v režimu open nesmí sklouznout k Bibli
    if meta.get("depth") == "open":
        if re.search(r"\b(bible|scripture|jesus christ|gospel of|psalm \d|genesis \d)\b", low):
            problems.append("článek má depth: open, ale zmiňuje Bibli — patří sem obecná vrstva")

    return problems


def run() -> int:
    INBOX.mkdir(parents=True, exist_ok=True)
    REJECTED.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in INBOX.glob("*.md") if not p.name.startswith("_"))
    if not files:
        config.log("Inbox je prázdný.")
        return 0

    existing = {p.name for lang in ("en",) for p in (config.CONTENT / lang).glob("*.md")}
    accepted = 0

    for p in files:
        meta, body = article.parse(p.read_text(encoding="utf-8"))
        if not meta:
            shutil.move(str(p), REJECTED / p.name)
            (REJECTED / (p.stem + ".txt")).write_text("Soubor nemá platnou hlavičku ---", encoding="utf-8")
            config.log(f"  ✗ {p.name}: chybí hlavička")
            continue

        meta, body = article.normalise(meta, body)
        problems = _rule_check(meta, body)
        target = article.path_for(meta)

        if target.name in existing:
            problems.append("článek se stejným názvem už existuje")

        if problems:
            shutil.move(str(p), REJECTED / p.name)
            (REJECTED / (p.stem + ".txt")).write_text(
                "Článek neprošel kontrolou:\n\n- " + "\n- ".join(problems), encoding="utf-8"
            )
            config.log(f"  ✗ {p.name}: {problems[0]}")
            continue

        # článek prošel – rozhodneme, jestli ven hned, nebo do zásoby
        threshold = config.confidence_threshold()
        conf = int(meta.get("confidence") or 0)
        if meta.get("status") in ("published", "reserve", "scheduled", "review"):
            pass  # autor už rozhodl
        elif conf and conf < threshold:
            meta["status"] = "review"
        elif meta.get("type") == "feature":
            meta["status"] = "reserve"
        else:
            meta["status"] = "published"

        article.save(meta, body)
        p.unlink()
        existing.add(target.name)
        accepted += 1
        config.log(f"  ✓ {target.name}  ({meta['status']}, jistota {conf or '—'})")

    config.log(f"Přijato {accepted} z {len(files)} článků.")
    return accepted


if __name__ == "__main__":
    run()
