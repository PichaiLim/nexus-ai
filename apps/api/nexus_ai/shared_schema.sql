CREATE TABLE IF NOT EXISTS shared_records (
    id uuid PRIMARY KEY,
    workspace text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('memory', 'skills')),
    owner text NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    source text,
    skill_key text,
    version integer,
    visibility text NOT NULL DEFAULT 'draft' CHECK (visibility IN ('draft', 'published', 'withdrawn')),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        (kind = 'memory' AND skill_key IS NULL AND version IS NULL) OR
        (kind = 'skills' AND skill_key IS NOT NULL AND version IS NOT NULL AND version > 0)
    ),
    UNIQUE (workspace, skill_key, version)
);

CREATE INDEX IF NOT EXISTS shared_records_lookup
    ON shared_records (workspace, kind, updated_at DESC, id);

CREATE TABLE IF NOT EXISTS shared_record_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    workspace text NOT NULL,
    record_id uuid NOT NULL,
    actor text NOT NULL,
    action text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
