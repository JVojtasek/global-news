CREATE TABLE IF NOT EXISTS daily_metrics (
  day TEXT NOT NULL, path TEXT NOT NULL,
  clicks INTEGER NOT NULL DEFAULT 0, reading_samples INTEGER NOT NULL DEFAULT 0,
  reading_seconds INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, path)
);
