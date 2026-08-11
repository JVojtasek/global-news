# MY PAPER → QMA: measurement contract

The link is useful only when the article genuinely concerns technology or
markets. It is never inserted into unrelated sections.

## Events and attribution

| Metric | Definition | Source |
| --- | --- | --- |
| `wider_lens_views` | Views of articles that contain both EVIDENCE and PERSPECTIVES | privacy-friendly site analytics |
| `qma_outbound_clicks` | Clicks on the contextual QMA link; browser event name `QMA Outbound` | My Paper analytics |
| `mypaper_to_qma_ctr` | `qma_outbound_clicks / wider_lens_views` | derived weekly |
| `qma_attributed_arrivals` | QMA sessions with `utm_source=mypaper`, `utm_medium=editorial` | QMA analytics |
| `qma_attributed_signups` | QMA registrations attributed to those UTM sessions | QMA analytics |

Every contextual link includes campaign `wider_lens` and the My Paper article
slug as `utm_content`. The outbound click also records the article slug and the
selected QMA path. This makes topic-level measurement possible without adding
tracking cookies to My Paper.

## Weekly decision rule

- Report CTR by article and destination; do not optimize on raw clicks alone.
- Keep a destination only when it helps the reader continue the same question.
- Review misleading or weak CTAs even if their CTR is high.
- Never infer investment suitability from a click. QMA remains analytical and
  educational, not a broker or personal adviser.

The event code and UTM links work now. Actual counts appear only after a
privacy-friendly analytics provider is configured in `data/site.yml` and QMA
records the same UTM parameters.
