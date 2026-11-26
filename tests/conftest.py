import os

# SETTING UP ENVIRONMENTS VARIALBES
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["APP_ENV"] = "development"

import pytest
import tempfile
import sqlite3

from app import app as flask_app


@pytest.fixture
def app():
    # Save the original Flask configuration
    original_database = flask_app.config["DATABASE"]
    original_testing = flask_app.config.get("TESTING", False)

    try:
        # Enable testing mode
        flask_app.config.update(TESTING=True)

        # Create a temporary database for each test
        with tempfile.TemporaryDirectory() as tmp_dir:
            database_path = os.path.join(tmp_dir, "test_salary.db")

            flask_app.config["DATABASE"] = database_path

            # Connect to the temporary database
            db = sqlite3.connect(database_path)

            # Create tables using your actual schema
            with open("database/schema.sql", "r") as sql_file:
                sql_script = sql_file.read()

            db.executescript(sql_script)
            db.commit()
            db.close()

            # Make the Flask application available to tests
            yield flask_app

    finally:
        # Restore the original configuration
        flask_app.config["DATABASE"] = original_database
        flask_app.config["TESTING"] = original_testing


@pytest.fixture
def client(app):
    # Create a test client using the test application
    return app.test_client()
