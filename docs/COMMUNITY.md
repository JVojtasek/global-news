# My Paper community — comments and reactions

Comments and aggregated reactions are intentionally not enabled until a
moderated data service is connected. My Paper is a static GitHub Pages site;
pretending that browser-only likes are shared would mislead readers, while an
unmoderated public comment form would invite spam, abuse and legal risk.

## Recommended reader actions

Use three constructive reactions instead of a single popularity score:

- **Useful** — the article helped with a real decision or understanding;
- **Made me think** — it changed or complicated the reader's view;
- **Clear** — it explained a difficult mechanism well.

Do not add a public dislike counter. Disagreement belongs in a reasoned comment,
not a pile-on. Reaction totals should never change article ranking until enough
real traffic exists to make them meaningful.

## Comment promise

Every article may end with one specific question derived from `## REFLECT`.
Comments should add evidence, experience, a correction or a serious question.
They are not a general social feed.

Minimum controls before launch:

1. first comment from a new identity waits for moderation;
2. comments containing links wait for moderation;
3. rate limiting and bot protection;
4. report button and visible community rules;
5. no publication of addresses, phone numbers, private health information or
   identifying information about children;
6. correction requests receive a distinct route and are not buried in debate;
7. moderators can hide content without silently editing a reader's words;
8. privacy and terms pages name the provider, stored data and retention period.

AI may flag spam, threats, personal data and likely abuse, but it must not
silently approve accusations about named people or make the final decision in a
legally sensitive case.

## Technical choices

### Fastest free pilot: GitHub Discussions / Giscus

Good moderation, public audit trail and no custom database. The drawback is
significant: a general reader needs a GitHub account. Use only for an early,
technically inclined pilot.

### Recommended public version: small managed database plus bot protection

Use a narrowly scoped comments API, a managed database, email magic-link or
anonymous session, and a privacy-preserving challenge. Store only the article
slug, reaction, comment text, moderation state, timestamps and the minimum
identity needed to prevent abuse. Never send local reading preferences or
health interests.

## Launch order

1. Add the three reaction buttons and moderation-only preview.
2. Test with a small group and publish the community rules.
3. Enable comments only after the moderation queue, reports and deletion path
   work end to end.
4. Measure useful comments per 1,000 article views, reports, moderation time and
   returning commenters. Raw comment count is not a quality goal.
