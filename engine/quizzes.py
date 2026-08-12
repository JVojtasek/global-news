"""Load and validate My Paper's standalone daily quizzes.

The browser calculates results locally.  This module deliberately keeps the
content format deterministic so a scheduled task cannot publish an arbitrary
script or silently turn a self-check into a medical diagnosis.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from . import config


QUIZ_DIR = config.DATA / "quizzes"
MODES = {"assessment", "profile", "knowledge"}
CATEGORIES = {
    "personality", "resilience", "relationships", "preparedness",
    "health-literacy", "money-habits", "science", "media-literacy",
}
_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class QuizValidationError(ValueError):
    """A quiz file is unsafe or cannot be rendered consistently."""


def _https(value: object) -> bool:
    try:
        parsed = urlparse(str(value))
        return parsed.scheme == "https" and bool(parsed.netloc)
    except ValueError:
        return False


def _local(value: object, lang: str) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or "").strip()
    return str(value or "").strip()


def _require_local(value: object, field: str) -> None:
    if not isinstance(value, dict) or not _local(value, "en") or not _local(value, "cs"):
        raise QuizValidationError(f"{field} must contain non-empty en and cs text")


def _validate(raw: dict, path: Path) -> dict:
    where = path.name
    if raw.get("schema_version") != 1:
        raise QuizValidationError(f"{where}: schema_version must be 1")
    slug = str(raw.get("slug") or "")
    if not _SLUG.fullmatch(slug):
        raise QuizValidationError(f"{where}: invalid slug")
    try:
        dt.date.fromisoformat(str(raw.get("date") or ""))
    except ValueError as exc:
        raise QuizValidationError(f"{where}: invalid ISO date") from exc
    if raw.get("category") not in CATEGORIES:
        raise QuizValidationError(f"{where}: unsupported category")
    mode = raw.get("mode")
    if mode not in MODES:
        raise QuizValidationError(f"{where}: unsupported mode")
    minutes = raw.get("estimated_minutes")
    if not isinstance(minutes, int) or minutes not in range(2, 11):
        raise QuizValidationError(f"{where}: estimated_minutes must be 2-10")

    copy = raw.get("copy")
    if not isinstance(copy, dict):
        raise QuizValidationError(f"{where}: copy is required")
    for field in ("title", "dek", "intro", "disclaimer"):
        _require_local(copy.get(field), f"{where}: copy.{field}")

    dimensions = raw.get("dimensions") or []
    if not isinstance(dimensions, list):
        raise QuizValidationError(f"{where}: dimensions must be a list")
    dim_ids = set()
    for dim in dimensions:
        dim_id = str(dim.get("id") or "") if isinstance(dim, dict) else ""
        if not _SLUG.fullmatch(dim_id) or dim_id in dim_ids:
            raise QuizValidationError(f"{where}: invalid or duplicate dimension")
        dim_ids.add(dim_id)
        for field in ("label", "why", "action"):
            _require_local(dim.get(field), f"{where}: dimension.{field}")

    questions = raw.get("questions")
    if not isinstance(questions, list) or not 6 <= len(questions) <= 20:
        raise QuizValidationError(f"{where}: quizzes need 6-20 questions")
    question_ids = set()
    maximum = 0
    for question in questions:
        if not isinstance(question, dict):
            raise QuizValidationError(f"{where}: malformed question")
        qid = str(question.get("id") or "")
        if not _SLUG.fullmatch(qid) or qid in question_ids:
            raise QuizValidationError(f"{where}: invalid or duplicate question id")
        question_ids.add(qid)
        _require_local(question.get("text"), f"{where}: question.text")
        options = question.get("options")
        if not isinstance(options, list) or not 3 <= len(options) <= 5:
            raise QuizValidationError(f"{where}: every question needs 3-5 options")
        for option in options:
            if not isinstance(option, dict):
                raise QuizValidationError(f"{where}: malformed option")
            _require_local(option.get("label"), f"{where}: option.label")

        if mode == "assessment":
            dim_id = str(question.get("dimension") or "")
            if dim_id not in dim_ids:
                raise QuizValidationError(f"{where}: assessment question has unknown dimension")
            scores = [option.get("score") for option in options]
            if any(not isinstance(score, int) or score not in range(0, 4) for score in scores):
                raise QuizValidationError(f"{where}: assessment scores must be integers 0-3")
            maximum += max(scores)
        elif mode == "profile":
            if len(dim_ids) < 3:
                raise QuizValidationError(f"{where}: profile quizzes need at least 3 dimensions")
            for option in options:
                scores = option.get("scores")
                if not isinstance(scores, dict) or not scores:
                    raise QuizValidationError(f"{where}: profile option scores are required")
                if not set(scores).issubset(dim_ids) or any(
                    not isinstance(score, int) or score not in range(0, 4)
                    for score in scores.values()
                ):
                    raise QuizValidationError(f"{where}: invalid profile scores")
        else:
            correct = [option.get("correct") is True for option in options]
            if sum(correct) != 1:
                raise QuizValidationError(f"{where}: knowledge question needs one correct option")
            _require_local(question.get("explanation"), f"{where}: question.explanation")
            maximum += 1

    outcomes = raw.get("outcomes")
    if mode in {"assessment", "knowledge"}:
        if not isinstance(outcomes, list) or len(outcomes) < 3:
            raise QuizValidationError(f"{where}: at least three score outcomes are required")
        covered: list[int] = []
        for outcome in outcomes:
            if not isinstance(outcome, dict):
                raise QuizValidationError(f"{where}: malformed outcome")
            lo, hi = outcome.get("min"), outcome.get("max")
            if not isinstance(lo, int) or not isinstance(hi, int) or lo < 0 or hi < lo:
                raise QuizValidationError(f"{where}: invalid outcome range")
            covered.extend(range(lo, hi + 1))
            for field in ("title", "summary"):
                _require_local(outcome.get(field), f"{where}: outcome.{field}")
        if sorted(covered) != list(range(maximum + 1)):
            raise QuizValidationError(f"{where}: outcome ranges must cover 0-{maximum} exactly")
    else:
        if not isinstance(outcomes, dict) or set(outcomes) != dim_ids:
            raise QuizValidationError(f"{where}: profile outcomes must match dimensions")
        for outcome in outcomes.values():
            for field in ("title", "summary", "strength", "watch", "action"):
                _require_local(outcome.get(field), f"{where}: profile outcome.{field}")

    sources = raw.get("sources")
    if not isinstance(sources, list) or len(sources) < 2:
        raise QuizValidationError(f"{where}: at least two sources are required")
    urls = []
    for source in sources:
        if not isinstance(source, dict) or not str(source.get("name") or "").strip():
            raise QuizValidationError(f"{where}: malformed source")
        if not _https(source.get("url")):
            raise QuizValidationError(f"{where}: every source needs a direct HTTPS URL")
        urls.append(str(source["url"]))
    if len(set(urls)) != len(urls):
        raise QuizValidationError(f"{where}: source URLs must be unique")
    if raw.get("diagnostic") is not False:
        raise QuizValidationError(f"{where}: diagnostic must explicitly be false")
    return raw


def load_all(today: str | None = None) -> list[dict]:
    """Return valid quizzes newest first; future-dated files stay unpublished."""
    cutoff = today or dt.date.today().isoformat()
    if not QUIZ_DIR.exists():
        return []
    quizzes = []
    for path in sorted(QUIZ_DIR.glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise QuizValidationError(f"{path.name}: invalid JSON") from exc
        if not isinstance(raw, dict):
            raise QuizValidationError(f"{path.name}: root must be an object")
        quiz = _validate(raw, path)
        if quiz["date"] <= cutoff:
            quizzes.append(quiz)
    quizzes.sort(key=lambda item: (item["date"], item["slug"]), reverse=True)
    return quizzes


def _local_question(question: dict, lang: str, mode: str) -> dict:
    result = {
        "id": question["id"],
        "text": _local(question["text"], lang),
        "dimension": question.get("dimension", ""),
        "options": [],
    }
    if mode == "knowledge":
        result["explanation"] = _local(question["explanation"], lang)
    for option in question["options"]:
        row = {"label": _local(option["label"], lang)}
        for key in ("score", "scores", "correct"):
            if key in option:
                row[key] = option[key]
        result["options"].append(row)
    return result


def view(raw: dict, lang: str, base: str = "") -> dict:
    """Localise a validated quiz and return only data needed by templates/JS."""
    mode = raw["mode"]
    dimensions = [
        {
            "id": dim["id"], "label": _local(dim["label"], lang),
            "why": _local(dim["why"], lang), "action": _local(dim["action"], lang),
        }
        for dim in raw.get("dimensions", [])
    ]
    if mode == "profile":
        outcomes = {
            key: {field: _local(value[field], lang)
                  for field in ("title", "summary", "strength", "watch", "action")}
            for key, value in raw["outcomes"].items()
        }
    else:
        outcomes = [
            {
                "min": item["min"], "max": item["max"],
                "title": _local(item["title"], lang),
                "summary": _local(item["summary"], lang),
            }
            for item in raw["outcomes"]
        ]
    questions = [_local_question(q, lang, mode) for q in raw["questions"]]
    copy = raw["copy"]
    return {
        "slug": raw["slug"], "date": raw["date"], "category": raw["category"],
        "mode": mode, "estimated_minutes": raw["estimated_minutes"],
        "title": _local(copy["title"], lang), "dek": _local(copy["dek"], lang),
        "intro": _local(copy["intro"], lang),
        "disclaimer": _local(copy["disclaimer"], lang),
        "questions": questions, "dimensions": dimensions, "outcomes": outcomes,
        "sources": raw["sources"],
        "url": f"{base}/{lang}/quizzes/{raw['slug']}/",
        "payload": {
            "slug": raw["slug"], "mode": mode, "category": raw["category"],
            "questions": questions, "dimensions": dimensions, "outcomes": outcomes,
        },
    }
