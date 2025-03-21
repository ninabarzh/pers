# backend/src/app/routes/upload.py
import json
import logging
from starlette.responses import JSONResponse
from starlette.requests import Request
from ..typesense_client import TypesenseClient

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Typesense client
typesense_client = TypesenseClient()

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
