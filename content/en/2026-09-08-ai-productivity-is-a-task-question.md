---
slug: ai-productivity-is-a-task-question
title: AI Productivity Is a Task Question, Not a Universal Percentage
dek: Studies can find faster customer service, more completed code, or slower expert
  development without contradicting one another. The result depends on the worker,
  task, tool and definition of finished.
section: ai
type: analysis
depth: open
lang: en
date: '2026-09-08'
status: review
confidence: 95
load: 0
topics: []
automation_generated: true
edition_slot: 2
automation_role: edition
generator: chatgpt-work
format: ''
event_id: 2026-09-08-slot-2-ai-productivity-measurement
series: ''
image_query: conceptual split workflow stopwatch quality check AI productivity editorial
  illustration no text
sources:
- name: The Quarterly Journal of Economics — Generative AI at Work
  url: https://academic.oup.com/qje/article/140/2/889/7990658
  published: '2025-02-04'
- name: Organization Science — Navigating the Jagged Technological Frontier
  url: https://pubsonline.informs.org/doi/10.1287/orsc.2025.21838
  published: '2026-03-11'
- name: Management Science — The Effects of Generative AI on High-Skilled Work
  url: https://pubsonline.informs.org/doi/10.1287/mnsc.2025.00535
  published: '2026-02-27'
- name: METR — Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer
    Productivity
  url: https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/
  published: '2025-07-10'
- name: METR — We Are Changing Our Developer Productivity Experiment Design
  url: https://metr.org/blog/2026-02-24-uplift-update/
  published: '2026-02-24'
qma_path: ''
tickers: []
quiz:
  question: What did the randomized METR study find for experienced developers working
    on their own large open-source repositories with early-2025 AI tools?
  options:
  - They finished tasks 19% faster
  - They took 19% longer
  - Their completion time did not change
  answer: 1
  explanation: Across 246 real issues completed by 16 experienced developers, allowing
    AI increased completion time by an estimated 19%; METR warned that this narrow
    result should not be generalized to all coding.
review_reason: 'citlivé téma: referendum'
---

## BRIEFLY

**What happened.** A growing body of field experiments finds that generative AI can raise productivity, but the size and even the direction of the effect changes across jobs and tasks.

**What it means.** “AI makes workers 20% faster” is not a portable fact. A study result belongs to a particular tool, workforce, workflow, outcome and moment in the technology’s development.

**Risks and impact.** Companies can buy licenses, redesign jobs or cut staffing on the strength of a headline number that excludes verification, quality failures or work shifted to somebody else.

**What can be done.** Run a small comparison on real recurring tasks. Measure elapsed time through approval, error rates and rework—not merely time to first draft.

**What to watch.** Better evidence will separate task categories, adoption, quality and learning effects instead of compressing them into one average.

## FACTS

The positive findings are real. In [The Quarterly Journal of Economics](https://academic.oup.com/qje/article/140/2/889/7990658), Erik Brynjolfsson, Danielle Li and Lindsey Raymond studied the staggered introduction of an AI assistant in customer support. Access raised issues resolved per hour by 15% on average. Gains were larger for less experienced and lower-skilled agents; the most experienced workers saw smaller speed gains and slight declines in quality.

A different set of field experiments, published in [Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.2025.00535), randomized access to a coding assistant at Microsoft, Accenture and a Fortune 100 company. Pooling 4,867 developers, the researchers estimated a 26.08% increase in completed tasks, with a standard error of 10.3%. Each company’s individual estimate was noisy, and adoption was higher among less experienced developers.

Then there is the result that travels most awkwardly through AI marketing. METR recruited 16 experienced contributors to large open-source projects and randomized 246 real issues from repositories they already knew. With early-2025 tools available, developers took an estimated 19% longer. They had expected a 24% speed-up before the experiment and still believed afterward that AI had made them 20% faster.

These numbers are not votes in a referendum. They answer different questions.

## EVIDENCE

Customer support offered a repeated, measurable unit: issues resolved per hour, combined with quality signals. The assistant surfaced guidance resembling the practices of strong agents. That helps explain why workers with less accumulated experience gained more. It does not prove the same mechanism applies to legal strategy, laboratory research or maintaining a mature codebase.

The corporate coding trials measured completed tasks from ordinary company systems. Their scale is a strength. But the pooled 26.08% estimate has substantial uncertainty, and task completion is not a complete account of long-run maintainability or downstream review.

METR’s experiment captured something the larger study did not: experts performing two-hour tasks in codebases rich with unwritten requirements. The researchers included testing, documentation, style and readiness for human review in the definition of completion. Time spent prompting, waiting, checking and correcting therefore counted. The sample of developers was small and specialized, which limits generalization; the within-developer randomization and screen recordings make the particular finding harder to dismiss as anecdote.

The strongest cross-check comes from consulting. A preregistered experiment with 758 knowledge workers, now published in [Organization Science](https://pubsonline.informs.org/doi/10.1287/orsc.2025.21838), found that people using GPT-4 completed 12.2% more tasks and worked 25.1% faster on 18 tasks within the model’s capability frontier. On a deliberately different task outside that frontier, AI users were 19% less likely to reach the correct solution.

Productivity rose sharply—until task fit changed.

## PERSPECTIVES

One interpretation is that the studies are outdated almost as soon as they appear. Models, interfaces and user habits improve quickly. That is true, but it is not a license to substitute the newest demo for measurement. A new tool changes the answer; it does not abolish the question.

A second view is that positive findings are industry promotion and negative findings are resistance. Funding and conflicts matter, yet study design matters more. Randomization, realistic tasks, predeclared outcomes and transparent uncertainty are more useful filters than whether a number feels optimistic.

A third view treats productivity as personal sensation. AI can make difficult work feel smoother and reduce the discomfort of a blank page. That experience has value. It is still possible to feel faster while taking longer, as the METR participants did.

Finally, an average can conceal distribution. A tool may raise the floor for novices, add little for experts and create a small set of costly failures. An organization must decide whether its bottleneck is draft production, judgment, review, coordination or accountability.

## CONTEXT

Technology has often delivered its largest gains after work was reorganized around it. Simply placing a new tool inside an old process may create another queue: prompts, generated output, verification and repair.

Generative AI makes that transition unusually hard to see because its output is immediate and fluent. The first visible artifact arrives quickly. The finished product may not. A summary still needs its sources checked; code still needs tests and review; a customer answer still needs to resolve the problem.

The “jagged frontier” is a better mental model than a universal uplift. Two tasks that look equally hard to a person may be radically different for a model. A worker cannot safely identify the boundary from confidence or prose quality alone.

The boundary also moves. METR’s [February 24, 2026 update](https://metr.org/blog/2026-02-24-uplift-update/) said later data weakly suggested better speed-ups, but participation and task-selection biases had become severe. Developers who valued AI most were less willing to accept AI-free assignments, and 30% to 50% said they withheld some tasks from the experiment. The researchers changed the design rather than presenting a clean-looking number they no longer trusted.

## PEOPLE

The practical divide is not between people who “believe in AI” and those who do not. It is between workers whose tasks, standards and experience interact differently with the tool.

A new support agent may benefit from distilled organizational knowledge. An experienced maintainer may spend extra time explaining context that already exists in their head. A consultant may move quickly through ideation while becoming more likely to accept a persuasive error on a task the model cannot solve.

Managers face another human problem: saved minutes do not automatically become saved money or better service. They may become more output, more checking, shorter queues, higher expectations or simply a less exhausting day. Each is a different outcome.

Workers should therefore have a voice in choosing the tasks tested and the failures counted. Otherwise a productivity program can reward visible generation while hiding the burden of cleanup.

## DEEPER

Before adopting a productivity claim, translate it into one sentence: “For these people, using this version of this tool on these tasks changed this measured outcome over this period.” If any blank is missing, the percentage is advertising shorthand.

A practical team test can be small. Select 20 to 30 comparable tasks from one recurring workflow. Decide in advance which can use AI and which form the comparison. Record active human time, waiting time, review time, rework, defects and a simple quality score. Keep the definition of “done” identical. Note worker experience and whether the tool was actually used.

Review results by task type before calculating an average. Look for work that became reliably faster, work that merely felt easier and work where checking erased the gain. Repeat when the model or workflow changes.

Do not use the exercise to monitor individuals or rank employees; that encourages gaming and suppresses failures. Use it to map the workflow. The most valuable result may be a rule such as “use AI for first-pass classification, not final approval.”

AI productivity is not a property printed on the model. It is an outcome produced by a system of people, tasks, incentives, interfaces and quality standards. The honest unit is not “the AI user.” It is the completed piece of work.

## REFLECT

Which part of your work becomes faster with AI only because somebody else now carries the verification burden?

If a tool makes work more enjoyable but not faster, would that still justify using it—and how would you measure that value?
