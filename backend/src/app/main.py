# backend/src/app/main.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Relative routes
from .middleware.security import CORSMiddlewareNew, CSRFMiddlewareNew
from .middleware.logging import RequestLoggerMiddleware
from .typesense_client import get_typesense_client
from .routes.search import search
from .routes.upload import upload
from .routes.contact import contact_post

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Environment setup
def load_environment():
    paths = [
        Path("/app/.env"),  # Docker production
        Path(__file__).parent.parent.parent.parent / '.env',
        Path(__file__).parent / '.env'
    ]
    for path in paths:
        if path.exists():
            load_dotenv(path)
            logger.info(f"Loaded .env from: {path}")
            return
    logger.warning("No .env file found")

load_environment()

config = {
    "PORT": int(os.getenv('BACKEND_PORT', 8000)),
    "DEBUG": os.getenv('DEBUG', 'false').lower() in ('true', '1', 't'),
    "TYPESENSE": {
        "API_KEY": os.getenv('TYPESENSE_API_KEY'),
        "HOST": os.getenv('TYPESENSE_HOST', 'typesense'),
        "PORT": os.getenv('TYPESENSE_PORT', '8108'),
        "PROTOCOL": os.getenv('TYPESENSE_PROTOCOL', 'http')
    },
    "STATIC_DIR": str(Path(__file__).parent.parent / "static")
}

# Create static directory
static_dir = Path(config["STATIC_DIR"])
static_dir.mkdir(exist_ok=True)

async def health_check(request):
    try:
        client = get_typesense_client()
        health_data = client.health()
        return JSONResponse({
            "status": "healthy" if health_data.get('ok') else "degraded",
            "services": {
                "typesense": health_data,
                "api": True
            }
        }, status_code=200 if health_data.get('ok') else 503)
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JSONResponse({"status": "unhealthy"}, status_code=500)

async def root(request):
    return JSONResponse({
        "message": "Backend API",
        "endpoints": {
            "/": "GET - API documentation",
            "/health": "GET - Service health",
            "/search": "GET - Search endpoint",
            "/upload": "POST - Upload endpoint",
            "/contact": "POST - Contact form",
            "/static": "GET - Static files"
        }
    })

routes = [
    Route("/", root),
    Route("/health", health_check, methods=["GET"]),
    Route("/search", search, methods=["GET"]),
    Route("/upload", upload, methods=["POST"]),
    Route("/contact", contact_post, methods=["POST"]),
]

if static_dir.exists():
    routes.append(Mount("/static", StaticFiles(directory=static_dir)))

app = Starlette(
    debug=config["DEBUG"],
    routes=routes,
)

app.add_middleware(CORSMiddlewareNew)
app.add_middleware(CSRFMiddlewareNew)
app.add_middleware(RequestLoggerMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config["PORT"],
        reload=config["DEBUG"]
    )
