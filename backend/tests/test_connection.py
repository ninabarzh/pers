# backend/tests/test_connection.py

def test_typesense_connection(integration_typesense_client):
    """Verify basic Typesense operations"""
    # Test collection exists
    collections = integration_typesense_client.client.collections.retrieve()
    assert any(c['name'] == 'ossfinder' for c in collections), "Collection missing"

    # Test search works
    results = integration_typesense_client.search("test")
    assert isinstance(results, dict)
    assert 'hits' in results