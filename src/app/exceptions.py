"""Application exceptions and global exception handler."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from pydantic import ValidationError


class AppError(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class UnauthorizedError(AppError):
    """Unauthorized access (401)."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    """Forbidden access (403)."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundError(AppError):
    """Resource not found (404)."""

    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        errors = exc.errors()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": [{"loc": e["loc"], "msg": e["msg"]} for e in errors],
            },
        )

    @app.exception_handler(AppError)
    async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
