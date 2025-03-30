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
            self._initialize_client()
            self._initialized = True

    def _initialize_client(self):
        """Initialize Typesense client with proper environment variable handling"""
        is_production = os.getenv('ENV', 'development').lower() == 'production'

        # Use PROD_ variables in production, otherwise fall back to non-prefixed
        self.TYPESENSE_API_KEY = (
            os.getenv('PROD_TYPESENSE_API_KEY') if is_production
            else os.getenv('TYPESENSE_API_KEY')
        )

        self.TYPESENSE_HOST = (
            os.getenv('PROD_TYPESENSE_HOST') if is_production
            else os.getenv('TYPESENSE_HOST', 'typesense')
        )

        self.TYPESENSE_PORT = (
            os.getenv('PROD_TYPESENSE_PORT') if is_production
            else os.getenv('TYPESENSE_PORT', '8108')
        )

        self.TYPESENSE_PROTOCOL = (
            os.getenv('PROD_TYPESENSE_PROTOCOL') if is_production
            else os.getenv('TYPESENSE_PROTOCOL', 'http')
        )

        # Timeout handling (in seconds)
        self.TIMEOUT_SECONDS = float(os.getenv('TYPESENSE_TIMEOUT_SECONDS', '30'))

        if not self.TYPESENSE_API_KEY:
            env_type = "production" if is_production else "development"
            raise ValueError(f"TYPESENSE_API_KEY is missing for {env_type} environment")

        logger.info(f"Initializing Typesense client in {'production' if is_production else 'development'} mode with: "
                    f"Host: {self.TYPESENSE_HOST}:{self.TYPESENSE_PORT}, "
                    f"Protocol: {self.TYPESENSE_PROTOCOL}")

        self.client = typesense.Client({
            'api_key': self.TYPESENSE_API_KEY,
            'nodes': [{
                'host': self.TYPESENSE_HOST,
                'port': self.TYPESENSE_PORT,
                'protocol': self.TYPESENSE_PROTOCOL
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
        try:
            self._with_timeout(self._ensure_collection)
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise

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