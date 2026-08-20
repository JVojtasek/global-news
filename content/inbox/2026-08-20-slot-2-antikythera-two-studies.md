---
lang: en
date: '2026-08-20'
status: draft
automation_generated: true
automation_role: edition
generator: claude-cowork
edition_slot: 2
type: analysis
section: mysteries
depth: open
slug: antikythera-two-measurements
title: One Team Says the Antikythera Mechanism Was More Precise Than We Thought. Another
  Says It Would Have Jammed.
dek: Both were measuring the same corroded bronze. The disagreement is not really about
  the machine — it is about what two thousand years on a seabed does to a measurement,
  and neither paper says what the headlines said it said.
confidence: 88
load: 0
topics: []
format: ''
event_id: ''
series: ''
image_query: Antikythera mechanism fragment museum
sources:
- name: Graham Woan and Joseph Bayley - An improved calendar ring hole-count for the
    Antikythera mechanism, University of Glasgow (arXiv 2403.00040)
  url: https://arxiv.org/abs/2403.00040
  published: '2024-02-29'
- name: Esteban Szigety and Gustavo F. Arenas - The Impact of Triangular-Toothed Gears
    on the Functionality of the Antikythera Mechanism (arXiv 2504.00327)
  url: https://arxiv.org/abs/2504.00327
  published: '2025-04-01'
- name: University of Glasgow - Gravitational wave researchers cast new light on Antikythera
    mechanism mystery
  url: https://www.gla.ac.uk/news/archiveofnews/2024/june/headline_1086643_en.html
  published: '2024-06-27'
- name: Phys.org - Antikythera Mechanism's intricate gears - simulations of ancient
    astronomical device reveal potential jamming issues
  url: https://phys.org/news/2025-04-antikythera-mechanism-intricate-gears-simulations.html
  published: '2025-04-21'
quiz:
  question: What did Szigety and Arenas conclude from their simulation?
  options:
  - The mechanism was a mechanical disaster that never worked
  - Either it never worked, or the published error measurements are larger than the
    original ones
  - The triangular teeth alone made the mechanism unusable
  answer: 1
  explanation: Their paper states the result as a dilemma and calls the impact of
    the variables speculative. The second branch — that the measured errors do not
    reflect the original build — is the one they themselves flag.
impact:
  areas:
  - life
  line: Two peer-reviewed measurements of the same object point in opposite directions,
    and both research teams say so plainly in their papers. The certainty appeared
    later, in the coverage.
  todo: Open arXiv 2504.00327 and read the abstract. The words "our results must be
    interpreted with caution" are in it. Then compare that with the headlines the
    paper produced.
---

## BRIEFLY

**What happened.** Two research teams have measured the Antikythera mechanism — the geared bronze device recovered from a Roman-era shipwreck — and reached conclusions that pull in opposite directions. One infers a maker more precise than assumed. The other finds that with the published error figures, the gears would jam.

**What it means.** Both teams are measuring corroded fragments, not a working machine. The gap between them is mostly the gap between the object as it is now and the object as it was built.

**Risks and impact.** Nothing practical. What is at stake is how a careful paper becomes a confident headline: one of these studies was reported as proving the device was a failure, which is not what its authors wrote.

**What can be done.** Read the abstracts. Both are open access and both state their own limits in plain language.

**What to watch.** Whether anyone can establish how much of the measured error is manufacture and how much is two thousand years of seawater. Until that is settled, neither result can be final.

## FACTS

In 1901 sponge divers working a wreck off the Greek island of Antikythera brought up a lump of corroded bronze. Inside it were gears. Nothing else like it survives from the ancient world, and nothing of comparable complexity appears in the European record for another thousand years or more.

It has been X-rayed, CT-scanned and modelled for a century. Two recent papers show how much room is still left.

📖 **What the sources say.** In February 2024 Graham Woan and Joseph Bayley of the University of Glasgow — both from the gravitational-wave group, people whose day job is extracting faint signals from noisy data — published a statistical re-analysis of the holes beneath the mechanism's calendar ring. Working from the surviving fragment, they estimated the complete ring held about **355 holes** (355.24, with an uncertainty of roughly 1.4 either way at 68% confidence), or **354** if holes next to the fracture are excluded.

That number matters. A ring of 365 holes would mean a solar year of the Egyptian kind. A ring of about 354 means a **lunar** year — twelve lunar months, the calendar of the Greek city-states. Their analysis disfavours 360 and makes 365 implausible under their model.

In April 2025 Esteban Szigety and Gustavo Arenas took a different approach. They built a computational simulation of the mechanism's behaviour, combining two existing frameworks: an analytical treatment of how triangular gear teeth transmit motion unevenly, and a published model of the manufacturing errors in the surviving gears.

Their result: the triangular teeth on their own produce negligible error. The manufacturing inaccuracies do not. Fed with those figures, the simulated gear trains jam or slip out of engagement.

## EVIDENCE

Here is where the story usually stops and the headline begins. *The famous Antikythera mechanism was a mechanical disaster*, ran one. The trouble is that this is not the conclusion of the paper.

📖 **What the sources say.** Szigety and Arenas frame their finding as a fork, not a verdict: either the mechanism never functioned as intended, **or** its actual errors were smaller than the ones in the published error model they used. They write that the impact of these variables is speculative and that their results must be interpreted with caution. They question in the paper itself whether those error values reflect the mechanism's original state.

That second branch is not a footnote. It is at least as likely as the first, and arguably more so — because of what the object has been through.

The mechanism spent roughly two thousand years in seawater. Bronze there does not sit still: it corrodes and swells, surfaces are lost, material is redeposited. The fragments were then broken, handled, and early on cleaned by methods nobody would use today. Every dimension anyone measures is a dimension of that history, not of the workshop.

So when a simulation says the gears would bind, the honest reading is not *the Greeks built a dud*. It is *the thing we can measure today would bind* — which is close to what you would expect from a corroded object, and tells you less about the maker than it first appears.

## PERSPECTIVES

**The Glasgow reading.** The fragment is damaged but the underlying pattern is regular, and regularity is recoverable from noise. On this view the maker was working to a lunar calendar and the hole spacing is good enough to say so with a stated uncertainty. Strength: it reports a number with an error bar rather than a verdict. Limit: it settles the calendar, not whether the device turned.

**The simulation reading.** Geometry is forgiving; mechanism is not. A gear train either meshes or it does not, and on the published error figures it does not. Strength: it tests the object as a machine rather than as a diagram, which almost nobody had done. Limit: it depends entirely on error values that its own authors doubt.

**The conservative reading, which both papers permit.** The device worked well enough for whoever paid for it, and the errors we measure today are mostly the wreck. This is unglamorous and unpublishable — there is no way to demonstrate it — but it is the reading most consistent with the object having been made, sold, carried onto a ship, and used.

**The reading that is not supported.** That the mechanism has been shown to be a failure. No paper claims this. It appeared in the coverage, not in the research.

## CONTEXT

Set the two papers side by side and the shape becomes clearer.

Woan and Bayley are working on **positions**: where holes sit around a circle. Corrosion shifts and obscures individual holes, but the underlying geometry — a regular ring — is strong enough that statistical inference can recover it. This is exactly the problem their field is built for: pulling a weak regular signal out of a noisy record.

Szigety and Arenas are working on **tolerances**: how far a tooth can be out of place before a gear train stops turning. Tolerance is unforgiving in a way that geometry is not. A ring of holes that is slightly irregular is still a ring. A gear train whose errors exceed the play available simply stops.

The same corrosion that a statistical method can see past is the corrosion that a mechanical simulation cannot. Neither team is doing anything wrong. They are asking questions with different sensitivity to the same damage.

## PEOPLE

It is worth pausing on who did the calendar work. Woan and Bayley are physicists who normally analyse data from gravitational-wave detectors, instruments listening for changes in length far smaller than an atomic nucleus. The University of Glasgow's own announcement described the transfer of technique plainly: methods developed to detect ripples in spacetime, turned on a hole-pattern in ancient bronze.

That matters because the problem was never a shortage of interest in the mechanism. It was that the fragment holds no complete circle of holes, so the total has to be inferred — and inference from partial, damaged evidence is a specialism.

## DEEPER

What can be said with reasonable confidence today:

- The device tracked astronomical cycles with gearing of a sophistication that has no surviving parallel for centuries afterwards.
- The calendar ring most likely carried around 354 or 355 holes, pointing to a lunar calendar rather than a 365-day one.
- The gears as they survive, measured as they survive, contain errors large enough that a simulation of them fails.

What cannot:

- Whether those errors were there when it was made.
- Therefore whether it ran smoothly, ran roughly, or ran at all.

There is no obvious way to settle that last question with the material that exists. Somebody would have to separate original manufacturing error from two millennia of accumulated damage in an object that cannot be dismantled and has no twin.

## REFLECT

The interesting thing here is not the machine. It is the distance between two open-access abstracts and the stories written from them.

Both papers are careful. One reports a number with an uncertainty attached. The other states a dilemma and tells the reader, in its own abstract, to interpret with caution. Neither claims to have settled anything.

What travelled was a verdict — *ancient computer was a failure* — assembled by removing the second half of a sentence.

This is the ordinary way scientific caution gets lost. It requires nobody to lie — only that the hedge is less quotable than the claim. Which it always is.

The useful habit is small and cheap: when a study is reported as proving something surprising, open the abstract. It is usually a paragraph, it is usually free, and the qualifier that decides the meaning is usually still in it.
