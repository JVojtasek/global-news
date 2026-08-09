"""Falešné odpovědi AI pro testování zdarma (AI_MOCK=1).

Díky tomu si můžeš celý systém vyzkoušet bez klíče a bez jediného dolaru.
"""
from __future__ import annotations

import json
import random
import re

LOREM = (
    "This is placeholder text produced in offline test mode so the whole pipeline "
    "can be exercised without an API key. It is deliberately long enough to pass the "
    "structural checks that the real editorial system applies to every article, and it "
    "carries no editorial meaning whatsoever. Nothing here should ever be published. "
    "The purpose is to confirm that files are written, parsed, validated, scheduled and "
    "rendered correctly from end to end before a single request is billed. "
)


def _para(n: int = 3) -> str:
    return "\n\n".join(LOREM * 2 for _ in range(n))


def mock_answer(system: str, user: str) -> str:
    s = system.lower()

    if "guardian" in s:
        return json.dumps({"issues": [], "confidence": 88, "verdict": "pass"})

    if "nevěřící čtenář" in s or "sceptic" in s:
        return json.dumps({
            "issues": [], "detected_agenda": False, "would_finish_reading": True,
            "manipulation_score": 12, "credibility_score": 86, "deeper_layer_quality": 82,
            "one_sentence_verdict": "Offline test mode — no real review performed.",
        })

    title = "Test article"
    m = re.search(r"(?:UDÁLOST|TÉMA):\s*(.+)", user)
    if m:
        title = m.group(1).strip()[:90]

    is_feature = "the deeper story pro rubriky" in s or "dlouhých článků" in s
    if "kontrolor faktů" in s:
        return json.dumps({"claims": [], "unsupported_count": 0,
                           "worst": "", "safe_to_publish": True})
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:50] or "test"

    import re as _re
    m2 = _re.search(r"RUBRIKA:\s*(\w+)", user)
    section = m2.group(1) if m2 else ("history" if is_feature else "world")
    m3 = _re.search(r"depth\):\s*(\w+)", user)
    depth = m3.group(1) if m3 else "open"

    head = f"""---
slug: {slug}
title: "{title}"
dek: "Offline test mode: this article was generated without any AI call."
section: {section}
type: {"feature" if is_feature else "news"}
depth: {depth}
image_query: "abstract landscape horizon"
lang: en
status: draft
confidence: 0
sources:
  - name: "Test Source A"
    url: "https://example.com/a"
  - name: "Test Source B"
    url: "https://example.com/b"
---
"""
    marker = ("📖 What the sources say: placeholder. 🏺 What the evidence supports: placeholder. "
              "🎬 Reconstruction (we are imagining): placeholder.\n\n") if is_feature else ""
    return head + f"""
## FACTS

{marker}{_para(2)}

## CONTEXT

{_para(2)}

## PEOPLE

{_para(1)}

## DEEPER

{_para(2)}

## REFLECT

- Placeholder question one for offline testing purposes only?
- Placeholder question two for offline testing purposes only?
- Placeholder question three for offline testing purposes only?

{LOREM}
"""
