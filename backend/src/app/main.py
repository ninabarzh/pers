# backend/src/app/main.py
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from .routes.search import search
from .routes.upload import upload
from dotenv import load_dotenv
import os

# Load .env.dev or .env.prod based on the ENV variable
env = os.getenv('ENV', 'development')
if env == 'production':
    load_dotenv('../.env.prod')
else:
    load_dotenv('../.env.dev')

# Access environment variables
TYPESENSE_API_KEY = os.getenv('TYPESENSE_API_KEY')
TYPESENSE_HOST = os.getenv('TYPESENSE_HOST')
TYPESENSE_PORT = os.getenv('TYPESENSE_PORT')
BACKEND_PORT = os.getenv('BACKEND_PORT')

# Health check endpoint
async def health_check(request):
    return JSONResponse({"status": "healthy"})

# Routes
routes = [
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
