# Reading metrics — draft, not deployed

This is an isolated prototype. It is not linked from the public site and the
client endpoint is deliberately blank. A separate D1 database and collector
have been created for My Paper; only the schema is present. Collector integration
tests were removed from the database, and the public site does not use it.

The collector accepts only the two reviewed article paths in `reviewedPaths`;
do not remove this restriction based solely on `g` health tags. Article tags
are incomplete: matching is English-oriented, capped at five, and can be
overridden by article metadata. A real launch needs an editorially reviewed
allowlist generated from one shared source for client and server, and a policy
for new or edited articles. The present prototype therefore does not provide
site-wide analytics.

Only daily counts and rounded visible-tab duration totals are written to a
separate D1 table. There are no session identifiers or reader preference fields.
Cloudflare still receives IP addresses as a network provider; disabled Worker
logs do not prove that all platform-level logs are disabled. Visible-tab time is
an estimate, not proof of reading. Requests can be forged, and small totals can
be identifying in context. Do not display small cohorts as anonymous results.

Before launch: review privacy and retention, add CS/EN privacy disclosures,
provide a private aggregate dashboard with suppression of small samples, review
abuse/rate limits and free-tier capacity, test CSP/CORS and browsing flows,
provision isolated D1, deploy collector, then activate client and verify both
languages and refusal of health or form data. Do not put credentials in git.

Run local checks with `node --test infra/reading-metrics/*.test.mjs`.
