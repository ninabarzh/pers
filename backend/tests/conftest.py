# backend/tests/conftest.py
import os
import pytest
from dotenv import load_dotenv
from pathlib import Path
from starlette.testclient import TestClient
from app.main import app
from app.typesense_client import TypesenseClient, set_testing_mode, get_typesense_client
from typesense.exceptions import ObjectNotFound, TypesenseClientError


# Load environment variables
# Try multiple possible .env locations
possible_env_locations = [
    Path(__file__).parent.parent / '.env',          # backend/.env (symlink)
    Path(__file__).parent.parent.parent / '.env',   # project_root/.env
    Path(__file__).parent.parent / 'backend' / '.env',
    Path('/app/.env')                               # Docker location
]

env_path = None
for location in possible_env_locations:
    if location.exists():
        env_path = location
        break

if env_path:
    load_dotenv(env_path)
    print(f"✓ Loaded .env from: {env_path}")
    print(f"✓ TYPESENSE_API_KEY exists: {'TYPESENSE_API_KEY' in os.environ}")
else:
    print("× No .env file found in any standard location")

# Verify critical variables
assert 'TYPESENSE_API_KEY' in os.environ, "TYPESENSE_API_KEY not found in environment"

# --------------------------
# Unit Test Fixtures (Mocked)
# --------------------------

TYPESENSE_COLLECTION_SCHEMA = {
    'fields': [
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


class MockCollection:
    def __init__(self, name):
        self.name = name
        self.documents = {}

    def create(self, document):
        doc_id = document["Id-repo"]
        self.documents[doc_id] = document
        return document

    def __getitem__(self, key):
        if key not in self.documents:
            raise ObjectNotFound(f"Document {key} not found")
        return self.documents[key]

    def delete(self, document_id):
        if document_id not in self.documents:
            raise ObjectNotFound(f"Document {document_id} not found")
        del self.documents[document_id]


class MockTypesenseClient:
    def __init__(self):
        self.collections = {}
        self.health_status = {"ok": True}

    def __getitem__(self, name):
        if name not in self.collections:
            raise ObjectNotFound(f"Collection {name} not found")
        return self.collections[name]

    def create(self, schema):
        name = schema['name']
        self.collections[name] = MockCollection(name)
        return schema

    def search(self, params):
        # Handle both string query and dictionary params
        if isinstance(params, str):
            query = params.lower()
        else:
            query = params.get('q', '').lower()

        hits = []
        for collection in self.collections.values():
            for doc_id, doc in collection.documents.items():
                if query in doc.get('name', '').lower():
                    hits.append({
                        'document': doc,
                        'highlight': {},
                        'text_match': 12345
                    })
        return {
            'facet_counts': [],
            'found': len(hits),
            'hits': hits,
            'out_of': len(hits),
            'page': 1,
            'search_time_ms': 1
        }

    def health(self):
        return self.health_status


@pytest.fixture
def mock_typesense():
    """Fixture for a mocked Typesense instance"""
    mock = MockTypesenseClient()
    mock.create({
        'name': 'ossfinder',
        'fields': TYPESENSE_COLLECTION_SCHEMA['fields'].copy()
    })
    return mock


@pytest.fixture
def unit_typesense_client(monkeypatch, mock_typesense):
    """Fixture for unit tests with mocked Typesense"""
    set_testing_mode(True)
    client = TypesenseClient()
    monkeypatch.setattr(client, 'client', mock_typesense)
    yield client
    set_testing_mode(False)


@pytest.fixture
def unit_client(monkeypatch, mock_typesense):
    """TestClient fixture for unit tests"""
    # Patch all possible client access points
    monkeypatch.setattr('app.typesense_client.get_typesense_client', lambda: mock_typesense)
    monkeypatch.setattr('app.routes.search.typesense_client', mock_typesense)
    monkeypatch.setattr('app.main.get_typesense_client', lambda: mock_typesense)

    # Ensure testing mode is enabled
    set_testing_mode(True)

    with TestClient(app) as client:
        yield client

    set_testing_mode(False)


# --------------------------
# Integration Test Fixtures
# --------------------------

@pytest.fixture(scope="module")
def integration_typesense_client():
    """Verified Typesense connection with debug output and cleanup"""
    # 1. Environment Verification
    if not os.getenv('TYPESENSE_API_KEY'):
        pytest.skip("TYPESENSE_API_KEY environment variable required")

    # 2. Debug Output
    print("\n=== Typesense Connection ===")
    print(f"Host: {os.getenv('TYPESENSE_HOST', 'typesense')}:{os.getenv('TYPESENSE_PORT', '8108')}")
    print(f"API Key: {'****' + os.getenv('TYPESENSE_API_KEY')[-4:]}")  # Masked output

    # 3. Client Initialization
    set_testing_mode(False)
    client = TypesenseClient()

    # 4. Connection Test
    try:
        health = client.health()
        print(f"Health Status: {health}")
        if not health.get('ok'):
            pytest.skip(f"Service unavailable: {health}")
    except Exception as e:
        pytest.skip(f"Connection failed: {str(e)}")

    yield client

    # 5. Cleanup (improved version)
    try:
        client.client.collections['ossfinder'].documents.delete({
            'filter_by': 'id: test_*'
        })
    except Exception as e:
        print(f"Cleanup note: {str(e)}")  # Non-fatal


@pytest.fixture
def integration_client(integration_typesense_client):
    """TestClient fixture for integration tests"""
    with TestClient(app) as client:
        yield client
