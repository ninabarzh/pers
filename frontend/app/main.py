from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import RedirectResponse, JSONResponse
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

# Home page (search)
async def home(request):
    query = request.query_params.get("q", "")
    results = None
    if query:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://backend:8000/search?q={query}")
            results = response.json()
    return templates.TemplateResponse("index.html", {"request": request, "results": results})

# Upload page
async def upload_page(request):
    return templates.TemplateResponse("upload.html", {"request": request})

# Handle upload
async def handle_upload(request):
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
                logger.error(f"Backend error: {response.text}")  # Log backend error
                return JSONResponse({"error": "Backend error"}, status_code=500)

        return RedirectResponse(url="/", status_code=303)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")  # Log JSON decode error
        return JSONResponse({"error": "Invalid JSON file"}, status_code=400)
    except Exception as e:
        logger.error(f"Error handling upload: {e}")  # Log any other error
        return JSONResponse({"error": str(e)}, status_code=500)

# Routes
routes = [
    Route("/", home, methods=["GET"]),
    Route("/upload", upload_page, methods=["GET"]),
    Route("/upload", handle_upload, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)