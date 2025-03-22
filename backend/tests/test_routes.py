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
    test_data = [{"id": "1", "name": "Test Document"}]
    response = client.post("/upload", json=test_data)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

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