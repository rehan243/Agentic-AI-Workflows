-- track agent runs end to end so we can debug flaky tool loops later
-- heavy indexes on foreign keys because joins blow up once you have millions of rows

CREATE TABLE IF NOT EXISTS agent_runs (
  id            BIGSERIAL PRIMARY KEY,
  session_id    UUID NOT NULL,
  agent_name    TEXT NOT NULL,
  started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at   TIMESTAMPTZ,
  status        TEXT NOT NULL CHECK (status IN ('running', 'ok', 'error', 'cancelled')),
  error_class   TEXT,
  meta          JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_session ON agent_runs (session_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status_time ON agent_runs (status, started_at DESC);

CREATE TABLE IF NOT EXISTS tool_calls (
  id           BIGSERIAL PRIMARY KEY,
  run_id       BIGINT NOT NULL REFERENCES agent_runs (id) ON DELETE CASCADE,
  tool_name    TEXT NOT NULL,
  args         JSONB NOT NULL DEFAULT '{}'::jsonb,
  result       JSONB,
  latency_ms   INTEGER,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_run ON tool_calls (run_id, created_at);

CREATE TABLE IF NOT EXISTS conversation_logs (
  id         BIGSERIAL PRIMARY KEY,
  run_id     BIGINT NOT NULL REFERENCES agent_runs (id) ON DELETE CASCADE,
  role       TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
  content    TEXT NOT NULL,
  token_est  INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_conv_run ON conversation_logs (run_id, created_at);

CREATE TABLE IF NOT EXISTS run_metrics (
  run_id       BIGINT PRIMARY KEY REFERENCES agent_runs (id) ON DELETE CASCADE,
  total_tokens INTEGER,
  tool_errors  INTEGER NOT NULL DEFAULT 0,
  retries      INTEGER NOT NULL DEFAULT 0,
  cost_usd     NUMERIC(12, 6)
);

-- partial index: only care about expensive failures when paging incidents
CREATE INDEX IF NOT EXISTS idx_agent_runs_errors
  ON agent_runs (started_at DESC)
  WHERE status = 'error';
