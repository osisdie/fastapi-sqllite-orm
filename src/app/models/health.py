"""Health check response model."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
