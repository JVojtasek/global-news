---
slug: why-ai-still-makes-things-up
title: Why AI Still Makes Things Up — And the One Habit That Catches It
dek: Chatbots don't lie the way people lie. They predict plausible text, and a confident,
  fabricated case citation is just as 'plausible' to the model as a real one.
section: ai
type: analysis
depth: open
lang: en
date: '2026-08-16'
status: published
confidence: 94
load: 0
topics: []
automation_generated: true
edition_slot: 4
automation_role: edition
generator: claude-code
format: ''
event_id: ''
series: ''
image_query: computer screen glitching text
sources:
- name: Wikipedia — Mata v. Avianca, Inc.
  url: https://en.wikipedia.org/wiki/Mata_v._Avianca,_Inc.
  published: ''
- name: Wikipedia — Hallucination (artificial intelligence)
  url: https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)
  published: ''
- name: Wikipedia — Large language model
  url: https://en.wikipedia.org/wiki/Large_language_model
  published: ''
- name: 'Lin, Hilton, Evans — TruthfulQA: Measuring How Models Mimic Human Falsehoods'
  url: https://arxiv.org/abs/2109.07958
  published: '2021-09-08'
impact:
  areas:
  - life
  - money
  line: 'Anyone who uses a chatbot for research, writing or legal or medical questions
    is exposed to this: fabricated citations, dates, and quotes that read as confidently
    as true ones.'
  todo: Before you rely on any specific name, number, date or quote an AI gives you,
    search for it independently — the model itself cannot reliably tell you which
    of its own claims are real.
quiz:
  question: According to this article, why do language models produce confident false
    statements instead of saying 'I don't know'?
  options:
  - They are deliberately programmed to deceive users
  - They predict plausible-sounding text and rarely saw honest uncertainty rewarded
    in training
  - They run out of processing power partway through an answer
  answer: 1
  explanation: The mechanism is statistical prediction of likely text, shaped by training
    and feedback that tends to favor fluent, confident answers over hedged or uncertain
    ones.
---

## BRIEFLY

**What happened.** AI chatbots continue to generate fabricated facts, citations and quotes with the same fluent confidence as accurate ones — a well-documented failure mode researchers call "hallucination."

**What it means.** This isn't a bug that gets fixed by a software update. It comes from how these systems work: predicting likely next words, not checking claims against reality.

**Risks and impact.** Anyone using AI for research, writing, legal filings or health questions can be handed a wrong fact dressed exactly like a right one — with no built-in warning sign.

**What can be done.** Treat any specific name, number, date, quote or citation from an AI assistant as a lead to verify, not a fact to use. Ask the model to show its sources, then check the sources exist.

**What to watch.** Whether "grounding" techniques — forcing a model to quote from retrieved real documents rather than its memory — keep closing the gap, or whether the problem proves harder to fully engineer away.

## FACTS

In the case Mata v. Avianca, a New York lawyer, Steven Schwartz, submitted a legal brief that cited past court rulings to support his argument. Several of those rulings did not exist. He had asked ChatGPT for supporting cases, the tool generated citations that looked exactly like real case law, complete with names and docket numbers, and he filed them without checking. A federal judge sanctioned him in 2023. It became one of the first widely reported, documented cases of what researchers call AI "hallucination" causing real-world consequences.

Hallucination, in this technical sense, means an AI system generating content that is fluent, confident and false. It is not the system "lying," because lying requires knowing the truth and choosing to hide it. A language model has no internal fact-checker running underneath its answers. It is a statistical system trained to predict which word plausibly comes next, given everything it has seen before, including in its own training data.

That mechanism explains why hallucinations so often look like real facts rather than nonsense: the model isn't randomly guessing, it's producing the most statistically plausible-sounding continuation, and a fabricated but well-formed citation is, to that process, just as "plausible" as a real one. Nothing in the basic architecture distinguishes "this is true" from "this is the kind of sentence that appears after this kind of question."

## EVIDENCE

Researchers agree, across a large body of published work, that hallucination is a structural property of how large language models generate text, not an occasional glitch specific to one company's product. That's well established and not seriously disputed in the field.

What's less settled is how much any given technique reduces it. Retrieval-based methods — where a model is required to quote from documents fetched at the moment of the question, rather than relying purely on what it absorbed during training — measurably reduce fabrication rates in benchmark testing. They do not eliminate the problem, because a model can still misread or misquote the real document it was given.

The 2021 TruthfulQA benchmark, built specifically to probe this, found that models could produce confidently wrong answers on questions where a plausible-sounding but false answer was common in text the model had likely trained on — imitating widespread human misconceptions rather than correcting them. That's a narrower and more specific finding than "AI is unreliable" — it shows the failure tracks what's common in training text, not random error.

What we don't have is a reliable way for a model to know, from the inside, which of its own outputs are hallucinated. Confidence expressed in the tone of an answer does not reliably track accuracy — a model can sound exactly as certain when it's wrong as when it's right.

## PERSPECTIVES

**The engineering-progress view**: hallucination rates have measurably dropped as retrieval grounding, better training data curation and fact-checking layers have been added, and the trend line points toward continued improvement. This view is well supported by benchmark comparisons over time, but it tends to understate that "lower rate" still means errors happen, and a user has no reliable way to tell, in the moment, which answer is the wrong one.

**The structural-limit view**: because the underlying mechanism is next-word prediction rather than verified retrieval of facts, some baseline rate of fabrication may be close to unavoidable without fundamentally different architectures. This is a more cautious, research-grounded position, but it can understate how useful heavily-grounded, source-citing systems have already become for narrower tasks.

**The user-responsibility view**, common in how companies frame the issue publicly: the tool is a draft generator, and verification is the user's job. This is true as far as it goes, but it places the entire cost of the failure mode on the person least equipped to catch it — someone asking a question specifically because they don't already know the answer.

## CONTEXT

The word "hallucination" is itself a metaphor borrowed from human psychology, and it's an imperfect one. A person who hallucinates has a malfunctioning perception of something that does or doesn't exist. A language model has no perception to malfunction — it has a text-prediction process operating exactly as designed, just applied to a case where the most statistically likely continuation happens to be false.

This matters because it changes what a "fix" can even look like. You cannot patch a language model's honesty the way you patch a security flaw, because the model was never checking honesty in the first place. What's actually improved outcomes so far are workarounds: requiring citations to real, retrievable documents; training models specifically to say "I don't know" more often in cases of genuine uncertainty; and building separate verification steps outside the model itself.

Attorney Steven Schwartz's case, documented in the court's own sanctions order, is a useful boundary marker rather than an outlier: it was widely reported at the time precisely because it was an early, unusually clean example of the same failure mode researchers had already been describing in benchmarks like TruthfulQA — fluent, specific, false, and unflagged by the tool that produced it. What isn't yet settled is how quickly grounding techniques close the gap for open-ended, general-purpose questions rather than narrow, document-anchored ones.

## DEEPER

There's a specific kind of trust that fluent language earns, almost automatically, regardless of who or what produced it. Humans are built to read confident, well-structured sentences as a signal of reliable knowledge — it's a shortcut that works reasonably well with other humans, because bluffing fluently on a specific fact is harder for us than it looks, and gets caught socially over time.

A language model breaks that shortcut without knowing it's doing so. It can produce a wrong case citation with exactly the same fluency, structure and confident tone as a right one, because fluency is the thing it was actually trained to produce. The accuracy, when it happens, is a byproduct of good training data and grounding — not a separate, checked property of the sentence.

That gap between "sounds right" and "is right" isn't new to AI. It's the same gap that lets a confident amateur out-argue a hesitant expert in a meeting, or that makes a well-written scam letter more convincing than a clumsy true one. What's new is the scale and speed: a tool that can produce that fluent, confident surface on demand, about nearly any topic, in seconds, for free.

The habit that actually catches it isn't a smarter AI model. It's the old, unglamorous one: treating fluency and accuracy as two different things that happen to travel together most of the time, and checking the second one anyway.

## REFLECT

When something sounds confident and well-organized, how much of your trust in it comes from the content, and how much from the delivery?

If a tool could tell you exactly how sure it was about each specific claim, would you actually stop to check the low-confidence ones — or would fluent phrasing win anyway?
