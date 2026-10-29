-- Only the separate My Paper database. Both send types count failed attempts.
-- 140/day in UTC ensures at most 280 attempts across any provider day,
-- leaving 20 of Brevo's 300 daily sends for operational variation.
CREATE TABLE IF NOT EXISTS briefing.send_budget_v2 (
 day date NOT NULL,
 kind text NOT NULL CHECK (kind IN ('confirmation','digest')),
 used integer NOT NULL CHECK (used >= 0 AND ((kind='confirmation' AND used<=40) OR (kind='digest' AND used<=100))),
 PRIMARY KEY(day,kind)
);

CREATE OR REPLACE FUNCTION briefing.confirm_pending(p_hash text,p_now_ms bigint,p_unsubscribe_hash text)
RETURNS text LANGUAGE plpgsql AS $$
DECLARE pending briefing.pending_confirmations%ROWTYPE;
BEGIN
 PERFORM pg_advisory_xact_lock(2026102901);
 SELECT * INTO pending FROM briefing.pending_confirmations
  WHERE token_hash=p_hash AND expires_at>to_timestamp(p_now_ms/1000.0) FOR UPDATE;
 IF NOT FOUND THEN RETURN 'invalid'; END IF;
 IF NOT EXISTS (SELECT 1 FROM briefing.subscribers WHERE email=pending.email AND unsubscribed_at IS NULL)
    AND (SELECT count(*) FROM briefing.subscribers WHERE unsubscribed_at IS NULL)>=100 THEN
  RETURN 'full';
 END IF;
 DELETE FROM briefing.pending_confirmations WHERE token_hash=p_hash;
 INSERT INTO briefing.subscribers(email,lang,sections,confirmed_at,unsubscribe_hash)
 VALUES (pending.email,pending.lang,pending.sections,to_timestamp(p_now_ms/1000.0),p_unsubscribe_hash)
 ON CONFLICT(email) DO UPDATE SET lang=EXCLUDED.lang,sections=EXCLUDED.sections,
  confirmed_at=EXCLUDED.confirmed_at,unsubscribe_hash=EXCLUDED.unsubscribe_hash,
  unsubscribed_at=NULL,updated_at=now();
 RETURN 'confirmed';
END $$;
