# backend/src/app/main.py
import os
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Relative imports (recommended)
from .routes.search import search
from .routes.upload import upload

# Environment setup - use absolute path in container
load_dotenv('/app/.env')  # Updated path for Docker

config = {
    "PORT": int(os.getenv('PROD_BACKEND_PORT', 8000)),
    "DEBUG": os.getenv('DEBUG', 'false').lower() in ('true', '1', 't'),
    "TYPESENSE": {
        "API_KEY": os.getenv('PROD_TYPESENSE_API_KEY'),
        "HOST": os.getenv('PROD_TYPESENSE_HOST', 'typesense'),
        "PORT": os.getenv('PROD_TYPESENSE_PORT', '8108')
    },
    "STATIC_DIR": "/app/static"
}


# Application endpoints
async def health_check(request):
    return JSONResponse({"status": "healthy"})


async def root(request):
    return JSONResponse({
        "message": "Backend API",
        "endpoints": {
            "/": "GET - API documentation",
            "/health": "GET - Service health",
            "/search": "GET - Search endpoint",
            "/upload": "POST - Upload endpoint",
            "/static": "GET - Static files"
        }
    })

routes = [
    Route("/", root),
    Route("/health", health_check),
    Route("/search", search, methods=["GET"]),
    Route("/upload", upload, methods=["POST"]),
    Mount("/static", StaticFiles(directory=config["STATIC_DIR"]), name="static"),
]

app = Starlette(
    debug=config["DEBUG"],
    routes=routes
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",  # Updated import path
        host="0.0.0.0",
        port=config["PORT"],
        reload=config["DEBUG"]
    )
