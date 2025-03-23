# frontend/src/app/main.py
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse
import os
from .routes.home import home
from .routes.upload import upload_page, handle_upload
from dotenv import load_dotenv
import os

# Load .env.dev or .env.prod based on the ENV variable
env = os.getenv('ENV', 'development')
if env == 'production':
    load_dotenv('../.env.prod')
else:
    load_dotenv('../.env.dev')

# Access environment variables
FRONTEND_PORT = os.getenv('FRONTEND_PORT')

# Define the path to the static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")


# Health check endpoint
async def health_check(request):
    return JSONResponse({"status": "healthy"})

# Routes
routes = [
    Route("/health", health_check),
    Route("/", home, methods=["GET"]),
    Route("/upload", upload_page, methods=["GET"]),
    Route("/upload", handle_upload, methods=["POST"]),
    Mount("/static", StaticFiles(directory=static_dir), name="static"),  # Serve static files
]

app = Starlette(debug=True, routes=routes)

# frontend/src/app/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
