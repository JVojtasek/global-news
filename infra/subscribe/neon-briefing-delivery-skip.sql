-- Apply after a reviewed deployment plan to the standalone My Paper project only.
-- Before applying, check that the named constraint is the existing state check.
ALTER TABLE briefing.deliveries DROP CONSTRAINT deliveries_state_check;
ALTER TABLE briefing.deliveries ADD CONSTRAINT deliveries_state_check
  CHECK (state IN ('claimed', 'sent', 'failed', 'unknown', 'skipped'));
