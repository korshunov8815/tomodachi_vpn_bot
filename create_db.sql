CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    is_trial INTEGER DEFAULT 1
);

CREATE TABLE servers (
    server_id INTEGER PRIMARY KEY,
    location TEXT NOT NULL,
    url TEXT NOT NULL
);

CREATE TABLE keys (
    key_id INTEGER PRIMARY KEY,
    key_name TEXT NOT NULL,
    outline_server_id INTEGER NOT NULL,
    key_server_id INTEGER NOT NULL,
    access_url TEXT NOT NULL,
    user_id INTEGER,
    expiration DATE,
    data_limit INTEGER, 
    is_free INTEGER NOT NULL DEFAULT 0,
    is_expired INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id) 
        REFERENCES users (user_id) 
        ON DELETE NO ACTION 
        ON UPDATE NO ACTION,

    FOREIGN KEY (outline_server_id) 
        REFERENCES servers (server_id) 
        ON DELETE NO ACTION 
        ON UPDATE NO ACTION
);

