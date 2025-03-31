# backend/src/app/typesense_client.py
import typesense
from typesense.exceptions import ObjectNotFound, ServiceUnavailable, TypesenseClientError
from dotenv import load_dotenv
import time
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TypesenseClient:
    _instance = None
    client: Any
    TIMEOUT_SECONDS: float
    TYPESENSE_API_KEY: str
    TYPESENSE_HOST: str
    TYPESENSE_PORT: str
    TYPESENSE_PROTOCOL: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_config()
            try:
                self._initialize_client()
                self._initialized = True
            except Exception as e:
                logger.error(f"Typesense initialization failed: {str(e)}")
                self.client = None

    def _initialize_config(self):
        """Load configuration from environment"""
        env_path = Path('/app/.env')
        if env_path.exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path}")
        else:
            logger.warning(f"No .env file found at {env_path}")

        self.TIMEOUT_SECONDS = float(os.getenv('TYPESENSE_TIMEOUT_SECONDS', '30'))
        self.TYPESENSE_API_KEY = os.getenv('TYPESENSE_API_KEY', '')
        self.TYPESENSE_HOST = os.getenv('TYPESENSE_HOST', 'typesense')
        self.TYPESENSE_PORT = os.getenv('TYPESENSE_PORT', '8108')
        self.TYPESENSE_PROTOCOL = os.getenv('TYPESENSE_PROTOCOL', 'http')

        if not self.TYPESENSE_API_KEY:
            raise ValueError("TYPESENSE_API_KEY is required")

    def health(self):
        """Standard health check interface using correct API endpoint"""
        if not hasattr(self, 'client') or self.client is None:
            return {
                "ok": False,
                "error": "Client not initialized"
            }

        try:
            # Use the correct health check endpoint
            health_response = self.client.health.retrieve()
            return {
                "ok": True,
                "status": "operational",
                "version": health_response.get("version", "unknown"),
                "timestamp": health_response.get("timestamp", "")
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "status": "unavailable"
            }

    def _initialize_client(self):
        """Initialize the Typesense client with proper configuration"""
        self.client = typesense.Client({
            'api_key': self.TYPESENSE_API_KEY,
            'nodes': [{
                'host': self.TYPESENSE_HOST,
                'port': self.TYPESENSE_PORT,
                'protocol': self.TYPESENSE_PROTOCOL,
                'connection_timeout_seconds': int(self.TIMEOUT_SECONDS)
            }]
        })
        self.ensure_collection_exists()

    def _with_timeout(self, func, *args, **kwargs):
        """Wrapper to add timeout to operations"""
        start_time = time.time()
        last_exception = None

        while time.time() - start_time < self.TIMEOUT_SECONDS:
            try:
                return func(*args, **kwargs)
            except (ServiceUnavailable, TypesenseClientError) as e:
                last_exception = e
                time.sleep(1)
                continue

        raise TimeoutError(
            f"Operation timed out after {self.TIMEOUT_SECONDS} seconds"
        ) from last_exception

    def ensure_collection_exists(self):
        """Ensure collection exists with timeout handling"""
        if not self.client:
            return False

        try:
            return self._with_timeout(self._ensure_collection)
        except Exception as e:
            logger.error(f"Collection verification failed: {str(e)}")
            return False

    def _ensure_collection(self):
        """Actual collection existence check"""
        collection_name = "ossfinder"
        try:
            self.client.collections[collection_name].retrieve()
            logger.info(f"Collection '{collection_name}' exists")
            return
        except ObjectNotFound:
            schema = {
                "name": collection_name,
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
                ],
            }
            self.client.collections.create(schema)
            logger.info(f"Created collection '{collection_name}'")

    def search(self, query: str) -> Dict:
        """Search with timeout handling"""
        return self._with_timeout(
            self.client.collections['ossfinder'].documents.search,
            {
                'q': query,
                'query_by': 'name,description,organisation',
                'timeout_ms': int(self.TIMEOUT_SECONDS * 1000)
            }
        )

    def index_data(self, data: List[Dict]) -> None:
        """Index data with timeout handling"""
        return self._with_timeout(self._index_data_impl, data)

    def _index_data_impl(self, data: List[Dict]) -> None:
        """Actual data indexing implementation"""
        for document in data:
            try:
                if "open_pull_requests" in document and not isinstance(document["open_pull_requests"], str):
                    document["open_pull_requests"] = str(document["open_pull_requests"])

                document_id = document["Id-repo"]
                document["id"] = document_id

                if self.document_exists(document_id):
                    logger.debug(f"Document {document_id} exists, skipping")
                    continue

                self.client.collections['ossfinder'].documents.create(document)
                logger.info(f"Indexed document: {document_id}")
            except TypesenseClientError as e:
                logger.error(f"Error indexing document {document.get('Id-repo', 'unknown')}: {e}")

    def document_exists(self, document_id: str) -> bool:
        """Check if document exists with timeout handling"""
        return self._with_timeout(self._document_exists_impl, document_id)

    def _document_exists_impl(self, document_id: str) -> bool:
        """Actual document existence check"""
        try:
            self.client.collections['ossfinder'].documents[document_id].retrieve()
            return True
        except ObjectNotFound:
            return False

# Singleton instance
client_instance = TypesenseClient()

def get_typesense_client() -> TypesenseClient:
    """Get the shared Typesense client instance"""
    return client_instance