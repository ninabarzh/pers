from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.requests import Request
from .typesense_client import TypesenseClient
import logging
import json

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Typesense client
typesense_client = TypesenseClient()

# Search endpoint
async def search(request: Request):
    query = request.query_params.get("q", "")
    results = typesense_client.search(query)
    return JSONResponse(results)


# Upload endpoint
async def upload(request: Request):
    try:
        # Parse JSON data from the request body
        body = await request.body()
        data = json.loads(body.decode("utf-8"))
        logger.debug(f"Received data: {data}")  # Log the received data

        # Ensure data is a list
        if not isinstance(data, list):
            return JSONResponse({"error": "Expected a list of documents"}, status_code=400)

        # Index the data
        typesense_client.index_data(data)
        return JSONResponse({"status": "success"})
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)


# Routes
routes = [
    Route("/search", search, methods=["GET"]),
    Route("/upload", upload, methods=["POST"]),
]


# Initialize Starlette app with routes
app = Starlette(debug=True, routes=routes)
