"""Příjem hotových článků ze složky content/inbox/.

Sem odkládají články naplánované úlohy ChatGPT Work (nebo ty ručně).
Tenhle modul je BEZPEČNOSTNÍ SÍTO a nestojí ani korunu — funguje
na pravidlech, ne na AI. Kontroluje:
  * formát a úplnost redakčních vrstev
  * přítomnost zdrojů u zpravodajství
  * zakázané formulace (proroctví, zbožné fráze místo argumentu)
  * duplicity

Co projde → content/<lang>/.  Co neprojde → content/inbox/_rejected/
s vysvětlením, proč.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil

from . import article, config, edition

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
    # --- právní pojistky (viz data/EDITORIAL-CODE.md) ---
    (r"\b(?:the )?holocaust (?:hoax|never happened|is a lie)\b", "popírání holokaustu"),
    (r"\b(?:they|the government|elites) (?:are )?(?:secretly )?(?:controlling|poisoning) (?:us|the population)\b",
     "konspirační tvrzení bez vyvrácení"),
    (r"\bnew world order\b(?![^.]{0,80}(?:claim|conspiracy|debunk|false|myth))", "konspirační tvrzení bez vyvrácení"),
    (r"\bwake up,? sheeple\b", "konspirační rétorika"),
    (r"\b(?:cure|cures|cured) (?:for )?cancer\b(?![^.]{0,60}(?:trial|study|research|not))", "zdravotní tvrzení bez opory"),
    (r"\byou should (?:buy|sell|invest in)\b", "investiční doporučení"),
    (r"\b(?:kill|exterminate|deport) (?:all|every) \w+", "podněcování k násilí"),
]

# Slova, po kterých článek vždy čeká na člověka, i když prošel vším ostatním
NEEDS_HUMAN = re.compile(
    r"\b(election|referendum|ballot|conspiracy|hoax|debunk|"
    r"rape|abuse|trafficking|suicide|self-harm|"
    r"convicted|indicted|accused|alleged|lawsuit|"
    r"death toll|casualties|killed|children)\b", re.I)

# Obvinění bez opory: sloveso zločinu, u kterého poblíž chybí slovo,
# které z něj dělá tvrzení někoho jiného ("alleged", "according to"…).
CRIME_VERB = re.compile(
    r"\b(?:stole|embezzled|defrauded|bribed|laundered|smuggled|assaulted|"
    r"murdered|abused|falsified|covered up|lied about)\b", re.I)
ATTRIBUTED = re.compile(
    r"\b(alleged|allegedly|accused|according to|court|prosecutors|"
    r"charged with|indicted|convicted|denies|reportedly)\b", re.I)

MIN_WORDS = 500


def _automation_rules() -> tuple[dict, dict]:
    cfg = config.site().get("automation") or {}
    return cfg.get("minimum_words") or {}, cfg.get("minimum_sources") or {}


def _source_urls(meta: dict) -> list[str]:
    return [
        str(s.get("url", "")).strip()
        for s in (meta.get("sources") or [])
        if isinstance(s, dict) and str(s.get("url", "")).startswith("https://")
    ]


def _quality_score(meta: dict, body: str) -> int:
    """Deterministická publikační známka pro text dodaný naplánovanou úlohou.

    Nehraje si na pravděpodobnost, že je článek pravdivý. Ověřuje jen věci,
    které umíme bez další AI opravdu spočítat: zdroje, rozsah, vrstvy,
    jedinečnost odkazů a přítomnost praktického vzdělávacího prvku.
    """
    secs = article.sections(body)
    urls = _source_urls(meta)
    words = len(body.split())
    score = 35
    score += min(len(set(urls)), 5) * 6
    score += 10 if {"EVIDENCE", "PERSPECTIVES"}.issubset(secs) else 0
    score += 8 if "BRIEFLY" in secs else 0
    score += 7 if words >= 900 else 0
    score += 5 if words >= 1200 else 0
    score += 5 if isinstance(meta.get("quiz"), dict) else 0
    return min(score, 95)


def _planned_slot(meta: dict) -> dict | None:
    """Return the deterministic edition specification for one article."""
    try:
        day = dt.date.fromisoformat(str(meta.get("date") or ""))
        slot = int(meta.get("edition_slot") or 0)
    except (TypeError, ValueError):
        return None
    plan = edition.build(day)
    specs = list(plan.get("slots") or [])
    if plan.get("reserve"):
        specs.append(plan["reserve"])
    return next((spec for spec in specs if int(spec.get("slot") or 0) == slot), None)


def _edition_check(meta: dict, body: str) -> list[str]:
    """Enforce the contract between the daily plan and scheduled articles.

    Ordinary collected or commissioned news never occupies an edition slot.
    Scheduled output must match the section, type, length and status assigned
    by the deterministic plan. This prevents an unrelated breaking-news item
    from silently becoming the day's flagship.
    """
    problems = []
    try:
        slot = int(meta.get("edition_slot") or 0)
    except (TypeError, ValueError):
        return ["edition_slot musí být celé číslo 0–7"]

    if not meta.get("automation_generated"):
        if slot != 0:
            problems.append("běžný článek nesmí obsadit automatický edition_slot 1–7")
        return problems

    spec = _planned_slot(meta)
    if not spec or slot not in range(1, 8):
        return ["automatický článek nemá platný edition_slot 1–7 pro svůj den"]

    if meta.get("section") != spec.get("section"):
        problems.append(
            f"slot {slot} patří rubrice {spec.get('section')}, ne {meta.get('section')}"
        )
    if meta.get("type") != spec.get("type"):
        problems.append(f"slot {slot} vyžaduje typ {spec.get('type')}, ne {meta.get('type')}")

    words = len(body.split())
    low, high = int(spec.get("min_words") or 0), int(spec.get("max_words") or 10**9)
    if not low <= words <= high:
        problems.append(f"slot {slot} má {words} slov, plán vyžaduje {low}–{high}")

    required_status = "reserve" if slot == 7 else "draft"
    if meta.get("status") != required_status:
        problems.append(
            f"slot {slot} musí přijít se status: {required_status}, ne {meta.get('status')}"
        )

    if slot <= 6:
        quiz = meta.get("quiz") or {}
        options = quiz.get("options") if isinstance(quiz, dict) else None
        answer = quiz.get("answer") if isinstance(quiz, dict) else None
        if (
            not isinstance(quiz, dict)
            or len(str(quiz.get("question") or "").strip()) < 12
            or not isinstance(options, list)
            or len(options) != 3
            or not isinstance(answer, int)
            or answer not in range(3)
            or len(str(quiz.get("explanation") or "").strip()) < 12
        ):
            problems.append(f"slot {slot} nemá platný věcný kvíz se třemi možnostmi")
    return problems


def _rule_check(meta: dict, body: str) -> list[str]:
    problems = article.validate(meta, body)
    problems.extend(_edition_check(meta, body))

    words = len(body.split())
    min_words, min_sources = _automation_rules()
    article_type = str(meta.get("type") or "news")
    required_words = int(min_words.get(article_type, MIN_WORDS))
    if words < required_words:
        problems.append(
            f"článek je příliš krátký ({words} slov, minimum {required_words} pro typ {article_type})"
        )

    low = body.lower()
    for pattern, why in BANNED:
        m = re.search(pattern, low)
        if m:
            problems.append(f"zakázaná formulace ({why}): „…{low[max(0, m.start()-40):m.end()+40]}…“")

    # zpravodajský článek musí mít funkční odkazy na zdroje
    required_sources = int(min_sources.get(article_type, 2 if article_type == "news" else 0))
    urls = _source_urls(meta)
    if len(set(urls)) < required_sources:
        problems.append(
            f"článek má {len(set(urls))} unikátních HTTPS zdrojů, minimum je "
            f"{required_sources} pro typ {article_type}"
        )

    # obvinění bez uvedení, že jde o cizí tvrzení, je žalovatelné
    for m in CRIME_VERB.finditer(body):
        okolo = body[max(0, m.start() - 260): m.end() + 260]
        if not ATTRIBUTED.search(okolo):
            problems.append(
                f"obvinění bez uvedení zdroje a bez slova „alleged/accused“: "
                f"„…{okolo[max(0, m.start() - (m.start() - 60)):][:90]}…“")
            break

    # citlivá témata nikdy nevycházejí sama
    hit = NEEDS_HUMAN.search(body + " " + str(meta.get("title", "")))
    if hit and meta.get("status") == "published":
        meta["status"] = "review"
        meta.setdefault("review_reason", f"citlivé téma: {hit.group(0)}")

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
    occupied_slots = set()
    for lang_dir in config.CONTENT.iterdir():
        if not lang_dir.is_dir() or lang_dir.name == "inbox":
            continue
        for existing_path in lang_dir.glob("*.md"):
            existing_meta, _ = article.parse(existing_path.read_text(encoding="utf-8"))
            try:
                existing_slot = int(existing_meta.get("edition_slot") or 0)
            except (TypeError, ValueError):
                existing_slot = 0
            if existing_slot > 0:
                occupied_slots.add((existing_meta.get("date"), existing_meta.get("lang"), existing_slot))

    inbox_slot_counts = {}
    for inbox_path in files:
        inbox_meta, _ = article.parse(inbox_path.read_text(encoding="utf-8"))
        try:
            inbox_slot = int(inbox_meta.get("edition_slot") or 0)
        except (TypeError, ValueError):
            inbox_slot = 0
        if inbox_slot > 0:
            key = (inbox_meta.get("date"), inbox_meta.get("lang"), inbox_slot)
            inbox_slot_counts[key] = inbox_slot_counts.get(key, 0) + 1
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

        try:
            slot = int(meta.get("edition_slot") or 0)
        except (TypeError, ValueError):
            slot = 0
        slot_key = (meta.get("date"), meta.get("lang"), slot)
        if slot > 0 and (slot_key in occupied_slots or inbox_slot_counts.get(slot_key, 0) > 1):
            problems.append(
                f"edition_slot {slot} už je pro {meta.get('date')} a jazyk {meta.get('lang')} obsazen"
            )

        if target.name in existing:
            problems.append("článek se stejným názvem už existuje")

        if problems:
            shutil.move(str(p), REJECTED / p.name)
            (REJECTED / (p.stem + ".txt")).write_text(
                "Článek neprošel kontrolou:\n\n- " + "\n- ".join(problems), encoding="utf-8"
            )
            config.log(f"  ✗ {p.name}: {problems[0]}")
            continue

        # Článek prošel – rozhodneme, jestli ven hned, nebo do zásoby.
        # U výstupu naplánované úlohy počítáme reprodukovatelnou známku
        # kvality. Model si nesmí sám napsat líbivé 99/100.
        if meta.get("automation_generated"):
            meta["confidence"] = _quality_score(meta, body)
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
        if slot > 0:
            occupied_slots.add(slot_key)
        accepted += 1
        config.log(f"  ✓ {target.name}  ({meta['status']}, jistota {conf or '—'})")

    config.log(f"Přijato {accepted} z {len(files)} článků.")
    return accepted


if __name__ == "__main__":
    run()
