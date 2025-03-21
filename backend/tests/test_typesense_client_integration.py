# backend/tests/test_typesense_client_integration.py
import pytest
from app.typesense_client import TypesenseClient

def test_ensure_collection_exists(typesense_client):
    """
    Test the ensure_collection_exists method.
    """
    # Ensure the collection exists
    typesense_client.ensure_collection_exists()

    # Verify that the collection exists
    collection = typesense_client.client.collections['ossfinder'].retrieve()
    assert collection['name'] == "ossfinder"

def test_search(typesense_client):
    """
    Test the search method.
    """
    # Index some data
    data = [
        {
            "Id-repo": "123",
            "name": "Test Repo",
            "organisation": "Test Org",
            "url": "http://example.com",
            "website": "http://example.com",
            "description": "Test description",
            "license": "MIT",
            "latest_update": "2023-10-01",
            "language": "Python",
            "last_commit": "2023-10-01",
            "open_pull_requests": "5",
            "master_branch": "main",
            "is_fork": "false",
            "forked_from": ""
        }
    ]
    typesense_client.index_data(data)

    # Perform a search
    results = typesense_client.search("Test Repo")

    # Assert the results
    assert len(results['hits']) > 0
    assert results['hits'][0]['document']['name'] == "Test Repo"

def test_document_exists(typesense_client):
    """
    Test the document_exists method.
    """
    # Index some data
    data = [
        {
            "Id-repo": "123",
            "name": "Test Repo",
            "organisation": "Test Org",
            "url": "http://example.com",
            "website": "http://example.com",
            "description": "Test description",
            "license": "MIT",
            "latest_update": "2023-10-01",
            "language": "Python",
            "last_commit": "2023-10-01",
            "open_pull_requests": "5",
            "master_branch": "main",
            "is_fork": "false",
            "forked_from": ""
        }
    ]
    typesense_client.index_data(data)

    # Check if a document exists
    assert typesense_client.document_exists("123") is True

def test_index_data(typesense_client):
    """
    Test the index_data method.
    """
    # Index some data
    data = [
        {
            "Id-repo": "123",
            "name": "Test Repo",
            "organisation": "Test Org",
            "url": "http://example.com",
            "website": "http://example.com",
            "description": "Test description",
            "license": "MIT",
            "latest_update": "2023-10-01",
            "language": "Python",
            "last_commit": "2023-10-01",
            "open_pull_requests": "5",
            "master_branch": "main",
            "is_fork": "false",
            "forked_from": ""
        }
    ]
    typesense_client.index_data(data)

    # Verify that the document was created
    document = typesense_client.client.collections['ossfinder'].documents["123"].retrieve()
    assert document['name'] == "Test Repo"
