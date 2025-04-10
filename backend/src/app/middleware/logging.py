# backend/src/app/middleware/logging.py
import logging
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Initialize logger at module level
logger = logging.getLogger(__name__)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    Logs the incoming request method/path and response status code.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Log incoming request
        logger.info(
            "Request: %s %s",
            request.method,
            request.url.path,
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params)
            }
        )

        response = await call_next(request)

        # Log response
        logger.info(
            "Response: %d %s",
            response.status_code,
            request.url.path,
            extra={
                "status": response.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )

        return response