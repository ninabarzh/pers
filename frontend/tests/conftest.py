import pytest
from starlette.testclient import TestClient

# Import from the installed package (how Docker sees it)
from app.main import app  # Updated import path

@pytest.fixture
def client():
    return TestClient(app)