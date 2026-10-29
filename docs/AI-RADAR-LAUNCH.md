# AI radar — pilot preparation, 29 October 2026

## What is implemented

- `/cs/ai-radar/` and `/en/ai-radar/`: offer for a proposed Czech-language pilot.
- `/cs/ai-radar/sample/` and `/en/ai-radar/sample/`: dated documentation-based sample, with print styling and three primary sources.
- Proposed prices: CZK 249/month individual, CZK 1,490/month for up to five people. These are interest-test prices, not an active checkout or a signed offer.
- The business radar is an optional extension: public articles, morning briefing and Saturday edition remain free. The homepage keeps its public editorial lead; the optional business notice appears after the news rows.
- Links under “Pro firmy / For businesses” in the navigation and footer.
- Real Google verification meta value obtained from Search Console for `https://mypaper.news/` in the owner's signed-in account. Verification itself requires the published meta value.
- Existing canonical, hreflang, Open Graph, sitemap and robots infrastructure reused. Sample dates stay fixed when the site rebuilds.
- No paywall, account, payment collection, fabricated reference, or invented benchmark.
- Enquiries use `mailto:hello@mypaper.news`; they require the reader to send a message. This is not automated registration or newsletter consent. Inbox delivery is not verified by rendering the link.
- The old general newsletter fallback no longer shows a success message merely for opening a mail client.

## Source review

Primary documents opened on 29 October 2026:

1. https://learn.microsoft.com/en-us/power-automate/get-started-approvals
2. https://docs.n8n.io/build/integrate-ai/ai-examples/human-in-the-loop-for-tools.md
3. https://openai.com/enterprise-privacy/

The sample distinguishes vendor documentation, editorial interpretation and a proposed ten-case test. No hands-on testing, measured savings, product launch date or individual legal finding is claimed. Factcheck: names and capability descriptions compared with those documents. Guardian: no preaching or fabricated lived experience. Sceptic: limitations, plan dependence and missing empirical validation explicitly retained.

## Actual activation gates

1. **Cloudflare analytics:** after the owner signed in, the existing `mypaper.news` analytics site was found with zero reported visits in the last 24 hours. Switched from automatic injection to manual snippet installation, copied the actual beacon token into `data/site.yml`, and matched the dashboard's module script. Verify a deployed page load in the dashboard before claiming data collection. Only aggregate page views; never attach browser settings or email addresses. No API credential is stored in the repository.
2. **Google:** ownership of `https://mypaper.news/` was successfully verified by HTML tag on 29 October 2026. The sitemap index `https://mypaper.news/sitemap.xml` was then submitted and reported as successful. Ownership and accepted sitemaps are not guaranteed indexing. The overview already has search/indexing history; it is not a brand-new site with no data.
3. **Bing/Seznam:** the existing IndexNow key and robots sitemap entries support discovery. Announcing URLs is not proof that they are indexed. Dashboard ownership requires a real verification value or an authorized import.
4. **Newsletter:** no provider form URL is configured. Before claiming registration works, test double opt-in, correct language/cadence, unsubscribe, actual delivery and suppression of removed addresses. Avoid advertising pixels and individual click/open tracking. Store no health interests. Do not silently add enquiries to a mailing list.
5. **Commerce:** supplier identity, final tax-inclusive price/treatment, launch date, terms and cancellation must be provided before accepting payment. Never enable recurring billing merely by toggling this pilot file.
6. **Hosting:** GitHub Pages usage limits restrict online businesses and commercial SaaS. Select a suitable host before introducing commercial transactions/accounts; do not imply that a third-party checkout automatically resolves host terms. This phase is a public editorial sample and non-binding enquiry only. https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
7. **Handover:** AI subscriptions, the owner's computer, editorial checks and staff time are real dependencies and costs. A sale needs a transferable workflow and properly assessed handling of subscriber data.

## Preview and validation

The lightweight preview uses the production radar renderer; it does not run the full article/image build or alter `data/state.json`:

```
python -m tools.preview_radar --out C:/Users/Admin/AppData/Local/Temp/mypaper-radar-preview
python -m unittest discover -s tests -v
```

Serve that output using a loopback HTTP server to inspect the Czech and English versions, narrow screens, dark mode and print. Full-site build/deployment remains a separate result from this preview.

## First customer conversations

Show the public sample first. Ask which recurring decision it helps with, what is missing, and whether the proposed price makes sense. Track only actual replies and payments separately from visits. Never report clicking a mailto link as a lead or a paid conversion. Record renewal, cancellation and preparation/review time before calling the pilot profitable.
