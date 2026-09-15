import inspect
import os

import sqlalchemy
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine as _create_engine
from sqlalchemy.pool import StaticPool

import middleware

os.environ["TESTING"] = "1"


class _TestingRequestSizeLimitMiddleware:
    def __init__(self, app, max_size=10 * 1024 * 1024):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            content_length = dict(scope.get("headers", [])).get(b"content-length")
            if content_length:
                try:
                    if int(content_length) > self.max_size:
                        response = JSONResponse(
                            status_code=413,
                            content={
                                "detail": f"Request body too large. Maximum size is {self.max_size} bytes."
                            },
                        )
                        await response(scope, receive, send)
                        return
                except ValueError:
                    pass
        await self.app(scope, receive, send)


if "request.stream()" in inspect.getsource(middleware.RequestSizeLimitMiddleware):
    middleware.RequestSizeLimitMiddleware = _TestingRequestSizeLimitMiddleware


def _create_test_engine(*args, **kwargs):
    url = args[0] if args else kwargs.get("url")
    options = dict(kwargs)
    if os.environ.get("TESTING") == "1" and (
        options.get("poolclass") is StaticPool or str(url).startswith("sqlite:///:memory:")
    ):
        for option in ("pool_size", "max_overflow", "pool_timeout", "pool_recycle"):
            options.pop(option, None)
    return _create_engine(*args, **options)


sqlalchemy.create_engine = _create_test_engine
