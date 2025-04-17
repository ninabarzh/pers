# backend/tests/test_typesense_client_integration.py
import pytest
from app.typesense_client import TypesenseClient
from typesense.exceptions import ObjectNotFound
import time


class MockTypesenseClient:
    def __init__(self):
        self.collections = {
            'ossfinder': MockCollection()
        }
        self.health = lambda: {"ok": True}
        # Add API key validation
        self.config = {
            'api_key': 'test_key',
            'nodes': [{'host': 'typesense', 'port': '8108', 'protocol': 'http'}],
            'connection_timeout_seconds': 3.0
        }


class MockCollection:
    """Mock for Typesense collection"""

    def __init__(self):
        self.documents = {}
        self.schema = {
            "name": "ossfinder",
            "fields": [
                {"name": "Id-repo", "type": "string"},
                {"name": "name", "type": "string"},
                {"name": "organisation", "type": "string"},
                {"name": "url", "type": "string"},
                {"name": "website", "type": "string"},
                {"name": "description", "type": "string"},
                {"name": "license", "type": "string"},
                {"name": "latest_update", "type": "string"},
                {"name": "language", "type": "string"},
                {"name": "last_commit", "type": "string"},
                {"name": "open_pull_requests", "type": "string"},
                {"name": "master_branch", "type": "string"},
                {"name": "is_fork", "type": "string"},
                {"name": "forked_from", "type": "string"},
            ]
        }

    def retrieve(self):
        return self.schema

    def delete(self):
        self.documents = {}

    def create(self, schema):
        self.schema = schema

    def search(self, params):
        query = params.get('q', '')
        return {
            'hits': [
                {
                    'document': doc
                    for doc in self.documents.values()
                    if query.lower() in doc.get('name', '').lower()
                }
            ]
        }


class MockDocument:
    """Mock for Typesense document operations"""

    def __init__(self, collection):
        self.collection = collection

    def create(self, document):
        doc_id = document['Id-repo']
        self.collection.documents[doc_id] = document

    def retrieve(self, doc_id):
        if doc_id in self.collection.documents:
            return self.collection.documents[doc_id]
        raise ObjectNotFound(f"Document {doc_id} not found")


@pytest.fixture
def typesense_client(monkeypatch):
    """Fixture with custom mock implementation"""
    mock_client = MockTypesenseClient()

    # Patch the actual client initialization
    def mock_init_client(self):
        self.client = mock_client
        self._initialized = True

    monkeypatch.setattr(TypesenseClient, '_initialize_client', mock_init_client)

    client = TypesenseClient()
    client.collections['ossfinder'].documents = MockDocument(client.collections['ossfinder'])
    yield client

    # Cleanup
    client.collections['ossfinder'].delete()


def test_ensure_collection_exists(typesense_client):
    """Test collection creation"""
    typesense_client.ensure_collection_exists()
    collection = typesense_client.client.collections['ossfinder'].retrieve()
    assert collection['name'] == "ossfinder"


def test_search(typesense_client):
    """Test search functionality"""
    test_data = {
        "Id-repo": "123",
        "name": "Test Repo",
        "organisation": "Test Org"
    }
    typesense_client.client.collections['ossfinder'].documents.create(test_data)

    results = typesense_client.search("Test")
    assert len(results['hits']) > 0
    assert results['hits'][0]['document']['name'] == "Test Repo"


def test_document_exists(typesense_client):
    """Test document existence check"""
    test_data = {
        "Id-repo": "123",
        "name": "Test Repo"
    }
    typesense_client.client.collections['ossfinder'].documents.create(test_data)
    assert typesense_client.document_exists("123") is True
    assert typesense_client.document_exists("456") is False


def test_index_data(typesense_client):
    """Test data indexing"""
    test_data = [{
        "Id-repo": "123",
        "name": "Test Repo",
        "organisation": "Test Org",
        "description": "Test upload",
        "license": "MIT",
        "open_pull_requests": "3"
    }]

    typesense_client.index_data(test_data)
    doc = typesense_client.client.collections['ossfinder'].documents.retrieve("123")
    assert doc['name'] == "Test Repo"


def test_timeout_handling(typesense_client, monkeypatch):
    """Test timeout handling"""

    def mock_failing_operation(*args, **kwargs):
        raise ObjectNotFound("Simulated error")

    monkeypatch.setattr(
        typesense_client.client.collections['ossfinder'].documents,
        'retrieve',
        mock_failing_operation
    )

    with pytest.raises(TimeoutError):
        typesense_client.document_exists("123")