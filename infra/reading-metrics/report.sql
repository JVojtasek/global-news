-- Execute privately in Cloudflare D1. Counts are events, not unique people.
-- Suppressing small counts limits but cannot eliminate re-identification risk.
SELECT path, CASE WHEN SUM(clicks) >= 5 THEN SUM(clicks) ELSE NULL END AS clicks,
       CASE WHEN SUM(reading_samples) >= 5 THEN SUM(reading_samples) ELSE NULL END AS reading_samples,
       CASE WHEN SUM(reading_samples) >= 5
            THEN ROUND(1.0 * SUM(reading_seconds) / SUM(reading_samples))
            ELSE NULL END AS avg_visible_seconds
FROM daily_metrics
WHERE day >= date('now', '-30 days')
GROUP BY path
HAVING SUM(clicks) >= 5 OR SUM(reading_samples) >= 5
ORDER BY clicks DESC;
