# INTRADAY DESK — THE NEWSROOM TABLE

This is the durable contract for My Paper's scheduled intraday commentary.
It supplements the morning edition; it never competes with it for edition slots.
Read `VOICE.md`, `FORMAT.md`, `SCHEDULED-NEWSROOM.md` and the editorial code in
full before acting.

## Purpose

During the day, watch for the rare development that materially changes how an
important story should be understood. Publish at most one new analysis per run
and no more than three per Europe/Prague date. Most runs should create nothing.
A quiet day is not a system failure.

This is not a breaking-news rewrite service. The live feed already tells readers
what happened. The intraday desk earns a new article only when it can explain:

- what genuinely changed since the morning edition;
- why the change matters beyond the headline;
- the mechanism connecting it to people's lives, money, safety, work or future;
- the strongest credible challenge to the leading interpretation;
- the next observable signal that would strengthen or weaken the conclusion.

## Significance gate

Create an analysis only when every condition is met:

1. The development is new since the last My Paper editorial pass.
2. It has a plausible material effect on a large population or reveals a durable
   lesson about power, technology, health, science, business, safety or society.
3. At least two genuinely independent sources confirm the central event, and a
   primary record is open when one exists.
4. At least four direct HTTPS sources can support a 900–1,400 word analysis.
5. The desk has an original explanatory angle, not merely a stronger adjective.
6. No My Paper article from the previous 14 days already answers the same reader
   question.

Celebrity chatter, routine political theatre, isolated viral posts, rumours,
minor price moves and outrage without a measurable consequence do not pass.
If the gate fails, create no file and report `NO MATERIAL CHANGE`.

## Format: The Newsroom Table / U redakčního stolu

The piece is a moderated conversation among three transparent AI editorial
roles. They are not real people and must never claim personal experience.

- **KAI · Moderator** keeps the pace, asks the question a thoughtful reader
  would ask next, translates jargon and stops either analyst from overstating.
- **MIRA · Evidence analyst** establishes what is verified, how strong the data
  are, what mechanism is visible and which numbers actually matter.
- **ORIN · Risk analyst** pressure-tests the leading story, names blind spots,
  second-order effects and the observable condition under which the conclusion
  would be wrong.

All three follow `VOICE.md`: the conversation should sound like experienced
editors at one table, not chatbots congratulating one another. No repeated
“Exactly!”, canned greetings, theatrical disagreement or fake personality.
Disagreement must arise from evidence, assumptions, timescale or risk—not from
roles being forced to take opposite sides.

Within `## PERSPECTIVES`, use this exact sequence:

### The newsroom conversation

> **KAI · Moderator:** A short opening question grounded in the new development.

> **MIRA · Evidence analyst:** What is verified and why it matters.

> **ORIN · Risk analyst:** The pressure-test, missing evidence or alternative.

Continue for a maximum of two rounds each. Every turn must add new information.
Finish the layer with:

### Where they agree

Two to four sentences stating the common ground and the live uncertainty.

The rest of the article still follows the full Wider Lens structure. Dialogue
does not replace FACTS, EVIDENCE, CONTEXT or DEEPER.

## Reader outcome

End with a clearly signposted, evidence-backed takeaway:

- **What changed** — one sentence;
- **Why it matters** — one or two sentences;
- **What to watch, not what to do** — one measurable signal and an approximate
  time horizon;
- **What would change our minds** — the missing evidence or threshold.

Never tell readers to trade, stockpile, change medication, travel, evacuate or
take legal action from commentary alone. When official guidance supports a
specific safety action, attribute it, link it and define where and until when it
applies.

## File contract

Create one new English Markdown file only when the significance gate passes:

`content/inbox/YYYY-MM-DD-intraday-HHMM-slug.md`

Required front matter:

```yaml
lang: en
date: YYYY-MM-DD
status: draft
type: analysis
format: roundtable
series: "The Newsroom Table"
automation_generated: true
automation_role: intraday
edition_slot: 0
event_id: "stable-source-backed-event-id"
generator: "chatgpt-work" # or "claude-cowork"
```

Include at least four unique direct HTTPS sources with publication dates, all
required Wider Lens layers, a practical `impact` block and an evidence-backed
three-option understanding quiz.

Do not overwrite an article, modify the morning agenda, occupy slots 1–7, create
an image, edit configuration, merge a branch or publish directly. GitHub Actions
is the only publication gate. Re-read `main` immediately before writing. If the
same `event_id` or materially equivalent angle already exists, create nothing.
