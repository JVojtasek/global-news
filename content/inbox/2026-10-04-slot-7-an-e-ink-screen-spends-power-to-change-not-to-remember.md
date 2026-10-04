---
slug: an-e-ink-screen-spends-power-to-change-not-to-remember
title: "An E-Ink Screen Spends Power to Change, Not to Remember"
dek: "Charged pigment particles hold their position after an update, giving electronic paper its long static life and its conspicuously slower refresh."
section: tech
type: feature
depth: open
lang: en
date: '2026-10-04'
status: reserve
confidence: 94
load: 0
topics: []
automation_generated: true
edition_slot: 7
automation_role: edition
generator: chatgpt-work
format: wider-lens
event_id: evergreen-electrophoretic-display-bistability
series: ''
image_query: macro close-up electronic paper e-reader black white pixels
sources:
  - name: "E Ink — How electronic ink works"
    url: "https://www.eink.com/tech/detail/How_it_works"
    published: ''
  - name: "Microchip Developer Help — ePaper Display Fundamentals"
    url: "https://developerhelp.microchip.com/xwiki/bin/view/software-tools/mgs/dev-kits/epd-ug/fundamentals/"
    published: ''
  - name: "Journal of Printing Science and Technology — Electrophoretic Electronic Paper Displays"
    url: "https://www.jstage.jst.go.jp/article/nig/44/5/44_5_257/_article/-char/en"
    published: '2007-01-01'
  - name: "IEEE Spectrum — How E Ink Developed Full-Color e-Paper"
    url: "https://spectrum.ieee.org/how-e-ink-developed-full-color-epaper"
    published: '2022-01-25'
qma_path: ''
tickers: []
quiz:
  question: "Why can text remain visible on a typical electrophoretic e-paper display after power is removed?"
  options:
    - "The screen keeps a hidden backlight running from stored charge."
    - "The display prints a disposable film for each page."
    - "Pigment particles remain in their last stable positions until another electric field moves them."
  answer: 2
  explanation: "Electrophoretic e-paper is bistable: an update uses electric fields to rearrange charged pigment particles, and the resulting image can persist without continuous power to the display."
---

## BRIEFLY

**What happened.** Electrophoretic e-paper forms an image by moving charged pigment particles through fluid inside tiny cells or capsules.

**What it means.** Once the particles reach a stable position, the display can keep showing the page without continuously powering each pixel. Energy is concentrated in the update rather than in remembering a static image.

**Risks and impact.** The same mechanism creates trade-offs. Refreshes are slower than on LCD or OLED screens, previous images may leave faint traces, and colour, animation and cold-weather performance demand more complicated control.

**What can be done.** Choose e-paper for information that changes occasionally and must remain readable for long periods. Choose a conventional display when rapid motion and frequent updates matter more.

**What to watch.** Product claims should separate display power from the rest of the device. Wireless radios, processors, front lights and touch layers still consume energy even while the electronic paper holds a page.

## FACTS

Most familiar e-paper readers use an electrophoretic display. In a common black-and-white design, microscopic cells contain dark and light pigment particles with opposite electrical charges suspended in a fluid. Electrodes create an electric field that pulls one set of particles toward the viewing surface and pushes the other away.

When light particles rise, that area appears light; when dark particles rise, it appears dark. A controller combines those areas into letters and images. E Ink describes the screen as reflective because it uses ambient light rather than emitting light from every pixel. Devices may add a front light, but that light is separate from the basic image-forming mechanism.

The display is also bistable. The particles can remain where the update placed them after the electric field stops, so a static image does not need continuous display power. Updating does require energy. The timing and voltage sequence—often called a waveform—depends on the transition and display type.

## EVIDENCE

E Ink's technical material says unchanged regions do not need updating and describes refresh modes for different speed and image-quality needs. The company also states that no power is required to hold an image. As the manufacturer, it is an authoritative source for its implementation but has an obvious interest in emphasising advantages.

Microchip's independent developer documentation explains the same mechanism: oppositely charged particles move under an electric field, stay in place after the update and suit low-duty-cycle interfaces. It also lists the constraints engineers must design around—slow refresh, limited colour or grayscale and interfaces that should not depend on smooth animation.

A 2007 technical review in the Journal of Printing Science and Technology documents the early commercial spread of electrophoretic paper and identifies response time and colour as central development challenges. IEEE Spectrum's engineering history, written by E Ink technical officers and labelled as such, gives more detail about voltage waveforms, reflective colour filters and multipigment cells.

The evidence supports a precise claim: the display layer can retain a static image with little or no holding power. It does not support the broader slogan that an entire e-reader uses no energy while a page is visible.

## PERSPECTIVES

### The reader's view

The page looks calm because it is not being continuously redrawn by emitted light. In bright surroundings, more ambient light can improve the view. A front light helps in darkness, but then some of the famous low-power advantage is being spent on illumination.

### The embedded engineer's view

E-paper is attractive when a sensor, label or sign sleeps for minutes or days between changes. The display can preserve the last state while the processor rests. For a moving pointer, video feed or fast menu, the same screen becomes a poor fit.

### The product marketer's view

"Weeks of battery life" is memorable. It can also blur the boundary between the panel and the product. Radios fetching books, processors indexing pages, touch controllers and lights have their own budgets.

### The display scientist's view

The black-and-white cell is only the beginning. Colour requires filters or more pigment species, and each choice trades brightness, resolution, saturation and update speed. The design problem is not simply adding colour; it is controlling several kinds of charged particles without losing the virtues of reflective paper.

## CONTEXT

Conventional screens and e-paper solve different jobs. An LCD uses a backlight and liquid-crystal layer to regulate transmitted light. An OLED pixel emits light. Those architectures can update rapidly because their visual state is actively driven. Electrophoretic paper physically rearranges pigment, which takes longer but leaves a persistent result.

The update is more like moving furniture than switching a lamp. An electric field pushes and pulls particles into a new arrangement. The controller may flash the screen through intermediate states to clear residual charge and reduce ghosting. Partial updates can be quicker, but repeated shortcuts may leave remnants that eventually require a fuller refresh.

Temperature matters because particles move through fluid. Controllers and waveforms compensate, yet cold conditions can slow the response. Colour adds another layer of difficulty. Filter-based systems divide reflected light among colour subpixels, reducing brightness or effective resolution. Multipigment systems must sort particles by different charges, sizes and movements.

These constraints explain e-paper's best habitats: books, shelf labels, badges, timetables and status panels. Their content changes, but not sixty times a second. A page can sit for ten minutes; a price label for days. The display's patience becomes an advantage.

That fit between medium and message is more important than novelty. The right question is not whether e-paper can imitate every task of a phone screen, but whether the information benefits from persistence, daylight readability and infrequent change.

## DEEPER

Digital technology is often described as restless: everything refreshes, polls and demands attention. E-paper offers a different design metaphor. Information can be electronic without being in motion. The screen does the energetic work at the moment of change, then leaves the result alone.

That temporal pattern matters. A technology should be judged not only by peak speed but by the rhythm of the job. A display that is miserable for video may be excellent for a battery-powered sign. Calling one screen "better" without naming the update rhythm is like comparing a noticeboard with a cinema screen by frame rate.

Bistability also makes persistence visible. A conventional display goes blank when its supporting power disappears. An electrophoretic page can remain, showing the last message even if the processor has stopped. That can be useful, but it creates a small interpretive hazard: visible does not mean current. A stale train time or sensor reading may look perfectly alive.

The practical question is therefore double. How much energy does it take to show information, and how does the system signal that the information is fresh? E-paper solves the first problem elegantly. Designers still have to solve the second, especially when a frozen image can look as authoritative as a newly updated one.

## PRACTICAL IMPACT

For a device comparison, ask how often the screen changes, whether it uses a front light, and what the processor and wireless connection consume. For a status display, look for a visible timestamp or freshness indicator. The image may survive a power loss; the underlying information may not.

## READER OUTCOME

You should be able to explain how charged particles create and retain an e-paper image, why that saves energy for static content, and why refresh speed and information freshness remain separate limitations.

## REFLECT

Which information in your day truly needs to move, and which would be more useful if it simply stayed legible without asking for attention?

When a screen can outlive the system behind it, what should make an old image look old?

Would a slower display change only the device's battery life, or might it also change the pace at which you expect information to arrive and disappear?
