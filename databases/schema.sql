CREATE TABLE IF NOT EXISTS sentiment (datetime datetime PRIMARY KEY, polarity NUMBER(4,2), percent_positive NUMBER(4,2), percent_negative NUMBER(4,2), tweet_count INTEGER);

CREATE INDEX idx_sentiment ON sentiment (datetime);