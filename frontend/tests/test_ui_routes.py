# frontend/tests/test_ui_routes.py
import pytest
from starlette.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_home_page_renders_correctly(client):
    """Test basic home page rendering with search form"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Search OSS Projects" in response.text
    assert 'form action="/"' in response.text
    assert 'input type="text"' in response.text
    assert 'placeholder="Search projects..."' in response.text


def test_search_results_rendering(client):
    """Test search results page structure"""
    test_query = "testquery123"
    response = client.get(f"/?q={test_query}")
    assert response.status_code == 200
    assert 'Search OSS Projects' in response.text

# Accessibility Tests
def test_aria_attributes(client):
    """Test accessibility features"""
    response = client.get("/")
    # assert 'aria-label="Toggle navigation"' in response.text
    # assert 'aria-controls="navbarContent"' in response.text
    # assert 'aria-expanded="false"' in response.text

    # Check for search input's aria attributes
    assert 'aria-label="Search"' in response.text