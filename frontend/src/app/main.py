# frontend/src/app/main.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent  # points to pers/
sys.path.insert(0, str(PROJECT_ROOT))

# Absolute imports
from frontend.src.app.routes.home import home
from frontend.src.app.routes.upload import upload_page, handle_upload

# Environment setup
load_dotenv(PROJECT_ROOT / '.env')

config = {
    "PORT": int(os.getenv('PROD_FRONTEND_PORT', 8001)),
    "DEBUG": os.getenv('DEBUG', 'false').lower() in ('true', '1', 't'),
    "STATIC_DIR": PROJECT_ROOT / "frontend" / "src" / "app" / "static"
}

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
        "frontend.src.app.main:app",
        host="0.0.0.0",
        port=config["PORT"],
        reload=config["DEBUG"]
    )
