import typesense
from typesense.exceptions import ObjectNotFound, ServiceUnavailable
import time
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TypesenseClient:
    def __init__(self):
        self.client = typesense.Client({
            'api_key': 'xyz',
            'nodes': [{
                'host': 'typesense',  # Docker service name
                'port': '8108',
                'protocol': 'http',
            }],
        })
        self.ensure_collection_exists()

    def ensure_collection_exists(self):
        collection_name = "ossfinder"
        retries = 10  # Increase retries
        delay = 5  # Increase delay

        for attempt in range(retries):
            try:
                self.client.collections[collection_name].retrieve()
                logger.debug(f"Collection '{collection_name}' exists.")
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
                logger.debug(f"Collection '{collection_name}' created.")
                return
            except ServiceUnavailable as e:
                logger.warning(f"Typesense not ready. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
                if attempt == retries - 1:
                    raise e


    def search(self, query: str):
        return self.client.collections['ossfinder'].documents.search({
            'q': query,
            'query_by': 'name,description,organisation',  # Specify fields to search
        })


    def document_exists(self, document_id: str):
        try:
            # Try to retrieve the document by its unique identifier (e.g., Id-repo)
            self.client.collections['ossfinder'].documents[document_id].retrieve()
            return True
        except ObjectNotFound:
            return False
        except Exception as e:
            logger.error(f"Error checking if document exists: {e}")
            raise e

    def index_data(self, data: list):
        # Index each document individually
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
                logger.debug(f"Indexed document: {document}")
            except Exception as e:
                logger.error(f"Error indexing document {document.get('Id-repo', 'unknown')}: {e}")
                # Continue processing other documents even if one fails
                continue
