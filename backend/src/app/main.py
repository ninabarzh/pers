# backend/src/app/main.py
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from .routes.search import search
from .routes.upload import upload

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
