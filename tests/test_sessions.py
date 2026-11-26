from tests.helpers import create_test_user

def test_old_session_cookie_rejected_after_logout(client, app):

    create_test_user(app.config["DATABASE"])

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

    old_cookie = client.get_cookie("session")

    with client.session_transaction() as session:
        session["csrf_token"] = "test-token"

    response = client.post(
        "/logout",
        data={"csrf_token": "test-token"}
    )

    client.set_cookie("session", old_cookie.value)

    response = client.get("/")

    assert response.status_code == 302
    assert response.location == "/login"

def test_protected_page_redirect_to_login(client, app):
    response = client.get("/records")

    assert response.status_code == 302
    assert response.location == "/login"