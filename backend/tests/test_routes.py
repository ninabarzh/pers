# backend/tests/test_routes.py
from app.main import app  # Import Starlette app
from app.typesense_client import TypesenseClient, get_typesense_client # Import dependency


def test_search_endpoint(unit_client, mock_typesense):
    """Test search endpoint with mocked Typesense"""
    # Verify mock is empty first
    assert len(mock_typesense['ossfinder'].documents) == 0, \
        f"Mock should start empty but contains: {mock_typesense['ossfinder'].documents}"

    # Setup test data in the mock
    test_doc = {
        "Id-repo": "1",
        "name": "Test Document",
        "organisation": "Test Org",
        "url": "http://example.com",
        "website": "it works",
        "description": "Test description",
        "license": "MIT",
        "latest_update": "2023-01-01",
        "language": "Python",
        "last_commit": "2023-01-01",
        "open_pull_requests": "0",
        "master_branch": "main",
        "is_fork": "false",
        "forked_from": "",
    }
    mock_typesense['ossfinder'].create(test_doc)

    # Verify document was added
    assert len(mock_typesense['ossfinder'].documents) == 1
    assert mock_typesense['ossfinder'].documents["1"]["name"] == "Test Document"

    # Make the request
    response = unit_client.get("/search", params={"q": "test"})

    # Verify response
    assert response.status_code == 200
    results = response.json()
    print("\n=== Search Results ===")
    print(results)  # Debug output

    assert results['found'] == 1, f"Expected 1 result, got {results['found']}"
    assert len(results['hits']) == 1
    assert results['hits'][0]['document']['name'] == "Test Document"


def test_upload_endpoint_valid_data(unit_client, unit_typesense_client):
    """Test valid data upload with mocked Typesense"""
    test_data = [{
        "Id-repo": "2",
        "name": "New Document"
    }]

    # Mock the index_data method
    unit_typesense_client.index_data = lambda data: None

    response = unit_client.post("/upload", json=test_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_health_check(unit_client, monkeypatch):
    """Test health check endpoint"""
    # Patch the health check with a direct lambda
    monkeypatch.setattr(
        'app.main.get_typesense_client',
        lambda: type('MockClient', (), {
            'health': lambda self: {
                "ok": True,
                "status": "operational",
                "version": "test"
            }
        })()
    )

    response = unit_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
