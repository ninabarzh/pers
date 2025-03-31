# backend/src/app/typesense_client.py
import typesense
from typesense.exceptions import ObjectNotFound, ServiceUnavailable, TypesenseClientError
from dotenv import load_dotenv
import time
import logging
import os
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TypesenseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            # Load environment variables when first creating the instance
            env_path = Path(__file__).resolve().parent.parent.parent / '.env'
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"Loaded environment variables from {env_path}")
            else:
                logger.warning(f"No .env file found at {env_path}")
        return cls._instance


    def __init__(self):
        if not self._initialized:
            try:
                self._initialize_client()
                self._initialized = True
            except Exception as e:
                logger.error(f"Typesense initialization failed: {str(e)}")
                self.client = None  # Mark as uninitialized but allow app to start


    def health(self):
        """Standard health check interface"""
        if not hasattr(self, 'client') or self.client is None:
            return {
                "ok": False,
                "error": "Client not initialized"
            }

        try:
            metrics = self.client.operations.metrics.retrieve()
            return {
                "ok": metrics.get("ok", False),
                "status": "operational",
                "version": metrics.get("version", "unknown"),
                "timestamp": metrics.get("timestamp", "")
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "status": "unavailable"
            }


    def _initialize_client(self):
        """Simplified initialization that works with Docker env variables"""
        self.TYPESENSE_API_KEY = os.getenv('TYPESENSE_API_KEY')
        self.TYPESENSE_HOST = os.getenv('TYPESENSE_HOST', 'typesense')
        self.TYPESENSE_PORT = os.getenv('TYPESENSE_PORT', '8108')
        self.TYPESENSE_PROTOCOL = os.getenv('TYPESENSE_PROTOCOL', 'http')
        self.TIMEOUT_SECONDS = float(os.getenv('TYPESENSE_TIMEOUT_SECONDS', '30'))

        if not self.TYPESENSE_API_KEY:
            raise ValueError("TYPESENSE_API_KEY is required")

        logger.info(f"Initializing Typesense client with: {self.TYPESENSE_HOST}:{self.TYPESENSE_PORT}")

        self.client = typesense.Client({
            'api_key': self.TYPESENSE_API_KEY,
            'nodes': [{
                'host': self.TYPESENSE_HOST,
                'port': self.TYPESENSE_PORT,
                'protocol': self.TYPESENSE_PROTOCOL,
                'connection_timeout_seconds': self.TIMEOUT_SECONDS
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
                time.sleep(1)  # Wait before retrying
                continue

        raise TimeoutError(
            f"Operation timed out after {self.TIMEOUT_SECONDS} seconds"
        ) from last_exception


    def ensure_collection_exists(self):
        """Ensure collection exists with timeout handling"""
        """More resilient collection setup"""
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


    def search(self, query: str):
        """Search with timeout handling"""
        return self._with_timeout(
            self.client.collections['ossfinder'].documents.search,
            {
                'q': query,
                'query_by': 'name,description,organisation',
                'timeout_ms': int(self.TIMEOUT_SECONDS * 1000)  # Convert to milliseconds
            }
        )

    def index_data(self, data: list):
        """Index data with timeout handling"""
        return self._with_timeout(self._index_data_impl, data)


    def _index_data_impl(self, data: list):
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
                continue


    def document_exists(self, document_id: str):
        """Check if document exists with timeout handling"""
        return self._with_timeout(self._document_exists_impl, document_id)


    def _document_exists_impl(self, document_id: str):
        """Actual document existence check"""
        try:
            self.client.collections['ossfinder'].documents[document_id].retrieve()
            return True
        except ObjectNotFound:
            return False

# Singleton instance - must be after class definition
client_instance = TypesenseClient()

def get_typesense_client():
    """Get the shared Typesense client instance"""
    return client_instance