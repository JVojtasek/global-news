# SCHEDULED NEWSROOM — CHATGPT WORK, NO API KEY

This file is the durable contract for My Paper's scheduled editorial tasks.
The task uses ChatGPT Work, web search and the connected GitHub plugin. It
must not call a paid model API and must never place a secret in the repository.

## The daily hand-off

1. The separate topic-scout task reads `engine/prompts/TOPIC-SCOUT.md`,
   `data/edition-plan.json`, `data/brief.json`, this file and English articles
   from the previous 14 days.
2. It ranks live search demand against usefulness, durability, evidence and
   originality, then creates `data/daily-agenda/YYYY-MM-DD.md` with one distinct
   assignment for each of the seven slots. Raw popularity alone is not enough;
   the agenda preserves the observed demand figures and the scoring rationale.
3. Each writer task reads the agenda and writes exactly its assigned slot as
   one new Markdown file in `content/inbox/`. It never edits or overwrites an
   existing article. If the agenda is unavailable, it may research a fitting
   topic itself, but it must still obey the section and role in
   `data/edition-plan.json`.
4. GitHub Actions later runs the deterministic inbox checks. Only a file that
   passes them can move into published content and trigger the website build.

## Six public roles

- `flagship`: the day's most consequential subject; mechanism, consequences,
  uncertainty and what to watch. It is not a recap.
- `evidence`: test a popular claim or assumption against the best available
  evidence. State what would change the conclusion.
- `practical`: explain a durable problem and give readers a safe, concrete
  checklist they can use or verify. No medical, legal or financial instruction.
- `memory`: use `data/memory/analyst-brief.md` or a documented timeline to show
  what changed, what did not and which earlier expectations failed.
- `evergreen`: answer a recurring search question with lasting educational
  value. The direct answer belongs in the first paragraph.
- `human`: begin with a concrete person, place or decision and use it to explain
  a larger system. Never invent a composite person or emotional detail.

Slot 7 is a `feature` placed in reserve. It must be as carefully researched as
a public article; reserve never means filler.

## Research before prose

- Search in English for an English-speaking audience, with the United States,
  United Kingdom, Canada, Australia and other globally relevant regions in mind.
- Use at least four independent, high-quality sources for `daily` articles and
  at least three for `analysis` or `feature` articles.
- At least one source should be primary whenever a primary record exists.
- Open every source. Record its direct HTTPS URL and publication date in front
  matter. Do not cite a search page, home page or fabricated URL.
- Distinguish independent confirmation from several outlets repeating the same
  press release. State material disagreements and unknowns.
- Never copy source wording beyond a short necessary quotation. Facts may be
  combined; expression and structure must be original.
- Reject the assignment if the central claim cannot be verified. A missed slot
  is better than invented evidence.
- Do not silently replace a demand-backed agenda assignment with an easier
  subject. If its evidence fails, use the next eligible candidate for the same
  slot and record why the original assignment was rejected.

## Article contract

Read `engine/prompts/FORMAT.md` in full and follow it. In addition:

- `lang: en`, `automation_generated: true`, and the assigned `edition_slot`.
- Public slots use `status: draft`; slot 7 uses `status: reserve`.
- Public slots are `daily` or `analysis`; both include `BRIEFLY`, `FACTS`,
  `EVIDENCE`, `PERSPECTIVES`, `CONTEXT`, `DEEPER` and, where useful, `PEOPLE`
  and `REFLECT`.
- Answer the reader's main question early. Explain the mechanism, not only the
  event. Include at least one practical thing to check, compare or watch.
- Add one three-option `quiz` whose answer is explicitly supported by the
  article. It is educational, not a trick and not a personality test.
- Add `tickers` or an existing relative `qma_path` only when QMA genuinely lets
  the reader inspect the article's market consequence. Never use “buy”, “sell”,
  “entry”, “target”, “signal” or promised-return language.
- Do not create an image. The build obtains only licensed imagery or uses a
  typographic cover.

## Final self-audit before writing to GitHub

Verify all six points. If any fails, revise or create no file:

1. Every material number, name and date is supported by a listed source.
2. Facts, interpretation and uncertainty are visibly separated.
3. The article does not duplicate a topic from the previous 14 days.
4. The word count fits the assigned range and no paragraph is a wall of text.
5. The quiz answer is present in the article and its index is 0, 1 or 2.
6. The target path is a new `content/inbox/YYYY-MM-DD-slot-N-slug.md` file.

The scheduled task writes only the new article or daily agenda requested by its
role. It does not merge branches, change workflows, edit configuration, delete
files or bypass the inbox checks.
