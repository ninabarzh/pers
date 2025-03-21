# backend/src/app/main.py
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
import httpx
import os
import json
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Define the path to the static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")

# Home page (search)
async def home(request):
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))
    results = None
    error = None
    total_results = 0
    total_pages = 0

    if query:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://backend:8000/search?q={query}&page={page}&per_page={per_page}"
                )
                logger.debug(f"Backend response: {response.text}")  # Log the raw response
                if response.status_code == 200:
                    data = response.json()
                    logger.debug(f"Parsed data: {data}")  # Log the parsed data
                    results = data.get("hits", [])  # Use "hits" instead of "results"
                    total_results = data.get("found", 0)  # Use "found" instead of "total_results"
                    total_pages = (total_results + per_page - 1) // per_page
                else:
                    error = f"Backend error: {response.text}"
                    logger.error(error)
        except Exception as e:
            error = f"Failed to connect to the backend: {str(e)}"
            logger.error(error)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "query": query,
            "results": results,
            "error": error,
            "page": page,
            "per_page": per_page,
            "total_results": total_results,
            "total_pages": total_pages,
        },
    )


# Upload page
async def upload_page(request):
    return templates.TemplateResponse("upload.html", {"request": request})


# Handle upload
async def handle_upload(request):
    error = None  # Initialize `error` with a default value
    try:
        form_data = await request.form()
        file = form_data["json_file"].file.read()  # Read file as bytes
        logger.debug(f"Uploaded file content: {file}")  # Log the file content
        json_data = json.loads(file.decode("utf-8"))  # Decode bytes to string and parse as JSON
        logger.debug(f"Parsed JSON data: {json_data}")  # Log the parsed JSON data

        # Send JSON data to the backend
        async with httpx.AsyncClient() as client:
            response = await client.post("http://backend:8000/upload", json=json_data)
            if response.status_code != 200:
                error = f"Backend error: {response.text}"
                logger.error(error)  # Log backend error
                return templates.TemplateResponse(
                    "upload.html",
                    {"request": request, "error": error},
                )

        return RedirectResponse(url="/", status_code=303)
    except json.JSONDecodeError as e:
        error = "Invalid JSON file. Please upload a valid JSON file."
        logger.error(f"Invalid JSON file: {e}")
    except Exception as e:
        error = f"An error occurred: {str(e)}"
        logger.error(f"Error handling upload: {e}")

    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "error": error},
    )


# Routes
routes = [
    Route("/", home, methods=["GET"]),
    Route("/upload", upload_page, methods=["GET"]),
    Route("/upload", handle_upload, methods=["POST"]),
    Mount("/static", StaticFiles(directory=static_dir), name="static"),  # Serve static files
]

app = Starlette(debug=True, routes=routes)