---
slug: a-queue-is-inventory-with-people-inside-it
title: A Queue Is Inventory with People Inside It
dek: Little’s Law connects arrivals, waiting time and work in progress with one compact equation—but averages cannot tell you whether the wait feels fair.
section: business
type: feature
depth: open
lang: en
date: '2026-09-22'
status: reserve
confidence: 90
load: 0
topics:
  - queues
  - operations
  - Little's Law
  - customer experience
automation_generated: true
edition_slot: 7
automation_role: edition
generator: chatgpt-work
format: ''
event_id: evergreen-littles-law-queue-operations-1961
series: ''
image_query: people waiting in orderly service queue operations illustration
sources:
  - name: John D. C. Little — A Proof for the Queuing Formula L = λW
    url: https://www.jstor.org/stable/167570
    published: '1961-06-01'
  - name: John D. C. Little — Little's Law as Viewed on Its 50th Anniversary
    url: https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/
    published: '2011-05-01'
  - name: Richard C. Larson — Perspectives on Queues, Social Justice, and the Psychology of Queueing
    url: https://www.jstor.org/stable/171439
    published: '1987-11-01'
  - name: Don Norman — The Psychology of Waiting Lines
    url: https://www.researchgate.net/publication/200085847_The_Psychology_of_waiting_lines
    published: '2008-08-21'
qma_path: ''
tickers: []
quiz:
  question: A stable service completes 12 cases an hour, and a case spends 30 minutes in the system on average. What does Little’s Law imply?
  options:
    - An average of 3 cases are in the system
    - An average of 6 cases are in the system
    - Exactly 24 cases must arrive every hour
  answer: 1
  explanation: Little’s Law gives L = λW. Twelve cases per hour multiplied by 0.5 hour equals an average of six cases in the system.
---

## BRIEFLY

**What happened.** In 1961, John D. C. Little proved a remarkably general relationship: the average number of items in a stable system equals their average arrival rate multiplied by their average time in the system.

**What it means.** If work arrives at 12 cases an hour and each case spends half an hour in the process, about six cases are present on average.

**Risks and impact.** The formula links waiting to work in progress, but it does not reveal who waits longest, why capacity fails or whether a queue feels fair.

**What can be done.** Measure arrivals, elapsed time and work in progress using the same boundary and period; then reduce one source of avoidable delay at a time.

**What to watch.** If demand persistently exceeds capacity, the queue is not stable and a tidy long-run average can conceal a backlog that keeps growing.

## FACTS

A queue is easy to see at an airport desk and easy to miss inside an office. An unread claim, a repair ticket, a patient awaiting a result and an unfinished software task are all items spending time in a system. Operations researchers call that stock work in progress. Customers call much of it waiting.

Little’s Law writes the relationship as **L = λW**. **L** is the average number of items in the chosen system. **λ** is the average rate at which items enter or leave it over the long run. **W** is the average time an item spends there. The units do much of the teaching: cases per hour multiplied by hours per case leaves cases.

Suppose a stable service completes 12 cases an hour and each case spends 30 minutes from entry to exit. Twelve multiplied by half an hour equals six. On average, six cases are somewhere inside the system—being worked, waiting for a handoff or parked for approval.

## EVIDENCE

Little’s 1961 paper gave a proof under broad conditions, helping turn an empirical rule into a foundational result of queueing theory. Fifty years later, he emphasized how widely the relationship travels. The “items” can be people, aircraft, manufacturing parts, messages or computer instructions. The law does not require a particular arrival pattern, service-time distribution or queue discipline.

Its generality comes with conditions that ordinary dashboards often blur. The boundaries must be consistent. If **L** counts customers from check-in to departure, **W** must measure that same journey, and **λ** must describe flow through the same system. The averages must refer to a period in which arrivals and departures balance in a meaningful long-run sense. Starting with an empty queue or ending with a large backlog can distort a short window.

The law is an identity, not a diagnosis. It can expose an impossible claim—halving average time while holding throughput and work in progress unchanged—but it does not say which step to redesign. Nor does it tell a manager what staffing level will produce a target wait. Variability, capacity, priorities and scheduling rules still matter.

## PERSPECTIVES

### The operations view

For an operator, Little’s Law makes invisible inventory visible. A team may celebrate that everyone is busy while requests spend days between touches. Counting only active work hides the queue. Counting everything inside the boundary connects delay to the number of open items and the rate at which the system actually finishes them.

This is why limits on work in progress can be powerful. Starting fewer items can shorten feedback loops and reduce handoffs. But a limit is not magic: if incoming demand remains above sustainable capacity, rejected or hidden work simply forms another queue outside the measured boundary.

### The customer view

Two queues with the same average duration can feel radically different. Richard Larson’s work on queueing and social justice highlighted the importance of order and fairness. A single serpentine line often feels more legitimate than several lines because it visibly follows “first come, first served.” Priority rules may be necessary, but unexplained exceptions look like favouritism.

Don Norman’s discussion of waiting adds feedback, expectations and emotion. People cope better when they know that the system has recognized them, understand what happens next and receive an honest estimate. Occupying attention can change the experience of time, but theatre should not become a substitute for repairing unnecessary delay.

### The leadership view

Averages are attractive because they fit a slide. They can also erase the tail. An average wait of ten minutes might combine many quick cases with a few people waiting an hour. Segmenting by case type, vulnerability, channel or time of day can reveal who pays for a process that looks efficient in aggregate.

## CONTEXT

The word “queue” suggests a line, yet the more consequential queues are often lists. Digital systems remove the physical discomfort of standing while making delay harder to inspect. A customer sees “in progress”; internally, the case may wait in several departmental piles.

Business language can make the same people appear as units of inventory. The analogy is analytically useful and morally incomplete. A component does not need to collect a child, manage pain, renew a visa or wonder whether an application disappeared. A good operations measure must therefore be paired with a customer outcome and a fairness check.

Little’s Law also separates three levers that managers sometimes confuse. Faster throughput can reduce a backlog if capacity genuinely rises. Lower work in progress can reduce time when teams stop opening more work than they can advance. Lower arrival rates may reflect prevention, clearer eligibility or suppressed demand; the last of those is not automatically an improvement.

## DEEPER

### A 15-minute queue audit

Choose one process and draw one boundary: from a clearly observable entry to a clearly observable exit. Count how many items are inside now. Estimate how many exit in a typical hour or day. Measure elapsed time for a small recent sample, including waiting as well as active work.

Then check whether the three quantities roughly agree under **L = λW**. Large disagreement is not a reason to force the equation. It is a clue that boundaries, units, time windows or data definitions differ—or that the system is changing too quickly for a stable average.

Next, inspect the oldest items rather than only the mean. Ask where they paused, whether priorities were explained and whether any group repeatedly receives a longer wait. Pick one reversible change: remove a duplicate approval, create an explicit handoff, cap the number of simultaneous cases or send a truthful status update.

Measure again over a comparable period. If a faster average comes with more abandonment, errors or excluded demand, the queue has not necessarily improved. The practical goal is not to make a metric elegant. It is to move work reliably while respecting the people whose time the system is holding.

## REFLECT

Little’s Law turns a queue into a relationship that can be checked. Its best use is modest: make delay and inventory discussable, catch inconsistent claims and point toward better questions. The equation counts people correctly only when the organization remembers that people are more than the count.

