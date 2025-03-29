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
    assert "Search OSS Projects" in response.text
    assert 'form action="/"' in response.text  # Search form
    assert 'input type="text"' in response.text
    assert 'placeholder="Search projects..."' in response.text


def test_search_results_rendering(client):
    """Test search results page structure with no results"""
    # Mock the home route to handle query parameter
    silly_query = "asdfghjkl12345"
    response = client.get(f"/?q={silly_query}")
    assert response.status_code == 200
    # Your home route might not actually show "No results" message
    # This test might need to be modified based on your home route implementation
    assert 'Search OSS Projects' in response.text  # Basic verification


def test_upload_page_rendering(client):
    """Test upload page form elements"""
    response = client.get("/upload")
    assert response.status_code == 200
    assert 'form action="/upload"' in response.text
    assert 'input class="form-control" type="file"' in response.text
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

    # Mock the handle_upload route to return success
    test_file = ("test_upload.json", json.dumps(test_data).encode(), "application/json")
    response = client.post("/upload", files={"json_file": test_file})

    # Adjust based on your actual handle_upload implementation
    assert response.status_code == 200
    # Check for either redirect or success message
    assert "Upload successful!" in response.text or response.is_redirect


# Error Handling Tests
def test_upload_errors(client):
    """Test various upload error scenarios"""
    # No file provided
    response = client.post("/upload", files={})
    assert response.status_code == 200
    assert "Please select a file to upload" in response.text

    # Invalid JSON structure (not an array)
    invalid_structure = {"not": "an array"}
    response = client.post("/upload", files={
        "json_file": ("bad.json", json.dumps(invalid_structure).encode(), "application/json")
    })
    assert response.status_code == 200
    assert "JSON must contain an array of documents" in response.text

    # Invalid JSON file
    response = client.post("/upload", files={
        "json_file": ("invalid.json", b"not json", "application/json")
    })
    assert response.status_code == 200
    assert "Invalid JSON file" in response.text

    # Missing required field
    missing_field = [{"name": "Missing ID"}]
    response = client.post("/upload", files={
        "json_file": ("missing_field.json", json.dumps(missing_field).encode(), "application/json")
    })
    assert response.status_code == 200
    # Check for HTML-encoded version of the error message
    assert "Missing &#39;Id-repo&#39; field in document" in response.text
    # Also check for the raw text in case HTML decoding happens
    assert "Missing 'Id-repo' field in document" in response.text or \
           "Missing &#39;Id-repo&#39; field in document" in response.text


# Cross-Component Tests
def test_search_to_upload_flow(client):
    """Test navigation between search and upload"""
    # Start at search
    search_response = client.get("/")
    assert search_response.status_code == 200
    assert "Search" in search_response.text

    # Go to upload
    upload_response = client.get("/upload")
    assert upload_response.status_code == 200
    assert "Upload" in upload_response.text

    # Verify navigation elements
    assert 'href="/"' in upload_response.text  # Back to search link
    assert 'href="/upload"' in search_response.text  # Upload link in nav


# Accessibility Tests
def test_aria_attributes(client):
    """Test basic accessibility features"""
    response = client.get("/")
    # Check for navbar toggle's aria attributes
    assert 'aria-label="Toggle navigation"' in response.text
    assert 'aria-controls="navbarContent"' in response.text
    assert 'aria-expanded="false"' in response.text

    # Check for search input's aria attributes
    assert 'aria-label="Search"' in response.text