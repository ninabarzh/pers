# backend/tests/conftest.py
import pytest
from starlette.testclient import TestClient
from app.main import app  # Import from the backend package

"""
Fixture to provide a test client for the backend app.
"""

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client
