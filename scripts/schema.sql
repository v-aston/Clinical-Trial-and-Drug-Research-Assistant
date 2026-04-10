CREATE TABLE IF NOT EXISTS source_documents (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    external_id TEXT,
    title TEXT NOT NULL,
    source_url TEXT,
    raw_text TEXT,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES source_documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    section TEXT,
    content TEXT NOT NULL,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding VECTOR(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);