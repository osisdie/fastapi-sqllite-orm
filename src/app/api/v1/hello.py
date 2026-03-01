"""Hello API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth import get_current_user_optional
from app.models.hello import HelloRequest, HelloResponse

router = APIRouter(tags=["hello"])


@router.get("/hello", response_model=HelloResponse)
async def hello_get(
    current_user: Annotated[str | None, Depends(get_current_user_optional)] = None,
) -> HelloResponse:
    """Simple GET hello (no auth required)."""
    name = current_user or "World"
    return HelloResponse(message=f"Hello, {name}!")


@router.post("/hello", response_model=HelloResponse)
async def hello_post(
    body: HelloRequest,
    current_user: Annotated[str | None, Depends(get_current_user_optional)] = None,
) -> HelloResponse:
    """POST hello with Pydantic-validated body."""
    name = body.name
    if current_user:
        return HelloResponse(message=f"Hello, {name}! (authenticated as {current_user})")
    return HelloResponse(message=f"Hello, {name}!")
