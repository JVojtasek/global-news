# Reading metrics — controlled pilot

The pilot uses a dedicated My Paper Cloudflare Worker and D1 database. The
collector is independently switchable with `ENABLE_COLLECTOR` in wrangler.toml.

The collector accepts only explicitly reviewed article paths in the generated
public allowlist; do not replace this restriction with `g` health tags. Article tags
are incomplete: matching is English-oriented, capped at five, and can be
overridden by article metadata. `reviewed-paths.json` records the reviewed
source and its SHA-256 with normalised line endings. The build removes an item
if the source changes or the article stops being published. Additions require
review of the complete text in each language. This pilot is not site-wide.

Only daily counts and rounded visible-tab duration totals are written to a
separate D1 table. There are no session identifiers or reader preference fields.
Cloudflare still receives IP addresses as a network provider; disabled Worker
logs do not prove that all platform-level logs are disabled. Visible-tab time is
an estimate, not proof of reading. Requests can be forged, and small totals can
be identifying in context. Do not display small cohorts as anonymous results.

`report.ps1` queries a private aggregate report for the last 30 days and writes
an HTML file in the current user's temp folder. It suppresses low counts. The
global per-location rate limiter is approximate, and the D1 daily cap limits
accepted events, not requests. Shared free Worker limits still apply. Do not
put credentials in git. Source preference fields must never be submitted.

Run local checks with `node --test infra/reading-metrics/*.test.mjs`.
