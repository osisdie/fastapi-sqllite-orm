"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.v1 import auth, cache_crud, health, hello, raw_sql_crud, sql_crud
from app.config import get_settings
from app.db.base import Base
from app.db.session import _engine
from app.exceptions import register_exception_handlers
from app.middleware.jwt_auth import JWTAuthMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Ensure models are registered before create_all
    from app.db.models import Category, Item  # noqa: F401 - register ORM models

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="FastAPI project with Pydantic validation, JWT auth, and Swagger",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(JWTAuthMiddleware)

    register_exception_handlers(app)

    # API versioning: /api/v1/...
    v1 = APIRouter(prefix="/api/v1")
    v1.include_router(health.router)
    v1.include_router(hello.router)
    v1.include_router(auth.router)
    v1.include_router(sql_crud.router)
    v1.include_router(raw_sql_crud.router)
    v1.include_router(cache_crud.router)
    app.include_router(v1)

    return app


app = create_app()


def run() -> None:
    """Run uvicorn server (used by pyproject script and launch.json)."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
