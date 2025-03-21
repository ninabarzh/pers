import pytest
from app.typesense_client import TypesenseClient
from starlette.testclient import TestClient
from app.main import app  # Import the Starlette app

@pytest.fixture
def typesense_client():
    """
    Fixture to provide a TypesenseClient instance.
    """
    client = TypesenseClient()
    # Clear the collection before each test
    try:
        client.client.collections['ossfinder'].documents.delete({'filter_by': 'id: *'})
    except Exception as e:
        print(f"Error clearing collection: {e}")
    return client

@pytest.fixture
def test_client(mock_typesense_client):
    """
    Fixture to provide a test client for the Starlette app.
    """
    with TestClient(app) as client:
        yield client
