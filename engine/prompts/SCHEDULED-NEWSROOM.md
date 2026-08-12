# SCHEDULED NEWSROOM — CHATGPT WORK, NO API KEY

This file is the durable contract for My Paper's scheduled editorial tasks.
The task uses ChatGPT Work, web search and the connected GitHub plugin. It
must not call a paid model API and must never place a secret in the repository.

## The daily hand-off

1. The research-desk task reads `data/edition-plan.json`, `data/brief.json`,
   this file and English articles from the previous 14 days.
2. It searches the web and creates `data/daily-agenda/YYYY-MM-DD.md` with one
   distinct topic for each of the seven slots. Every topic gets a reader question,
   a precise angle, what would make the article useful in six months, and at
   least four candidate sources. Prefer primary documents, official statistics,
   regulators, research papers and direct company filings. A search result
   snippet is not a source. The same agenda ends with `## Briefing watch calendar`
   and one fenced `json` array containing three to six consequential, time-bound
   events expected on that Europe/Prague date. This is a calendar, not another
   list of possible article topics. Open the source for every event and include:
   `starts_at` (ISO 8601 with offset), `all_day` (boolean), `title_en`, `title_cs`,
   `why_en`, `why_cs`, `publisher`, `source_url` (direct HTTPS), `source_date`,
   `section_id`, `section_en`, `section_cs`, `countries` (two-letter codes) and
   `scope` (`none`, `eu` or `global`). Prefer official calendars, regulators,
   statistical agencies, courts, legislatures and event organisers. Do not list
   rumours, merely possible developments, recurring observances or an event whose
   date cannot be verified. An empty array is better than an invented appointment.
   After the calendar, add two more fenced JSON arrays:

   - `## Briefing country notes`: three to eight current notes for the priority
     countries surfaced by today's research, including the operator's home edition
     (`cz`) when reliable sources support it. Each row needs `title_en`, `title_cs`,
     `why_en`, `why_cs`, `publisher`, direct HTTPS `source_url`, `valid_until`,
     `section_id`, `section_en`, `section_cs`, `countries` and `scope`. This is not
     permission to invent local relevance: use an official national source or a
     feed genuinely dedicated to that country. Leave a country absent rather than
     fill it from a search snippet.
   - `## Briefing practical decisions`: zero to six source-backed decision cards.
     Every row needs `level` (`know`, `watch`, `prepare` or `act`), bilingual
     `title`, `why`, `action` and `trigger`, plus `publisher`, direct HTTPS
     `source_url`, boolean `official`, `valid_until`, `countries` and `scope`.
     `watch` must name a measurable trigger. `prepare` and `act` require an
     official source and expiry; `act` also requires a concrete country. A headline
     alone never justifies stockpiling, a financial trade, a medication change or
     evacuation. If no action is justified, say so with a `know` card or leave the
     array empty. Do not manufacture urgency.
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

Standalone daily quizzes are a separate scheduled role. They follow
`engine/prompts/QUIZ-FORMAT.md` and `data/quiz-plan.json`; article writers keep
using only the three-option understanding check defined above.
