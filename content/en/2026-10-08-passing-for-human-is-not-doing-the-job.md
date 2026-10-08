---
slug: passing-for-human-is-not-doing-the-job
title: Passing for Human Is Not the Same as Doing the Job
dek: AI now wins tests that once looked like the finish line. Here is what those wins
  measure, what they leave out, and why that gap matters for anyone asking about jobs.
section: tech
type: analysis
depth: open
lang: en
date: '2026-10-08'
status: published
confidence: 88
load: 0
topics: []
automation_generated: true
edition_slot: 2
automation_role: edition
generator: claude-code
format: wider-lens
event_id: ''
series: ''
image_query: empty exam desk office chair
sources:
- name: Wikipedia — Artificial general intelligence
  url: https://en.wikipedia.org/wiki/Artificial_general_intelligence
  published: '2026-10-08'
- name: Wikipedia — Artificial intelligence in healthcare
  url: https://en.wikipedia.org/wiki/Artificial_intelligence_in_healthcare
  published: '2026-10-08'
- name: Wikipedia — Hallucination (artificial intelligence)
  url: https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)
  published: '2026-10-08'
qma_path: ''
tickers: []
impact:
  areas:
  - life
  - money
  line: 'Nothing here measures how many jobs AI has taken or created. What changes
    is how to read the next claim that a machine ''beats'' doctors, writers or analysts:
    a preferred answer is not yet a checked one.'
  todo: 'When a headline says AI outperformed professionals, look for three things:
    who did the judging, whether accuracy was graded, and who checks the output when
    it is wrong.'
quiz:
  question: In the 2023 study of medical questions from an online forum, what were
    ChatGPT's answers NOT graded on?
  options:
  - The accuracy of the medical information
  - Quality
  - Empathy
  answer: 0
  explanation: Evaluators preferred ChatGPT's answers in 78.6% of 585 evaluations
    for quality and empathy, but the responses were not graded on whether the medical
    information was accurate.
---

## BRIEFLY

**What happened.** Language models now pass tests that were long treated as milestones, including a 2025 Turing-test study in which GPT-4.5 was judged human in 73% of short text conversations.

**What it means.** Most of these tests reward answers that people like or find convincing. A job also requires answers that are right, in context, when nobody is grading.

**Risks and impact.** Confident errors, usually called hallucinations, remain a known obstacle to using these systems where mistakes are costly, such as medical diagnostics, chip design and supply-chain logistics.

**What can be done.** When a claim says AI beat professionals, check who judged it, whether accuracy was measured, and whether the comparison happened in a real working setting.

**What to watch.** Studies that grade AI output for correctness inside real workplaces, against people doing the same task, rather than preference ratings on isolated questions.

## FACTS

In 1965 the AI pioneer Herbert A. Simon wrote that "machines will be capable, within twenty years, of doing any work a man can do". That deadline came and went in 1985. In 1967 Marvin Minsky had been just as bold: "Within a generation... the problem of creating 'artificial intelligence' will substantially be solved".

Sixty years on, the tests look very different. A pre-registered 2025 study by Cameron R. Jones and Benjamin K. Bergen ran a three-party version of Alan Turing's 1950 test. GPT-4.5 was judged to be the human in 73% of five-minute text conversations. Real human participants scored 67%. By the researchers' own criterion, the machine passed.

Medicine has its own version. A 2023 study took medical questions posted on Reddit's r/AskDocs forum. Evaluators preferred ChatGPT's answers to doctors' answers in 78.6% of 585 evaluations, citing quality and empathy. A 2025 systematic review of 15 studies found that in a large majority of them, participants rated chatbot replies as more empathic than clinicians'.

On paper, the job looks done. The fine print disagrees.

## EVIDENCE

**What the sources agree on.** Language models now produce text that people often prefer, and sometimes cannot tell from a person's.

**What rests on thinner ground.** The 2023 medical study carries its own caveats. The questions were isolated forum posts, not part of a relationship between a patient and a doctor. The answers were not graded on the accuracy of the medical information. Critics also argued the study was not properly blinded, because the evaluators were co-authors. A preference for tone is real data. It is not a measure of safe advice.

**What is documented as a weakness.** A hallucination is a response that contains false or misleading information presented as fact. Meta's warning for BlenderBot 2 in July 2021 put it plainly: "confident statements that are not true". Detecting and reducing these errors is described as a major challenge for deploying language models in high-stakes work such as chip design, supply-chain logistics and medical diagnostics.

**What we do not know.** None of the three sources measures how many jobs AI has removed, changed or created. Anyone who tells you the employment answer from these tests alone is guessing.

## PERSPECTIVES

**"The tests are falling, so the jobs are next."** This view rightly notes how fast the goalposts have moved. In 2023 Google DeepMind researchers proposed five levels of general AI and placed models like ChatGPT at the bottom, "emerging", comparable to unskilled humans. The next level, "competent", means beating half of skilled adults across a wide range of non-physical tasks. What this leaves out: a job is not many tasks done once. It is a few tasks done reliably, for months, with consequences.

**"It just predicts words, so it can't really do anything."** This view has a solid mechanism behind it. Models are trained to predict the next word, which pushes them to guess even when they lack information. The statistician Gary Smith argues they "do not understand what words mean". The blind spot is that useful work does not always need understanding in a human sense. Clinical note-taking tools, for example, are spreading, and early studies suggest they may reduce paperwork, a known driver of burnout.

**"Hallucination is the wrong word."** The computer scientist Mary Shaw calls the term "appalling", because it makes software errors sound like quirks of a mind. This matters for jobs. If errors are framed as charming oddities, nobody budgets for checking them. If they are framed as defects, somebody's job becomes catching them.

The evidence does not split evenly. The caution comes with a documented mechanism. The excitement, so far, comes mostly with preference scores.

## CONTEXT

The tests themselves tell a story. Steve Wozniak proposed a "coffee test": enter an ordinary home, find the machine, the coffee, the water and a mug, and brew a cup. In January 2024 a humanoid robot from Figure AI learned to work a Keurig machine after watching video demonstrations. In 2025, University of Edinburgh researchers described a robotic arm that makes coffee in changing kitchens.

Each test captured something that once felt like the hard part. Each fell. The definition problem has barely moved. In 2007 John McCarthy wrote: "We cannot yet characterize in general what kinds of computational procedures we want to call intelligent."

A useful way to see the gap is to compare a test with a shift at work.

- **A test has a judge. A job has consequences.** In the Turing test, success means being believed. At work, being believed while wrong is the expensive outcome.
- **A test is a snapshot. A job is a record.** Five minutes of conversation says little about the thousandth answer on a busy Thursday.
- **A test compares against a reference. A job compares against a colleague.** Healthcare researchers note that many early studies of medical AI simply did not compare the algorithm with human performance. Where they did, the results were sometimes strong: AI has been found non-inferior to humans at interpreting heart ultrasound scans.

The mechanism behind confident errors is now partly visible. Interpretability research by Anthropic in 2025 reported that its model Claude appears to have internal circuits that, by default, stop it answering unless it knows the answer. Errors appeared when that brake was released wrongly, for example when the model recognised a name but knew too little about the person.

Then there is Galactica. Meta AI released it on 15 November 2022 to "store, combine and reason about scientific knowledge". It cited a fictitious paper attributed to a real researcher. Meta withdrew it on 17 November. Two days is a short career.

## PEOPLE

Imagine a hospital doctor whose day is split between patients and paperwork. A tool that transcribes the consultation and drafts the note may give back time. But someone still has to read that note before it enters the record. The job shifts from writing to checking.

Now imagine someone whose job is mostly drafting replies to customers. Here the preference scores matter more, because tone is a large part of the work. The risk is a confident wrong answer about a refund or a contract term, sent at scale.

Same technology, different exposure: it depends on how costly an error is, and who is paid to catch it.

## DEEPER

Herbert Simon's prediction failed in an instructive way. Machines did get better. What he misjudged was what "any work" includes: knowing when an answer is shaky, noticing that a question is the wrong question, standing behind a decision when it goes badly.

Tests are built from what can be written down. A test can check whether an answer sounds human or kind. It struggles to check whether someone will be accountable for it next week.

Three researchers, Hicks, Humphries and Slater, borrowed a blunt term from the philosopher Harry Frankfurt to describe language-model output. Their argument was that the models are "in an important way indifferent to the truth of their outputs". True statements come out true by accident, and false ones false by accident. You need not accept their word to take the point. A tool can be useful without caring about truth. The caring has to sit somewhere else.

That may be the real jobs question. Not which tasks a machine can perform, but where responsibility for being right will live once it performs them. The tests ask what a machine can do. Work keeps asking who answers for it.

## REFLECT

Which part of your own work would a five-minute test capture, and which part would it miss?

If a tool drafted half your output tomorrow, how would you know which half to check?

One thing to try: take the next "AI beats experts" headline and find out who judged it and whether correctness was measured.
