# backend/src/app/main.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware
from .typesense_client import get_typesense_client
from starlette.requests import Request

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Relative imports
from .routes.search import search
from .routes.upload import upload
from .routes.contact import contact_post

# Environment setup (original version)
def load_environment():
    """Conditionally loads .env file from either container path or project root"""
    # Try container path first (Docker production)
    container_env = Path("/app/.env")
    if container_env.exists():
        load_dotenv(container_env)
        logger.info(f"Loaded .env from container path: {container_env}")
        return

    # Try development path (4 levels up from src/app/)
    dev_env = Path(__file__).parent.parent.parent.parent / '.env'
    if dev_env.exists():
        load_dotenv(dev_env)
        logger.info(f"Loaded .env from development path: {dev_env}")
        return

    # Try adjacent .env (for alternative project structures)
    adjacent_env = Path(__file__).parent / '.env'
    if adjacent_env.exists():
        load_dotenv(adjacent_env)
        logger.info(f"Loaded .env from adjacent path: {adjacent_env}")
        return

    logger.warning("No .env file found in any standard location")

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
    "STATIC_DIR": str(Path(__file__).parent.parent / "static"),
    "CSRF_SECRET_KEY": os.getenv("CSRF_SECRET_KEY", "default-secret-change-me")
}

# Create static directory
static_dir = Path(config["STATIC_DIR"])
try:
    static_dir.mkdir(exist_ok=True)
    logger.info(f"Static files directory: {static_dir}")
except Exception as e:
    logger.error(f"Failed to create static directory: {e}")

async def health_check(request):
    """Enhanced health check endpoint"""
    try:
        client = get_typesense_client()
        health_data = client.health()

        if not health_data.get('ok'):
            logger.warning(f"Typesense health check failed: {health_data.get('error', 'Unknown error')}")

        return JSONResponse({
            "status": "healthy" if health_data.get('ok') else "degraded",
            "services": {
                "typesense": health_data,
                "api": True
            }
        }, status_code=200 if health_data.get('ok') else 503)

    except Exception as e:
        logger.error(f"Health check system error: {str(e)}")
        return JSONResponse(
            {"status": "unhealthy", "error": "Internal server error"},
            status_code=500
        )

async def root(request):
    return JSONResponse({
        "message": "Backend API",
        "endpoints": {
            "/": "GET - API documentation",
            "/health": "GET - Service health",
            "/debug-routes": "GET - List all routes",
            "/search": "GET - Search endpoint",
            "/upload": "POST - Upload endpoint",
            "/contact": "POST - Contact form",
            "/static": "GET - Static files"
        }
    })

# Base routes
base_routes = [
    Route("/", root),
    Route("/health", health_check, methods=["GET"]),
    Route("/search", search, methods=["GET"]),
    Route("/upload", upload, methods=["POST"]),
    Route("/contact", contact_post, methods=["POST"]),
]

# Static files
if static_dir.exists():
    base_routes.append(Mount("/static", StaticFiles(directory=static_dir)))

# Middleware
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8080",  # Development
            "https://finder.green"    # Production
        ],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
        expose_headers=["*"]
    ),
    Middleware(
        CSRFMiddleware,
        secret=config["CSRF_SECRET_KEY"],
        sensitive_cookies=["session"],
        safe_methods={"GET", "HEAD", "OPTIONS"}
    )
]

# Create app with base routes
app = Starlette(
    debug=config["DEBUG"],
    routes=base_routes,
    middleware=middleware
)

# Add request logging middleware HERE
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Add debug routes after app creation
app.router.routes.append(
    Route("/debug-routes", lambda _: JSONResponse({
        "routes": [
            {
                "path": route.path,
                "methods": sorted(list(getattr(route, "methods", ["GET"]))),  # Convert set to sorted list
                "name": getattr(route, "name", ""),
                "type": route.__class__.__name__
            }
            for route in app.routes
        ]
    }), name="debug_routes")
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