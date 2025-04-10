# frontend/src/app/main.py
import logging
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.config import Config

# Relative route imports
from .routes.home import home
from .routes.admin import admin_dashboard, handle_admin_actions
from .routes.static_pages import about, contact, privacy, terms

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize config
config = Config()

def load_environment():
    """Load .env file from various locations"""
    paths = [
        Path("/app/.env"),  # Docker production
        Path(__file__).parent.parent.parent.parent / '.env',  # Development
        Path(__file__).parent / '.env'  # Alternative location
    ]
    for path in paths:
        if path.exists():
            load_dotenv(path)
            logger.info(f"Loaded .env from: {path}")
            return
    logger.warning("No .env file found")

# Initialize environment
load_environment()

# Configuration
app_config = {
    "PORT": config("FRONTEND_PORT", default=8001, cast=int),
    "DEBUG": config("DEBUG", default=False, cast=bool),
    "STATIC_DIR": "/var/www/static",
    "BACKEND_URL": config("BACKEND_URL", default="http://localhost:8080"),
    "FRIENDLY_CAPTCHA_SITE_KEY": config("FRIENDLY_CAPTCHA_SITE_KEY", default=""),
    "CSRF_SECRET_KEY": config("CSRF_SECRET_KEY", default="")
}

logger.info(f"Configuration loaded: {app_config}")

# Check production variables are set - KEEPING THIS IMPORTANT SECTION
if not app_config["DEBUG"]:
    required_vars = ['BACKEND_URL', 'FRIENDLY_CAPTCHA_SITE_KEY', 'CSRF_SECRET_KEY']
    missing = [var for var in required_vars if not app_config.get(var)]
    if missing:
        raise ValueError(f"Missing required production environment variables: {missing}")

# Create static directory if it doesn't exist - KEEPING THIS IMPORTANT SECTION
static_dir = Path(app_config["STATIC_DIR"])
try:
    static_dir.mkdir(exist_ok=True, parents=True)  # Added parents=True for nested directories
    logger.info(f"Static files directory: {static_dir}")
except Exception as e:
    logger.error(f"Failed to create static directory: {e}")
    raise  # Re-raise the exception to fail fast in production

# Application routes
routes = [
    Route("/", home, methods=["GET"]),
    Route("/health", lambda r: JSONResponse({"status": "healthy"})),
    Route("/admin", admin_dashboard, methods=["GET"]),
    Route("/admin", handle_admin_actions, methods=["POST"]),
    Route("/about", about, methods=["GET"]),
    Route("/contact", contact, methods=["GET"]),
    Route("/privacy", privacy, methods=["GET"]),
    Route("/terms", terms, methods=["GET"]),
    Mount("/static", StaticFiles(directory=app_config["STATIC_DIR"]), name="static"),
]

app = Starlette(
    debug=app_config["DEBUG"],
    routes=routes
)

# Proper way to set app state
app.state.config = app_config

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=app_config["PORT"],
        reload=app_config["DEBUG"],
        access_log=False
    )

