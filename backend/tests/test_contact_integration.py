# backend/tests/test_contact_integration.py
import os
import pytest
import starlette.testclient
from app.main import app


@pytest.fixture
def contact_client():
    # Create a test client with DEBUG mode enabled
    os.environ['DEBUG'] = 'true'
    with starlette.testclient.TestClient(app) as client:
        yield client
    os.environ.pop('DEBUG', None)


def test_contact_form_submission(contact_client):
    """Test contact form submission with debug mode"""
    form_data = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "Test message",
        "consent": "on",
        "frc-captcha-solution": "TEST_SOLUTION",
        "csrf_token": "test-csrf-token"
    }

    response = contact_client.post("/contact", data=form_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"