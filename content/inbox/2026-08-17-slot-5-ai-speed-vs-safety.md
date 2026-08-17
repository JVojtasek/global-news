---
slug: ai-speed-vs-safety
title: Three AI Companies, One Week, Zero Time to Check Each Other's Work
dek: Google shipped a new model in three weeks, OpenAI dissolved the team built
  to catch dangerous ones, and Meta argued openness is safety. None of it was
  checked by anyone outside the building.
section: tech
type: analysis
depth: open
lang: en
date: '2026-08-17'
status: draft
confidence: 78
load: 0
topics: []
automation_generated: true
edition_slot: 5
automation_role: edition
generator: claude-code
format: ''
event_id: ''
series: ''
image_query: computer chip circuit board
sources:
- name: Ars Technica — Google announces Gemini 3.7 Flash just three weeks after
    previous release
  url: https://arstechnica.com/ai/2026/08/google-announces-gemini-3-7-flash-just-three-weeks-after-previous-release/
  published: '2026-08-13'
- name: The Verge — OpenAI reportedly disbanded its preparedness team
  url: https://www.theverge.com/ai-artificial-intelligence/980817/openai-disbands-preparedness-team
  published: '2026-08-16'
- name: The Verge — Rogue AI aren't science fiction anymore
  url: https://www.theverge.com/column/980337/rogue-ai-science-fiction-openai
  published: '2026-08-16'
- name: TechCrunch — Why people aren't buying Mark Zuckerberg's AI future
  url: https://techcrunch.com/2026/08/16/why-people-arent-buying-mark-zuckerbergs-ai-future/
  published: '2026-08-16'
- name: TechCrunch — Does Mark Zuckerberg really believe AI is 'for everyone'?
  url: https://techcrunch.com/video/does-mark-zuckerberg-really-believe-ai-is-for-everyone/
  published: '2026-08-14'
- name: The Verge — Apple trained its own AI model for China with help from Alibaba
  url: https://www.theverge.com/ai-artificial-intelligence/980160/apple-intelligence-china-custom-ai-model-alibaba
  published: '2026-08-14'
impact:
  areas:
  - safety
  - life
  line: Anyone who now leans on an AI tool for research, work or decisions is
    trusting products that shipped faster this week than any outside reviewer
    could realistically check them.
  todo: Before you let a new AI feature handle something that matters, look
    for what the company has published about how it was tested — not just
    what's new about it.
quiz:
  question: According to this article, how long was it between Google's
    Gemini 3.6 Flash and Gemini 3.7 Flash releases?
  options:
  - About three weeks
  - About three months
  - About a year
  answer: 0
  explanation: Ars Technica reported that Gemini 3.7 Flash launched just three
    weeks after version 3.6, with Google describing "substantial improvements."
---

## BRIEFLY

**What happened.** In one week, Google shipped a new AI model three weeks after the last one, OpenAI reportedly disbanded the team responsible for catching dangerous model behavior, and Meta pushed a message that open AI models are the safe choice — while facing public skepticism about it.

**What it means.** The pace at which AI companies release and restructure is now faster than the pace at which anyone outside those companies can independently check the results.

**Risks and impact.** People using AI tools for research, work, health or money questions are relying on systems that may have had less internal safety review than the last version, with no outside way to tell.

**What can be done.** Nothing about these specific decisions is reversible by a reader. What is available: treating "new" and "safety-tested" as two separate claims, and checking whether a company says anything concrete about the second one.

**What to watch.** Whether other AI labs follow OpenAI in scaling back dedicated risk-assessment teams, or whether this week turns out to be the exception industry critics point back to.

## FACTS

On August 13, Google released Gemini 3.7 Flash, an update to its AI model line that arrived just three weeks after Gemini 3.6 Flash, according to Ars Technica. Google described the new version as carrying "substantial improvements" over its predecessor.

Three days later, The Verge reported, citing the Financial Times, that OpenAI had disbanded its "preparedness" team at the end of July. That team's stated job was to assess whether AI models posed serious risks and to develop ways to reduce them before release. What happens to that work now is not fully clear from the reporting available — the Financial Times account, as relayed by The Verge, describes the team's dissolution but not, in detail, what replaced it.

The same week, Meta released an open-weight model called Glimmer, which anyone can download and run on their own hardware, in contrast to the company's more powerful Muse Spark model, which stays behind Meta's own servers and APIs. The release came with a public letter from Mark Zuckerberg arguing that AI should be "for everyone" rather than controlled by a small number of labs. By August 16, TechCrunch was covering public skepticism about that framing.

Separately, The Verge reported that Apple had built a custom AI model for the Chinese market in partnership with Alibaba, citing Reuters reporting based on three unnamed people familiar with the arrangement.

## EVIDENCE

Some of this is solid. Gemini 3.7 Flash's release date and Google's own description of it are directly confirmed — a company announcing its own product is about as documented as a tech story gets.

OpenAI's disbandment of its preparedness team rests on Financial Times reporting, relayed by The Verge. That is a single reporting chain, not independently corroborated by a second outlet in the material available here, and OpenAI's own public statement on the matter, if any, is not part of that reporting.

The Apple-Alibaba partnership is the least confirmed claim in this set: it comes from unnamed sources describing an arrangement that neither company has stated publicly. It should be read as reported, not established.

What connects the four stories is not proof of a single cause. No source claims OpenAI cut safety staff because Google is shipping faster, or that Meta's "AI for everyone" message is a direct response to either. What the timing shows is that all four are happening in the same stretch of days, in an industry where a model's public release and its internal safety review now compete for the same tight production calendar.

## PERSPECTIVES

**The velocity view**, implicit in how Google frames its own release cadence: faster iteration is itself a form of improvement, catching and fixing problems in the next version rather than trying to perfect the current one. This view has real support — software has shipped this way for decades — but it assumes flaws are cheap to fix after the fact, which is a different claim for a spreadsheet bug than for an AI system making decisions that affect people.

**The safety-researcher view**, represented in The Verge's column tracing renewed concern back to an OpenAI autonomous agent incident in July — the exact details of which remain unconfirmed in the reporting available — is that removing a dedicated risk-review team while such incidents are already surfacing is a foreseeable-risk story, not a neutral cost-cutting one. This view carries weight because it rests on a documented structural change, not speculation about intent.

**The openness-as-safety view**, articulated by Zuckerberg around Glimmer's release, holds that distributing model weights widely, rather than locking them behind one company's servers, prevents any single actor from having unchecked control. It is a coherent argument, but TechCrunch's reporting on public skepticism suggests it hasn't persuaded the audience it was aimed at — and it says nothing about whether Meta's own internal review of Glimmer was thorough.

**The market-and-geopolitics view**, visible in the Apple-Alibaba story, treats AI releases as shaped as much by where a company is legally and commercially allowed to operate as by any safety timeline. A model built partly to satisfy Chinese market requirements is optimized for a different set of constraints than one built purely around a lab's own risk assessment.

## CONTEXT

None of this happened in isolation from a longer trend. Major AI labs have moved, over a few years, from releasing a new model family roughly once a year to releasing incremental updates every few weeks. Each individual update is framed as small and low-risk. The cumulative effect is that the total amount of new, unreviewed-by-outsiders capability entering public use in a given month has grown, even where no single release looks alarming on its own.

Dedicated internal safety or "preparedness" teams were, in part, a response to exactly that problem — an attempt to keep a slower, more deliberate check running alongside a fast product cycle. When such a team is reduced or dissolved, the fast cycle doesn't automatically slow down to compensate; the check simply gets thinner, absorbed into general product teams whose primary incentive is still to ship.

What's not established here is how OpenAI's preparedness work will actually be handled going forward, whether it will be less rigorous in practice, or whether this is a reorganization rather than a reduction. The Financial Times report describes what was dissolved, not what replaced it in day-to-day terms.

## DEEPER

There's an old habit of mind that treats "newer" as a stand-in for "better" and "better" as a stand-in for "safer" — three different claims, quietly collapsed into one, every time a company ships an update with a version number one digit higher than the last.

That habit isn't new to AI. It's the same instinct that makes a freshly painted building look more trustworthy than an old one, regardless of what's actually holding up the walls. What AI adds is speed: the interval between "new" and "trusted" used to be long enough that reputation could catch up with reality. A model that changes every few weeks doesn't give that interval time to close.

The honest position isn't that new AI tools are secretly dangerous, or that the companies building them are careless. It's narrower and less satisfying: for any specific version of any specific tool, an ordinary user currently has very little way to know how much internal scrutiny it actually received before release. The absence of visible evidence isn't evidence of absence — but it isn't evidence of rigor, either.

What would change that isn't a smarter chatbot. It's the boring, unglamorous thing every other safety-critical industry eventually built: a visible, external record of what was checked, by whom, before the product reached the public. Aviation has it. Pharmaceuticals have it, however imperfectly. Consumer AI, as of this week, still mostly runs on a company's word.

## REFLECT

The next time an AI product announcement uses the word "improved," what would you actually want to know before believing the word "safer" was implied?

If a company can change how much internal risk review a model gets without telling its users, what does "trusting" that company's AI tools really mean in practice?
