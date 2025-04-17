# frontend/tests/test_admin_routes.py
import pytest
from starlette.testclient import TestClient
from app.main import app
import json
import httpx
from starlette.requests import Request


class MockResponse(httpx.Response):
    def __init__(self, status_code, json_data=None):
        super().__init__(
            status_code=status_code,
            json=json_data or {},
            request=Request({"type": "http", "method": "POST"})
        )
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise httpx.HTTPStatusError(
                message=f"HTTP error {self.status_code}",
                request=self.request,
                response=self
            )


class MockAsyncClient:
    def __init__(self):
        self._closed = False

    async def post(self, url, **kwargs):
        if self._closed:
            raise RuntimeError("Client is closed")

        if url == "http://testbackend/upload":
            data = kwargs.get('json', [])

            if not data or not all(isinstance(item, dict) for item in data):
                return MockResponse(400, {"detail": "Invalid data format"})

            if not all('Id-repo' in item for item in data):
                return MockResponse(400, {"detail": "Missing Id-repo field"})

            return MockResponse(200, {"detail": "Success"})

        return MockResponse(404, {"detail": "Not Found"})

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._closed = True
        return None


@pytest.fixture
def client(monkeypatch):
    test_client = TestClient(app)

    # Create a synchronous mock that returns an already-created client
    def sync_async_client(*args, **kwargs):
        # Create a new mock client for each test
        mock_client = MockAsyncClient()

        # Return a context manager that immediately enters and returns the client
        class SyncContextManager:
            async def __aenter__(self):
                return mock_client

            async def __aexit__(self, *args):
                await mock_client.__aexit__(*args)

        return SyncContextManager()

    monkeypatch.setattr(httpx, "AsyncClient", sync_async_client)

    test_client.app.state.config = {'BACKEND_URL': 'http://testbackend'}
    yield test_client


@pytest.fixture
def test_data():
    return [{
        "Id-repo": "test123",
        "name": "Test Project",
        "organisation": "Test Org",
        "description": "Test description",
        "license": "MIT",
        "url": "http://example.com"
    }]


def test_admin_page_renders(client):
    """Test admin page loads correctly"""
    response = client.get("/admin")
    assert response.status_code == 200
    assert "Upload JSON" in response.text
    assert 'enctype="multipart/form-data"' in response.text


def test_admin_upload_success(client, test_data):
    """Test successful file upload"""
    test_file = ("projects.json", json.dumps(test_data).encode(), "application/json")
    response = client.post("/admin", files={"json_file": test_file})
    assert response.status_code == 200


def test_admin_upload_missing_field(client, test_data):
    """Test upload with missing required field"""
    invalid_data = test_data.copy()
    invalid_data[0].pop("Id-repo")
    test_file = ("bad.json", json.dumps(invalid_data).encode(), "application/json")
    response = client.post("/admin", files={"json_file": test_file})
    assert response.status_code == 200
    assert "Missing Id-repo field" in response.text


def test_admin_upload_no_file(client):
    """Test upload with no file provided"""
    response = client.post("/admin", data={})
    assert response.status_code == 200


def test_admin_upload_invalid_json(client):
    """Test upload with invalid JSON"""
    test_file = ("invalid.json", b"not json", "application/json")
    response = client.post("/admin", files={"json_file": test_file})
    assert response.status_code == 200
    assert "Invalid JSON file" in response.text
