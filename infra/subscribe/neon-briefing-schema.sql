-- Dedicated My Paper briefing schema. Run only in the independent My Paper project.
-- Addresses and section choices are collected only for newsletter enrollment;
-- browser preferences, health interests and IP addresses do not belong here.
CREATE SCHEMA IF NOT EXISTS briefing;
CREATE TABLE IF NOT EXISTS briefing.subscribers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  lang text NOT NULL CHECK (lang IN ('cs', 'en')),
  sections text[] NOT NULL CHECK (cardinality(sections) BETWEEN 1 AND 10),
  confirmed_at timestamptz NOT NULL,
  unsubscribed_at timestamptz,
  unsubscribe_hash text NOT NULL UNIQUE CHECK (unsubscribe_hash ~ '^[0-9a-f]{64}$'),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS briefing.pending_confirmations (
  email text PRIMARY KEY,
  lang text NOT NULL CHECK (lang IN ('cs', 'en')),
  sections text[] NOT NULL CHECK (cardinality(sections) BETWEEN 1 AND 10),
  token_hash text NOT NULL UNIQUE CHECK (token_hash ~ '^[0-9a-f]{64}$'),
  requested_at timestamptz NOT NULL,
  expires_at timestamptz NOT NULL CHECK (expires_at > requested_at)
);
CREATE TABLE IF NOT EXISTS briefing.deliveries (
  subscriber_id uuid NOT NULL REFERENCES briefing.subscribers(id) ON DELETE CASCADE,
  edition_date date NOT NULL,
  state text NOT NULL CHECK (state IN ('claimed', 'sent', 'failed', 'unknown', 'skipped')),
  claimed_at timestamptz NOT NULL DEFAULT now(),
  provider_id text,
  PRIMARY KEY (subscriber_id, edition_date)
);
CREATE INDEX IF NOT EXISTS briefing_active_subscribers_idx
  ON briefing.subscribers(id) WHERE unsubscribed_at IS NULL;
CREATE INDEX IF NOT EXISTS briefing_pending_expiry_idx
  ON briefing.pending_confirmations(expires_at);

-- Defense in depth: reject health and unknown sections even if an API validator fails.
DO $$ BEGIN ALTER TABLE briefing.subscribers ADD CONSTRAINT briefing_subscribers_allowed_sections CHECK (sections <@ ARRAY['world','business','tech','science','culture','travel','motoring','sport','food','goodnews','history','questions','meaning','relationships','parenting','wonder','ai','safety','soul','mysteries']::text[] AND array_position(sections, NULL) IS NULL); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN ALTER TABLE briefing.pending_confirmations ADD CONSTRAINT briefing_pending_allowed_sections CHECK (sections <@ ARRAY['world','business','tech','science','culture','travel','motoring','sport','food','goodnews','history','questions','meaning','relationships','parenting','wonder','ai','safety','soul','mysteries']::text[] AND array_position(sections, NULL) IS NULL); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
