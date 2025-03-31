# frontend/src/app/main.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Relative imports
from .routes.home import home
from .routes.upload import upload_page, handle_upload

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Environment setup
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    logger.warning(f"No .env file found at {env_path}")

config = {
    "PORT": int(os.getenv('PROD_FRONTEND_PORT', 8001)),
    "DEBUG": os.getenv('DEBUG', 'false').lower() in ('true', '1', 't'),
    "STATIC_DIR": "/app/src/app/static"  # Absolute path in container
}

# Check production variables are set
if os.getenv('ENV') == 'production':
    required_vars = ['PROD_TYPESENSE_API_KEY', 'PROD_TYPESENSE_HOST']  # Add others as needed
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
    Route("/upload", upload_page, methods=["GET"]),
    Route("/upload", handle_upload, methods=["POST"]),
    Mount("/static", StaticFiles(directory=str(config["STATIC_DIR"])), name="static"),
]

app = Starlette(
    debug=config["DEBUG"],
    routes=routes
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        access_log = False
    )
