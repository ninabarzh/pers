# frontend/tests/test_routes.py
import pytest
from starlette.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Search" in response.text  # Check for a keyword in the home page

def test_home_route_with_query(client):
    response = client.get("/?q=test")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Search" in response.text  # Check for a keyword in the home page
    assert "test" in response.text  # Check if the query is reflected in the response

def test_upload_route(client):
    response = client.get("/upload")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Upload" in response.text  # Check for a keyword in the upload page

def test_handle_upload_route(client):
    # Test with no file
    response = client.post("/upload")
    print(f"Response (no file): {response.status_code} - {response.headers} - {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "No file provided." in response.text, "Expected error message for no file provided."

    # Test with a JSON file
    test_json_file = ("test.json", b'{"key": "value"}')
    response = client.post("/upload", files={"json_file": test_json_file})
    print(f"Response (with JSON file): {response.status_code} - {response.headers} - {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Upload successful!" in response.text, "Expected success message for JSON file upload."

    # Test with a non-JSON file
    test_txt_file = ("test.txt", b"Test file content")
    response = client.post("/upload", files={"json_file": test_txt_file})
    print(f"Response (with non-JSON file): {response.status_code} - {response.headers} - {response.text}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "Upload successful!" in response.text, "Expected success message for non-JSON file upload."

def test_handle_upload_with_test_json(client):
    # Test with the test.json file
    with open("/app/tests/test.json", "rb") as file:
        response = client.post("/upload", files={"json_file": ("test.json", file)})
        print(f"Response (test.json): {response.status_code} - {response.headers} - {response.text}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "Upload successful!" in response.text, "Expected success message for JSON file upload."