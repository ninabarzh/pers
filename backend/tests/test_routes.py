# backend/tests/test_routes.py
import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_search_endpoint(client):
    response = client.get("/search", params={"q": "test"})
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_upload_endpoint_valid_data(client):
    test_data = [
        {
            "Id-repo": "1",  # Add this field
            "name": "Test Document",
            "organisation": "Test Org",
            "url": "http://example.com",
            "website": "http://example.com",
            "description": "A test document",
            "license": "MIT",
            "latest_update": "2023-10-01",
            "language": "Python",
            "last_commit": "2023-10-01",
            "open_pull_requests": "0",
            "master_branch": "main",
            "is_fork": "false",
            "forked_from": "",
        }
    ]
    response = client.post("/upload", json=test_data)
    assert response.status_code == 200

def test_upload_endpoint_invalid_json(client):
    # Pass invalid JSON as raw bytes
    response = client.post("/upload", content="invalid json", headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid JSON"}

def test_upload_endpoint_non_list_data(client):
    test_data = {"id": "1", "name": "Test Document"}
    response = client.post("/upload", json=test_data)
    assert response.status_code == 400
    assert response.json() == {"error": "Expected a list of documents"}