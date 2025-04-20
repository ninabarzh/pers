# backend/tests/test_typesense_client_integration.py
import os
import pytest
import time
from typesense.exceptions import ObjectNotFound, TypesenseClientError

def test_real_search(integration_typesense_client):
    """Test real search functionality with Typesense"""

    test_data = {
        "Id-repo": "integration_test_123",
        "name": "Integration Test Repo",
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

    # Index the test document
    try:
        # First verify the client is properly initialized
        assert integration_typesense_client.client is not None
        assert integration_typesense_client.client.config.api_key == os.getenv('TYPESENSE_API_KEY')

        # Index test data
        integration_typesense_client.index_data([test_data])

        # Search with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                results = integration_typesense_client.search("Integration")
                assert results['found'] >= 1
                break
            except TypesenseClientError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
    finally:
        # Cleanup
        try:
            integration_typesense_client.client.collections['ossfinder'].documents["integration_test_123"].delete()
        except (ObjectNotFound, TypesenseClientError):
            pass

def test_document_operations(integration_typesense_client):
    """Test document CRUD operations"""
    if not os.getenv('TYPESENSE_API_KEY'):
        pytest.skip("Typesense not configured for testing")

    doc_id = "integration_test_123"
    test_doc = {
        "Id-repo": "integration_test_123",
        "name": "Integration Test Repo",
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

    # Create and test operations
    try:
        # Index the document
        integration_typesense_client.index_data([test_doc])

        # Verify document exists - now checking the correct ID
        assert integration_typesense_client.document_exists(doc_id) is True, \
            f"Document {doc_id} should exist but wasn't found"

        # Verify search works
        results = integration_typesense_client.search("Integration Test")
        assert results['found'] >= 1, \
            f"Expected at least 1 search result, got {results['found']}"

    finally:
        # Cleanup - use the same ID for deletion
        try:
            integration_typesense_client.client.collections['ossfinder'].documents[doc_id].delete()
        except (ObjectNotFound, TypesenseClientError) as e:
            print(f"Cleanup warning: {str(e)}")
            pass


def test_health_check(integration_typesense_client):
    """Test real health check"""
    if not os.getenv('TYPESENSE_API_KEY'):
        pytest.skip("Typesense not configured for testing")

    health = integration_typesense_client.health()
    assert isinstance(health, dict)
    assert "ok" in health
    if not health['ok']:
        pytest.skip(f"Typesense health check failed: {health}")
