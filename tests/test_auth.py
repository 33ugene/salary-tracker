import sqlite3

import pytest

from tests.helpers import create_test_user


def test_register_valid_details_creates_account(client, app):
    """" Valid registration details should create a new account. """

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/register",
        data={
            "username": "eugene",
            "password": "Difficult123Password!",
            "confirmation": "Difficult123Password!",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 302

    db = sqlite3.connect(app.config["DATABASE"])
    cursor = db.execute("SELECT * FROM users WHERE username = ?", ("eugene",))

    user = cursor.fetchone()
    db.close()

    assert user is not None


def test_register_weak_password_rejected(client, app):
    """A password with a zxcvbn score below 3 should be rejected."""

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/register",
        data={
            "username": "eugene",
            "password": "abcd1234",
            "confirmation": "abcd1234",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 200

    db = sqlite3.connect(app.config["DATABASE"])
    cursor = db.execute("SELECT * FROM users WHERE username = ?", ("eugene",))

    user = cursor.fetchone()
    db.close()

    assert user is None


def test_register_duplicate_username_rejected(client, app):
    """A username that already exists should not be registered again."""

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/register",
        data={
            "username": "eugene",
            "password": "Difficult123Password!",
            "confirmation": "Difficult123Password!",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 302

    response = client.post(
        "/register",
        data={
            "username": "eugene",
            "password": "Difficult123Password!",
            "confirmation": "Difficult123Password!",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 200
    assert b"Username already exists" in response.data

    db = sqlite3.connect(app.config["DATABASE"])
    cursor = db.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("eugene",))

    user = cursor.fetchone()
    db.close()

    assert user[0] == 1


def test_register_password_over_72_characters_rejected(client, app):
    """Passwords longer than 72 characters should be rejected."""

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/register",
        data={
            "username": "eugene",
            "password": "$CP9CqYA!?y^e~Y3W4h*j1*^Wr^WE=d7M#~fzeZzxV*=X89Gg7rz^bftTgG4gg1PGVMM=Tffb",
            "confirmation": "$CP9CqYA!?y^e~Y3W4h*j1*^Wr^WE=d7M#~fzeZzxV*=X89Gg7rz^bftTgG4gg1PGVMM=Tffb",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 200
    assert b"Max password length is 72 characters" in response.data

    db = sqlite3.connect(app.config["DATABASE"])
    cursor = db.execute("SELECT * FROM users WHERE username = ?", ("eugene",))

    user = cursor.fetchone()
    db.close()

    assert user is None


def test_login_valid_credentials(client, app):
    create_test_user(app.config["DATABASE"], "eugene", "Difficult123Password!")

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "Difficult123Password!",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["user_id"] is not None

    assert response.location == "/"

def test_login_invalid_password_rejected(client, app):
    create_test_user(app.config["DATABASE"], "eugene", "Difficult123Password!")

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "SomeWrongPassword123!!!",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 200
    assert b"Invalid password or username" in response.data

    with client.session_transaction() as session:
        assert "user_id" not in session

def test_login_invalid_password_sixth_time(client, app):
    create_test_user(app.config["DATABASE"], "eugene", "Difficult123Password!")

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "WrongPassword1231",
            "csrf_token": "test-token"
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "WrongPassword1232",
            "csrf_token": "test-token"
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "WrongPassword1233",
            "csrf_token": "test-token"
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "WrongPassword1234",
            "csrf_token": "test-token"
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "WrongPassword1235",
            "csrf_token": "test-token"
        }
    )
    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "WrongPassword1236",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 429
    assert b"Too many attempts. Try again later." in response.data

    with client.session_transaction() as session:
        assert "user_id" not in session

def test_username_case_insensitive(client, app):
    create_test_user(app.config["DATABASE"], "eugene", "Difficult123Password!")

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/login",
        data={
            "username": "Eugene",
            "password": "Difficult123Password!",
            "csrf_token": "test-token"
        }
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["user_id"] is not None

    assert response.location == "/"