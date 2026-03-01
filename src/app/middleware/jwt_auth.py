"""JWT token validation middleware for non-healthcheck API."""

import re

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.auth import verify_token

# Paths that skip JWT validation (regex, matched against path)
JWT_EXEMPT_PATTERNS = [
    r"^/api/v1/health$",
    r"^/docs",
    r"^/redoc",
    r"^/openapi\.json$",
    r"^/api/v1/auth/token$",
]


def _is_exempt(path: str) -> bool:
    """Check if path is exempt from JWT validation."""
    for pattern in JWT_EXEMPT_PATTERNS:
        if re.match(pattern, path):
            return True
    return False


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Validate JWT on non-exempt API paths."""

    async def dispatch(self, request: Request, call_next):
        if _is_exempt(request.url.path):
            return await call_next(request)

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth[7:]
        sub = verify_token(token)
        if sub is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user = sub
        return await call_next(request)
