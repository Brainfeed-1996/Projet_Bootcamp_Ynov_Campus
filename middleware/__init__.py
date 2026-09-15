import uuid

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: StarletteRequest, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": f"Request body too large. Maximum size is {self.max_size} bytes."},
                    )
            except ValueError:
                pass

        body = b""
        async for chunk in request.stream():
            body += chunk
            if len(body) > self.max_size:
                return JSONResponse(
                    status_code=413,
                    content={"detail": f"Request body too large. Maximum size is {self.max_size} bytes."},
                )

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive
        return await call_next(request)


SWAGGER_UI_SCRIPT_HASH = "sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY="
SWAGGER_UI_CDN = "https://cdn.jsdelivr.net"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if request.url.path == "/docs" or request.url.path.startswith("/docs/"):
            csp = (
                "default-src 'self'; "
                f"script-src 'self' {SWAGGER_UI_CDN} {SWAGGER_UI_SCRIPT_HASH}; "
                f"style-src 'self' 'unsafe-inline' {SWAGGER_UI_CDN}; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                f"font-src 'self' {SWAGGER_UI_CDN}; connect-src 'self'"
            )
        else:
            csp = (
                "default-src 'self'; script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                "font-src 'self'; connect-src 'self'"
            )

        response.headers["Content-Security-Policy"] = csp
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            accept = request.headers.get("accept", "")
            is_browser = "text/html" in accept
            if not is_browser:
                return await call_next(request)
            token = request.headers.get('X-CSRF-Token')
            if not token:
                return JSONResponse(status_code=403, content={'detail': 'CSRF token missing'})
        return await call_next(request)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response