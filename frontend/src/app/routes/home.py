# frontend/src/app/routes/home.py
# from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import httpx
import os
import logging
from starlette.requests import Request

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

async def home(request: Request):
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
        request, "index.html",
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
