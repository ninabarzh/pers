# frontend/tests/conftest.py
import pytest
from starlette.testclient import TestClient
from app.main import app  # Import the Starlette/FastAPI app from the frontend package

@pytest.fixture
def test_client():
    """
    Fixture to provide a test client for the frontend app.
    """
    with TestClient(app) as client:
        yield client