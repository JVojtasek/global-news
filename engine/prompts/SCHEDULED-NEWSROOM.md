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
   snippet is not a source.
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
- Only slot 1 creates an original hero image. Follow the image contract below.
  All other slots leave image selection to the build.

## Editorial hero image — slot 1 only

After the article itself passes the editorial self-audit, slot 1 invokes
`$imagegen` exactly once and creates one original landscape hero image.

- Use a 16:9 editorial composition, at least 1200 × 630 pixels, with no headline,
  logo, watermark, brand, readable interface or decorative text in the image.
- Base the visual on the article's central idea, not merely its section.
- Never fabricate apparent photographic evidence. For politics, war, disasters,
  crime, public figures, real people, real places or a current event, use a
  clearly conceptual illustration rather than a photorealistic reconstruction.
- Inspect the result for distorted faces or hands, false symbols, garbled text
  and details that contradict the article. Reject a misleading image.
- Convert the approved result to JPEG and store it as
  `static/covers/<article-slug>.jpg`.
- Store `static/covers/<article-slug>.json` beside it with exactly this shape:
  `{"text":"AI-generated editorial illustration · OpenAI ChatGPT","url":"https://openai.com/index/chatgpt/","provider":"OpenAI","synthetic":true}`
- Commit the Markdown article, JPEG cover and JSON disclosure atomically. Upload
  the JPEG as a base64 Git blob, then create one tree and one commit containing
  all three files. Never commit an orphaned cover or an article that refers to a
  missing generated image.
- If image generation is unavailable, reaches a usage limit or fails inspection,
  publish the article without a generated cover. The existing licensed-image and
  typographic-cover pipeline remains the safe fallback.

## Final self-audit before writing to GitHub

Verify all seven points. If any fails, revise or create no file:

1. Every material number, name and date is supported by a listed source.
2. Facts, interpretation and uncertainty are visibly separated.
3. The article does not duplicate a topic from the previous 14 days.
4. The word count fits the assigned range and no paragraph is a wall of text.
5. The quiz answer is present in the article and its index is 0, 1 or 2.
6. The target path is a new `content/inbox/YYYY-MM-DD-slot-N-slug.md` file.
7. For slot 1, the cover is either disclosed and safe under the image contract,
   or omitted so the deterministic fallback can run.

The scheduled task writes only the requested daily agenda, or the new article
and its slot-1 cover companions. It does not merge branches, change workflows,
edit configuration, delete files or bypass the inbox checks.
