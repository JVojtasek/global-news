# DAILY QUIZ CONTRACT — CHATGPT WORK, NO PAID API

Read `engine/prompts/VOICE.md` in full. The quiz should feel like an
intelligent, friendly conversation with an experienced editor—not an entrance
exam, diagnosis, marketing funnel or machine-generated form.

Create exactly one new bilingual daily quiz for My Paper. Read this file,
`data/quiz-plan.json`, every file in `data/quizzes/` from the previous 30 days
and the current site before choosing a subject. Use web research and open every
source. A search snippet is not evidence.

## Reader promise

The quiz must help a reader understand a pattern, test useful knowledge or find
one practical next step. It may be enjoyable, but the result cannot be an empty
compliment, a fixed identity, an IQ claim or a clinical diagnosis. Never use fear,
shame, superiority, a forced email gate or a promise to predict the future.

Follow today's category and mode in `data/quiz-plan.json`. Within that boundary,
prefer a question with visible reader demand. Compare current quiz catalogues and
recent popular lists from established publishers, then choose an original angle
that My Paper can support with better evidence and a more useful result. Do not
copy a competitor's wording, items, scoring, character types or result text.

## Evidence and licences

- Open and cite at least two direct HTTPS sources. Prefer public agencies,
  peer-reviewed papers, professional bodies and the original authors of a scale.
- Use a named validated instrument only when its item and scoring licences permit
  this exact public use. Otherwise write an original educational self-check and
  say so in both disclaimers.
- Psychological, relationship and resilience quizzes are reflective, not
  diagnostic. Health quizzes test literacy or knowledge, not symptoms or disease.
- Financial quizzes may cover habits, fraud awareness or concepts. They never
  produce a trade, product recommendation, credit decision or promised outcome.
- Every result must name a limitation and a safe, realistic next step.

## File contract

Write one new UTF-8 JSON file directly on `main`:

`data/quizzes/YYYY-MM-DD-short-english-slug.json`

Never overwrite a file, create a branch or pull request, edit code or configuration,
or write any executable HTML or JavaScript. GitHub Actions is the only publication
gate. If evidence, licensing or bilingual accuracy is inadequate, create no file.

The root object uses `schema_version: 1`, `diagnostic: false`, a unique kebab-case
`slug`, Europe/Prague `date`, one allowed `category`, `mode`, and an integer
`estimated_minutes` from 2 to 10. It contains:

- bilingual `copy.title`, `copy.dek`, `copy.intro`, `copy.disclaimer`;
- 3–7 `dimensions` for assessment/profile quizzes, each with `id` and bilingual
  `label`, `why`, `action`;
- 6–20 `questions`, unique `id`, bilingual `text`, and 3–5 bilingual options;
- `outcomes` that cover every possible score, or one profile outcome for every
  dimension;
- at least two unique direct-HTTPS `sources` with `name`, `url`, honest
  `published` (empty when unknown), and `type`.

### Mode: assessment

Each question has one valid `dimension`. Each option has integer `score` 0–3.
`outcomes` is a list of non-overlapping `{min,max,title:{en,cs},summary:{en,cs}}`
objects that covers every integer from zero through the maximum possible score.
A high score must not claim moral, clinical or intellectual superiority.

### Mode: profile

Each option has a `scores` object whose keys are declared dimension IDs and whose
values are integers 0–3. `outcomes` is an object keyed by every dimension ID. Each
outcome contains bilingual `title`, `summary`, `strength`, `watch` and `action`.
Profiles describe a current tendency, never a permanent type.

### Mode: knowledge

Dimensions may be empty. Exactly one option per question has `correct: true`; the
others have `correct: false`. Every question has a bilingual `explanation`.
`outcomes` covers every possible correct-answer score. Never describe a trivia
score as IQ or intelligence.

Before writing, calculate every score path, confirm outcome coverage, check both
languages for meaning rather than literal translation, verify source URLs, and
confirm the subject does not duplicate the previous 30 days.
