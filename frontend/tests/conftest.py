# frontend/tests/conftest.py
import pytest
from app.main import app  # Update the import path
from starlette.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)
