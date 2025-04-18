# backend/src/app/middleware/security.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired
import time
import os


class CORSMiddlewareNew(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request) if request.method != "OPTIONS" else Response()

        # Auto-configure allowed origins
        is_dev = os.getenv('DEBUG', 'false').lower() in ('true', '1', 't')
        origin = request.headers.get('origin')

        # Development: Allow common dev origins + local network
        if is_dev:
            dev_origins = [
                'http://localhost:8080',
                'http://127.0.0.1:8001',
                'http://localhost:8001',
                'http://0.0.0.0:8001',
                'http://backend:8000'  # Docker internal
            ]
            if origin in dev_origins or not origin:
                response.headers['Access-Control-Allow-Origin'] = origin or '*'

        # Production: Strict origin check
        else:
            prod_origins = [
                'https://finder.green',
                'https://www.finder.green',
                'http://backend:8000' # Direct backend access
            ]
            if origin in prod_origins:
                response.headers['Access-Control-Allow-Origin'] = origin

        # Common headers
        if 'Access-Control-Allow-Origin' in response.headers:
            response.headers.update({
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-CSRF-Token, Origin, X-CSRFToken',
                'Access-Control-Max-Age': '600'
            })

        return response


class CSRFMiddlewareNew(BaseHTTPMiddleware):
    def __init__(self, app, secret_key=None, cookie_name='csrftoken', safe_methods=None):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("CSRF_SECRET_KEY")
        self.cookie_name = cookie_name
        self.safe_methods = safe_methods or {'GET', 'HEAD', 'OPTIONS', 'TRACE'}
        self.serializer = URLSafeTimedSerializer(self.secret_key)

        if not self.secret_key:
            raise ValueError("CSRF_SECRET_KEY must be set in environment")

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF checks for development if DEBUG=True
        if os.getenv("DEBUG", "false").lower() in ('true', '1', 't'):
            response = await call_next(request)
            self._set_csrf_cookie(response)
            return response

        # Skip CSRF checks for safe methods
        if request.method in self.safe_methods:
            return await call_next(request)

        # Get tokens from header or form data
        csrf_token = (
                request.headers.get('X-CSRF-Token') or
                (await request.form()).get('csrf_token') or
                request.query_params.get('csrf_token')
        )
        cookie_token = request.cookies.get(self.cookie_name)

        if not csrf_token or not cookie_token:
            return Response('CSRF token missing', status_code=403)

        try:
            cookie_data = self.serializer.loads(cookie_token, max_age=3600)
            token_data = self.serializer.loads(csrf_token, max_age=3600)

            if cookie_data != token_data:
                raise ValueError("Tokens don't match")

        except (BadSignature, SignatureExpired, ValueError) as e:
            return Response(f'Invalid CSRF token: {str(e)}', status_code=403)

        response = await call_next(request)
        self._set_csrf_cookie(response)
        return response

    def _set_csrf_cookie(self, response):
        """Sets CSRF cookie with domain handling for prod/dev"""
        cookie_kwargs = {
            'key': self.cookie_name,
            'value': self.serializer.dumps(str(time.time())),
            'httponly': True,
            'samesite': 'lax',
            'secure': not os.getenv("DEBUG", "false").lower() in ('true', '1', 't'),
            'max_age': 3600
        }

        # Only set domain in production
        if not os.getenv("DEBUG", "false").lower() in ('true', '1', 't'):
            cookie_kwargs['domain'] = ".finder.green"

        response.set_cookie(**cookie_kwargs)
