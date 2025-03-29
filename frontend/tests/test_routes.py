# frontend/tests/test_routes.py
import pytest
from starlette.testclient import TestClient
from app.main import app
import os
import json


@pytest.fixture
def client():
    return TestClient(app)


# UI Rendering Tests
def test_home_page_renders_correctly(client):
    """Test basic home page rendering with search form"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Search open source projects" in response.text
    assert 'form action="/"' in response.text  # Search form
    assert 'input type="search"' in response.text


def test_search_results_rendering(client):
    """Test search results page structure"""
    response = client.get("/?q=python")
    assert response.status_code == 200
    assert 'class="search-results"' in response.text
    assert 'class="result-item"' in response.text


def test_upload_page_rendering(client):
    """Test upload page form elements"""
    response = client.get("/upload")
    assert response.status_code == 200
    assert 'form action="/upload"' in response.text
    assert 'input type="file"' in response.text
    assert 'accept=".json"' in response.text


# Form Submission Tests
def test_file_upload_workflow(client):
    """Test complete file upload happy path"""
    test_data = [{
        "Id-repo": "test123",
        "name": "Frontend Test Project",
        "organisation": "Test Org",
        "description": "Test upload from frontend",
        "license": "MIT",
        "open_pull_requests": "3"
    }]

    # Test JSON upload
    test_file = ("test_upload.json", json.dumps(test_data).encode(), "application/json")
    response = client.post("/upload", files={"json_file": test_file})

    assert response.status_code == 200
    assert "Your data was successfully uploaded" in response.text
    assert 'href="/"' in response.text  # Back to search link


# Error Handling Tests
def test_upload_errors(client):
    """Test various upload error scenarios"""
    # Invalid JSON structure
    invalid_structure = {"not": "an array"}
    response = client.post("/upload", files={
        "json_file": ("bad.json", json.dumps(invalid_structure).encode(), "application/json")
    })
    assert "must be an array of documents" in response.text

    # Missing required field
    missing_field = [{"name": "Missing ID"}]
    response = client.post("/upload", files={
        "json_file": ("missing_field.json", json.dumps(missing_field).encode(), "application/json")
    })
    assert "missing required fields" in response.text

    # Test error page rendering
    assert 'class="error-message"' in response.text
    assert 'Try again' in response.text  # Recovery option


# Cross-Component Tests
def test_search_to_upload_flow(client):
    """Test navigation between search and upload"""
    # Start at search
    search_response = client.get("/")
    assert "Search" in search_response.text

    # Go to upload
    upload_response = client.get("/upload")
    assert "Upload" in upload_response.text

    # Verify navigation elements
    assert 'href="/"' in upload_response.text  # Back to search link
    assert 'href="/upload"' in search_response.text  # Upload link in nav


# Accessibility Tests
def test_aria_attributes(client):
    """Test basic accessibility features"""
    response = client.get("/")
    assert 'aria-label="Search"' in response.text
    assert 'role="navigation"' in response.text

    upload_response = client.get("/upload")
    assert 'aria-label="File upload"' in upload_response.text
    assert 'role="alert"' in upload_response.text  # For error messages
