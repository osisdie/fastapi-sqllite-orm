"""Health check endpoints."""

from fastapi import APIRouter

from app import __version__
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check for load balancers and monitoring."""
    return HealthResponse(status="ok", version=__version__)
