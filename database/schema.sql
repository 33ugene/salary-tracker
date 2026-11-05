CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS income_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    income_type TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    rate_per_unit INTEGER NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(id)
);