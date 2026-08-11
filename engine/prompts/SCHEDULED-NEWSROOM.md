# SCHEDULED EVERGREEN NEWSROOM — CHATGPT WORK, NO API KEY

This is the durable contract for My Paper's scheduled ChatGPT Work tasks. They
may use web search and the connected GitHub tool, but they must not call a paid
model API or put a secret in the repository.

## Daily hand-off

1. The scout reads `engine/prompts/EVERGREEN-VALUE-SCOUT.md`, builds one scored
   agenda and writes it to `data/daily-agenda/YYYY-MM-DD.md`.
2. Six independent tasks read that agenda and their exact slot from
   `data/edition-plan.json`. Slots 1–4 write new complete articles to
   `content/inbox/`. Slots 5–6 write full replacement proposals to
   `content/refresh-inbox/`. Slot 7 writes a reserve article only when assigned.
3. Deterministic repository checks validate format, evidence, value metadata,
   duplicate paths, safety and refresh identity. A failed task never weakens the
   gate and never causes another task to invent filler.
4. GitHub Actions publishes accepted new pages, safely applies eligible
   refreshes without changing their URLs, runs the complete test suite and then
   rebuilds the website.

## Research before prose

- Write for an English-speaking international audience. Search US, UK, Canada
  and Australia, while using globally authoritative evidence.
- Open every source. Use direct HTTPS URLs and accurate publication dates.
- Prefer primary records, official guidelines, systematic reviews and large or
  well-designed peer-reviewed studies. Use at least five sources for a daily
  cornerstone, four for an analysis or feature, and three for a demand page.
- Distinguish independent evidence from several outlets repeating the same
  release. Explain study design, population and limits when they affect the
  conclusion. Never turn association into causation.
- Forums and search questions show what readers need; they do not prove facts.
- Reject the assignment if the central claim cannot be supported or the topic
  requires diagnosis, treatment, legal or financial advice.
- Use original structure and language. Facts may be combined; source wording
  may not be copied beyond a short necessary quotation.

## New article contract — slots 1 to 4 and reserve

Read `engine/prompts/FORMAT.md` in full. Set:

- `lang: en`, `automation_generated: true`, the assigned `edition_slot`;
- `value_article: true`, assigned `pillar` and `cluster`;
- specific `search_intent`, named `practical_asset` and
  `evergreen_target_years` of at least 3;
- `reviewed_at` as today's date and `review_due` six or twelve months later;
- `status: draft` for slots 1–4 and `status: reserve` for slot 7.

Every new article must answer its question early, explain a mechanism, separate
facts/evidence/perspectives/uncertainty, include a concrete safe tool, state who
the advice may not fit, and finish with an educational three-option quiz. A
self-assessment may promote reflection but may never diagnose or claim clinical
validation. Do not create an image; the build uses licensed images or none.

## Refresh contract — slots 5 and 6

Write the complete replacement article, not a patch, to
`content/refresh-inbox/YYYY-MM-DD-slot-N-slug.md`. Copy the target's `slug`,
`lang`, original `date` and `section` exactly. Preserve all valid attribution and
sources, then add the new evidence. Add:

```yaml
refresh_target: content/en/YYYY-MM-DD-existing-slug.md
refresh_reason: "A concrete description of the new evidence, correction or substantial improvement"
updated_at: YYYY-MM-DD
reviewed_at: YYYY-MM-DD
review_due: YYYY-MM-DD
```

Never refresh syndicated or externally canonical content. Never change the URL,
original publication date, language or section. Do not submit a cosmetic edit:
the proposal must add a new quality source or document a material correction,
must not shrink the article by more than ten per cent, and must still pass the
entire new-article contract. Sensitive proposals wait for a person.

## Final self-audit

Before writing anything to GitHub verify:

1. The assignment scored at least 80 and is not a 180-day duplicate.
2. Every material number, name and date is supported by a listed opened source.
3. The direct answer, mechanism, evidence, limits and uncertainty are distinct.
4. The practical asset can be used safely and is not medical, legal or financial advice.
5. The word range, metadata, article layers and quiz all pass `FORMAT.md`.
6. A new article uses a new inbox path; a refresh uses an exact existing target.

The task writes only its requested agenda, article or refresh proposal. It does
not merge branches, change workflows, edit configuration, delete files or
bypass checks.
