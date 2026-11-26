import sqlite3
from werkzeug.security import generate_password_hash

def create_test_user(database_path, username="eugene", password="Difficult123Password!"):
    db = sqlite3.connect(database_path)

    password_hash = generate_password_hash(password)

    cursor = db.execute(
        "INSERT INTO users (username, password_hash) "
        "VALUES (?, ?)", 
        (username, password_hash)
    )

    user_id = cursor.lastrowid
    db.commit()
    db.close()

    return user_id

def log_in(client, user_id):
    """Set up an authenticated session with a CSRF token."""
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["session_version"] = 1
        session["csrf_token"] = "test-csrf-token"


def add_records(database_path, description, app, user_id):
    db = sqlite3.connect(database_path)

    cursor = db.execute(
        "INSERT INTO income_records "
        "(user_id, date, income_type, description, quantity, rate_per_unit) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, "2026-11-23", "Teaching", description, 2, 2500)
    )

    record_id = cursor.lastrowid
    db.commit()
    db.close()

    return record_id

