# frontend/src/app/main.py
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import os
from .routes.home import home
from .routes.upload import upload_page, handle_upload

# Define the path to the static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")


# Routes
routes = [
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
