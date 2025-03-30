# backend/src/app/main.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Relative imports
from .routes.search import search
from .routes.upload import upload

# Environment setup
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    logger.warning(f"No .env file found at {env_path}")

config = {
    "PORT": int(os.getenv('PROD_BACKEND_PORT', 8000)),
    "DEBUG": os.getenv('DEBUG', 'false').lower() in ('true', '1', 't'),
    "TYPESENSE": {
        "API_KEY": os.getenv('PROD_TYPESENSE_API_KEY'),
        "HOST": os.getenv('PROD_TYPESENSE_HOST', 'typesense'),
        "PORT": os.getenv('PROD_TYPESENSE_PORT', '8108')
    },
    "STATIC_DIR": str(Path(__file__).parent.parent / "static")  # Relative to src/app
}

# Create static directory if it doesn't exist
static_dir = Path(config["STATIC_DIR"])
try:
    static_dir.mkdir(exist_ok=True)
    logger.info(f"Static files directory: {static_dir}")
except Exception as e:
    logger.error(f"Failed to create static directory: {e}")

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
]

# Only mount static files if directory exists
if static_dir.exists():
    routes.append(Mount("/static", StaticFiles(directory=str(static_dir)), name="static"))
else:
    logger.warning(f"Static directory not found at {static_dir}")

app = Starlette(
    debug=config["DEBUG"],
    routes=routes
)

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on port {config['PORT']}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config["PORT"],
        reload=config["DEBUG"]
    )
