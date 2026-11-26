
import sqlite3

import pytest


def create_user(app, username):
    """Create a user directly in the test database."""
    db = sqlite3.connect(app.config["DATABASE"])

    cursor = db.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
        """,
        (username, "test-password-hash")
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


def create_record(app, user_id):
    """Create an income record for a user."""
    db = sqlite3.connect(app.config["DATABASE"])

    cursor = db.execute(
        """
        INSERT INTO income_records
        (user_id, date, income_type, description, quantity, rate_per_unit)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, "2026-11-23", "Teaching", "Test class", 2, 2500)
    )

    record_id = cursor.lastrowid
    db.commit()
    db.close()

    return record_id


def test_export_without_keyword(client, app):
    """Export should work when the optional keyword is omitted."""
    user_id = create_user(app, "export_user")
    log_in(client, user_id)

    response = client.get("/records/export?year=2026")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert b"Date,Category,Description" in response.data


def test_user_cannot_delete_another_users_record(client, app):
    """A user must not be able to delete another user's income record."""
    owner_id = create_user(app, "record_owner")
    other_user_id = create_user(app, "other_user")

    record_id = create_record(app, owner_id)

    log_in(client, other_user_id)

    response = client.post(
        f"/delete/{record_id}",
        data={"csrf_token": "test-csrf-token"}
    )

    assert response.status_code == 302

    db = sqlite3.connect(app.config["DATABASE"])

    record = db.execute(
        "SELECT id FROM income_records WHERE id = ?",
        (record_id,)
    ).fetchone()

    db.close()

    assert record is not None


def test_delete_with_extremely_large_id_does_not_return_500(client, app):
    """An ID outside SQLite's integer range should be handled safely."""
    user_id = create_user(app, "large_id_user")
    log_in(client, user_id)

    huge_id = 2**63

    response = client.post(
        f"/delete/{huge_id}",
        data={"csrf_token": "test-csrf-token"}
    )

    assert response.status_code != 500
