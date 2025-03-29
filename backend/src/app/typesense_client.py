# backend/src/app/typesense_client.py
import typesense
from typesense.exceptions import ObjectNotFound, ServiceUnavailable, TypesenseClientError
from dotenv import load_dotenv
import time
import logging
import os

# Always load .env, production values will come from environment
load_dotenv('../.env')

# Load environment variables (fall back to non-prefixed versions for local development)
TYPESENSE_API_KEY = os.getenv('PROD_TYPESENSE_API_KEY') or os.getenv('TYPESENSE_API_KEY')
TYPESENSE_HOST = os.getenv('PROD_TYPESENSE_HOST') or os.getenv('TYPESENSE_HOST')
TYPESENSE_PORT = os.getenv('PROD_TYPESENSE_PORT') or os.getenv('TYPESENSE_PORT')
TYPESENSE_PROTOCOL = os.getenv('PROD_TYPESENSE_PROTOCOL') or os.getenv('TYPESENSE_PROTOCOL', 'http')  # Default to http

# Validate required environment variables
if not TYPESENSE_API_KEY:
    raise ValueError("TYPESENSE_API_KEY is missing. Check your .env files.")
if not TYPESENSE_HOST:
    raise ValueError("TYPESENSE_HOST is missing. Check your .env files.")
if not TYPESENSE_PORT:
    raise ValueError("TYPESENSE_PORT is missing. Check your .env files.")

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TypesenseClient:
    def __init__(self):
        """
        Initialize the Typesense client and ensure the collection exists.
        """
        self.client = typesense.Client({
            'api_key': TYPESENSE_API_KEY,
            'nodes': [{
                'host': TYPESENSE_HOST,
                'port': TYPESENSE_PORT,
                'protocol': TYPESENSE_PROTOCOL,
            }],
        })
        self.ensure_collection_exists()

    def ensure_collection_exists(self):
        """
        Ensure the ossfinder collection exists in Typesense. If it doesn't, create it with a predefined schema.
        Retry Mechanism: Retries up to 10 times with a 5-second delay between attempts if Typesense is unavailable.
        """
        collection_name = "ossfinder"
        retries = 10
        delay = 5

        for attempt in range(retries):
            try:
                self.client.collections[collection_name].retrieve()
                logger.info(f"Collection '{collection_name}' exists.")
                return
            except ObjectNotFound:
                # Create the collection if it doesn't exist
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
                        {"name": "open_pull_requests", "type": "string"},  # Changed to string
                        {"name": "master_branch", "type": "string"},
                        {"name": "is_fork", "type": "string"},
                        {"name": "forked_from", "type": "string"},
                    ],
                }
                self.client.collections.create(schema)
                logger.info(f"Collection '{collection_name}' created.")
                return
            except ServiceUnavailable as e:
                logger.warning(f"Typesense not ready. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
                if attempt == retries - 1:
                    logger.error(f"Failed to connect to Typesense after {retries} attempts.")
                    raise e

    def search(self, query: str):
        """
        Search the ossfinder collection for documents matching the provided query.
        Query Fields: The search is performed on the name, description, and organisation fields.
        """
        try:
            return self.client.collections['ossfinder'].documents.search({
                'q': query,
                'query_by': 'name,description,organisation',  # Specify fields to search
            })
        except TypesenseClientError as e:
            logger.error(f"Error searching for query '{query}': {e}")
            raise e

    def document_exists(self, document_id: str):
        """
        Check if a document with the specified document_id exists in the ossfinder collection.
        """
        try:
            self.client.collections['ossfinder'].documents[document_id].retrieve()
            return True
        except ObjectNotFound:
            return False
        except TypesenseClientError as e:
            logger.error(f"Error checking if document exists: {e}")
            raise e

    def index_data(self, data: list):
        """
        Index a list of documents into the ossfinder collection.
        Document ID: Uses Id-repo as the unique identifier for each document.
        Data Validation: Ensures open_pull_requests is a string.
        Error Handling: Logs errors for individual documents but continues processing the remaining documents.
        """
        for document in data:
            try:
                # Ensure `open_pull_requests` is a string
                if "open_pull_requests" in document and not isinstance(document["open_pull_requests"], str):
                    document["open_pull_requests"] = str(document["open_pull_requests"])

                # Use `Id-repo` as the document ID
                document_id = document["Id-repo"]
                document["id"] = document_id  # Set the primary key field

                # Check if the document already exists
                if self.document_exists(document_id):
                    logger.debug(f"Document with ID '{document_id}' already exists. Skipping.")
                    continue

                # Add the document to the collection
                self.client.collections['ossfinder'].documents.create(document)
                logger.info(f"Indexed document: {document}")
            except TypesenseClientError as e:
                logger.error(f"Error indexing document {document.get('Id-repo', 'unknown')}: {e}")
                # Continue processing other documents even if one fails
                continue
