import pytest
import sys
import os
os.environ["DISABLE_METRICS"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """
    Creates a fresh Flask app instance for testing with a real Postgres test DB.
    """

    os.environ["DATABASE_URL"] = "postgresql+psycopg2://postgres:postgres@localhost:5432/microloans_test"

    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
