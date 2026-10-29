-- Isolated My Paper project only. Reservations include confirmation emails
-- and daily emails; failed attempts intentionally consume budget too.
CREATE TABLE IF NOT EXISTS briefing.send_budget (
  day date PRIMARY KEY,
  used integer NOT NULL CHECK (used BETWEEN 0 AND 20)
);
