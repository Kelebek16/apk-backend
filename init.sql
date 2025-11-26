CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TABLE IF NOT EXISTS tweets_queue (
    id SERIAL PRIMARY KEY,
    tweet_text TEXT NOT NULL,
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    label VARCHAR(10),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('turkish', coalesce(tweet_text, ''))
    ) STORED
);

CREATE TABLE IF NOT EXISTS positive (
    id SERIAL PRIMARY KEY,
    data_id INT NOT NULL REFERENCES tweets_queue(id) ON DELETE CASCADE,
    tweet_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('turkish', coalesce(tweet_text, ''))
    ) STORED
);

CREATE TABLE IF NOT EXISTS negative (
    id SERIAL PRIMARY KEY,
    data_id INT NOT NULL REFERENCES tweets_queue(id) ON DELETE CASCADE,
    tweet_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('turkish', coalesce(tweet_text, ''))
    ) STORED
);

CREATE INDEX IF NOT EXISTS idx_tweets_queue_processed
    ON tweets_queue(is_processed, id);

CREATE INDEX IF NOT EXISTS idx_tweets_queue_label
    ON tweets_queue(label);

CREATE INDEX IF NOT EXISTS idx_tweets_search
    ON tweets_queue USING GIN (search_vector);

CREATE INDEX IF NOT EXISTS idx_positive_data_id
    ON positive(data_id);

CREATE INDEX IF NOT EXISTS idx_positive_search
    ON positive USING GIN (search_vector);

CREATE INDEX IF NOT EXISTS idx_negative_data_id
    ON negative(data_id);

CREATE INDEX IF NOT EXISTS idx_negative_search
    ON negative USING GIN (search_vector);
