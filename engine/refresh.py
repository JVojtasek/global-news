"""Bezpečně aplikuje úplné návrhy aktualizací z content/refresh-inbox/.

Naplánovaná úloha nikdy neupravuje živý článek přímo. Vytvoří kompletní
náhradní Markdown s polem ``refresh_target``. Tento modul ověří cestu,
identitu článku, zdroje, rozsah, citlivost i zachování URL a teprve potom
přepíše cílový soubor. Git uchovává předchozí verzi jako auditní stopu.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
from pathlib import Path

from . import article, config, inbox

REFRESH_INBOX = config.CONTENT / "refresh-inbox"
REJECTED = REFRESH_INBOX / "_rejected"
REVIEW = REFRESH_INBOX / "_review"


def _source_urls(meta: dict) -> set[str]:
    return {
        str(s.get("url") or "").strip()
        for s in (meta.get("sources") or [])
        if isinstance(s, dict) and str(s.get("url") or "").startswith("https://")
    }


def _target(meta: dict) -> tuple[Path | None, list[str]]:
    raw = str(meta.get("refresh_target") or "").strip()
    if not raw:
        return None, ["chybí refresh_target"]
    root = (config.CONTENT / "en").resolve()
    candidate = (config.ROOT / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, ["refresh_target musí být existující soubor uvnitř content/en/"]
    if not candidate.is_file() or candidate.suffix != ".md":
        return None, ["refresh_target neexistuje nebo není Markdown"]
    return candidate, []


def _check(original_meta: dict, original_body: str, new_meta: dict, new_body: str) -> list[str]:
    problems = inbox._rule_check(new_meta, new_body)
    for field in ("slug", "lang", "date", "section"):
        if str(new_meta.get(field) or "") != str(original_meta.get(field) or ""):
            problems.append(f"aktualizace nesmí změnit pole '{field}'")

    if original_meta.get("syndicated") or original_meta.get("origin"):
        problems.append("převzatý nebo kanonicky cizí článek se nesmí automaticky přepisovat")
    if not new_meta.get("refresh_reason"):
        problems.append("chybí konkrétní refresh_reason")
    if not new_meta.get("updated_at"):
        problems.append("chybí updated_at")

    policy = (config.site().get("automation") or {}).get("refresh_policy") or {}
    shrink = float(policy.get("maximum_word_shrink_ratio", 0.10))
    original_words = max(1, len(original_body.split()))
    if len(new_body.split()) < original_words * (1 - shrink):
        problems.append(f"aktualizace zkracuje text o více než {shrink:.0%}")

    added_sources = _source_urls(new_meta) - _source_urls(original_meta)
    correction = re.search(
        r"\b(correction|corrected|error|fix|clarif|oprava|chyba|upřesněn)\w*\b",
        str(new_meta.get("refresh_reason") or ""), re.I,
    )
    if policy.get("require_new_source_or_material_correction", True) and not added_sources and not correction:
        problems.append("aktualizace musí přidat nový kvalitní zdroj nebo popsat věcnou opravu")

    # Publikovaný citlivý text smí vzniknout jen jako návrh pro člověka.
    if new_meta.get("status") == "review":
        problems.append("citlivá aktualizace čeká na lidskou kontrolu")
    return problems


def _move(proposal: Path, destination: Path, problems: list[str]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.move(str(proposal), destination / proposal.name)
    (destination / f"{proposal.stem}.txt").write_text(
        "Aktualizace neprošla kontrolou:\n\n- " + "\n- ".join(problems),
        encoding="utf-8",
    )


def run() -> int:
    REFRESH_INBOX.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in REFRESH_INBOX.glob("*.md") if not p.name.startswith("_"))
    applied = 0
    for proposal in files:
        new_meta, new_body = article.parse(proposal.read_text(encoding="utf-8"))
        if not new_meta:
            _move(proposal, REJECTED, ["soubor nemá platnou YAML hlavičku"])
            continue
        target, problems = _target(new_meta)
        if problems or target is None:
            _move(proposal, REJECTED, problems)
            continue

        original_meta, original_body = article.parse(target.read_text(encoding="utf-8"))
        # Návrh musí být úplný článek. Pro publikační kontrolu se posuzuje
        # jako vydaný; bezpečnostní síto může status změnit na review.
        new_meta["status"] = original_meta.get("status", "published")
        new_meta["date"] = original_meta.get("date")
        new_meta["updated_at"] = str(new_meta.get("updated_at") or dt.date.today().isoformat())
        new_meta.setdefault("reviewed_at", new_meta["updated_at"])
        problems = _check(original_meta, original_body, new_meta, new_body)
        if problems:
            destination = REVIEW if any("lidskou kontrolu" in p for p in problems) else REJECTED
            _move(proposal, destination, problems)
            continue

        # Pole řízení aktualizace na živou stránku nepatří.
        new_meta.pop("refresh_target", None)
        new_meta.pop("refresh_reason", None)
        target.write_text(article.dump(new_meta, new_body), encoding="utf-8")
        proposal.unlink()
        applied += 1
        config.log(f"  ↻ {target.name}: bezpečně aktualizováno")

    config.log(f"Aktualizováno {applied} z {len(files)} navržených článků.")
    return applied


if __name__ == "__main__":
    run()
