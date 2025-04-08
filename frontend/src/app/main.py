# frontend/src/app/main.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Relative route imports
from .routes.home import home
from .routes.admin import admin_dashboard, handle_admin_actions
from .routes.static_pages import about, contact, privacy, terms

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Environment setup
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


# Initialize environment
load_environment()

config = {
    "PORT": int(os.getenv('FRONTEND_PORT', 8001)),
    "DEBUG": os.getenv('DEBUG', 'false').lower() in ('true', '1', 't'),
    "STATIC_DIR": "/app/src/app/static",  # Absolute path in container
    "BACKEND_URL": os.getenv('BACKEND_URL', 'http://localhost:8000')  # New config
}

# Check production variables are set
if os.getenv('ENV') == 'production':
    required_vars = ['BACKEND_URL']  # Only require backend URL in production
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required production environment variables: {missing}")

# Create static directory if it doesn't exist
static_dir = Path(config["STATIC_DIR"])
try:
    static_dir.mkdir(exist_ok=True)
    logger.info(f"Static files directory: {static_dir}")
except Exception as e:
    logger.error(f"Failed to create static directory: {e}")

# Application routes
routes = [
    Route("/", home, methods=["GET"]),
    Route("/health", lambda r: JSONResponse({"status": "healthy"})),
    Route("/admin", admin_dashboard, methods=["GET"]),
    Route("/admin", handle_admin_actions, methods=["POST"]),
    # Static page routes
    Route("/about", about, methods=["GET"]),
    Route("/contact", contact, methods=["GET"]),
    Route("/privacy", privacy, methods=["GET"]),
    Route("/terms", terms, methods=["GET"]),
    Mount("/static", StaticFiles(directory=str(config["STATIC_DIR"])), name="static"),
]

app = Starlette(
    debug=config["DEBUG"],
    routes=routes
)

# Add the config to app state
app.state.config = config

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=config["PORT"],  # Use configured port
        reload=False,
        access_log=False
    )
