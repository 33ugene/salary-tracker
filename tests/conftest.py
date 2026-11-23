import pytest
import tempfile
import sqlite3
import os

from app import app as flask_app

@pytest.fixture
def app():
    original_database = flask_app.config["DATABASE"]
    original_testing = flask_app.config.get("TESTING", False)


    try:
        flask_app.config.update(TESTING=True,)

        with tempfile.TemporaryDirectory() as tmp_dir:
            database_path = os.path.join(tmp_dir, "test_salary.db")

            flask_app.config["DATABASE"] = database_path
            db = sqlite3.connect(flask_app.config["DATABASE"])

            with open("database/schema.sql", "r") as sql_file:
                sql_script = sql_file.read()

            db.executescript(sql_script)
            db.commit()
            db.close()
            yield flask_app
    
    finally:
        flask_app.config["DATABASE"] = original_database
        flask_app.config["TESTING"] = original_testing


