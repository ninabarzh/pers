# backend/src/app/main.py
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from .routes.search import search
from .routes.upload import upload
from dotenv import load_dotenv
import os

# Always load .env, production values will come from environment
load_dotenv('../.env')

# Load environment variables (fall back to non-prefixed versions for local development)
TYPESENSE_API_KEY = os.getenv('PROD_TYPESENSE_API_KEY') or os.getenv('TYPESENSE_API_KEY')
TYPESENSE_HOST = os.getenv('PROD_TYPESENSE_HOST') or os.getenv('TYPESENSE_HOST')
TYPESENSE_PORT = os.getenv('PROD_TYPESENSE_PORT') or os.getenv('TYPESENSE_PORT')
BACKEND_PORT = os.getenv('PROD_BACKEND_PORT') or os.getenv('BACKEND_PORT')

# Health check endpoint
async def health_check(request):
    return JSONResponse({"status": "healthy"})

# Root endpoint
async def root(request):
    return JSONResponse({"message": "Backend API", "endpoints": {
        "/health": "GET - Health check",
        "/search": "GET - Search endpoint",
        "/upload": "POST - Upload endpoint"
    }})

# Routes
routes = [
    Route("/", root),
    Route("/health", health_check),
    Route("/search", search, methods=["GET"]),
    Route("/upload", upload, methods=["POST"]),
]


# Initialize Starlette app with routes
app = Starlette(debug=True, routes=routes)

# frontend/src/app/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
