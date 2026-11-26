from tests.helpers import create_test_user, log_in, add_records

def test_csv_neutralises_cells(client, app):
    user_id = create_test_user(app.config["DATABASE"])
    log_in(client, user_id)

    descriptions = [
    "=HYPERLINK('https://malicious-site.com', 'Click Here')",
    "+123456",
    "-123456",
    "@SUM(A1:A10)"
    ]

    add_records(app.config["DATABASE"], descriptions[0], client, user_id)
    add_records(app.config["DATABASE"], descriptions[1], client, user_id)
    add_records(app.config["DATABASE"], descriptions[2], client, user_id)
    add_records(app.config["DATABASE"], descriptions[3], client, user_id)

    response = client.get("/records/export?year=2026")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"

    csv_content = response.data.decode("utf-8")

    expected = [
    "'=HYPERLINK('https://malicious-site.com', 'Click Here')",
    "'+123456",
    "'-123456",
    "'@SUM(A1:A10)"
    ]

    assert expected[0] in csv_content
    assert expected[1] in csv_content
    assert expected[2] in csv_content
    assert expected[3] in csv_content

def test_post_without_csrf_token(client, app):

    response = client.post(
        "/login",
        data={
            "username": "eugene",
            "password": "Difficult123Password!"
        }
    )

    assert response.status_code == 400
    