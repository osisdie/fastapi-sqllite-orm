"""Auth endpoints for token generation."""

from fastapi import APIRouter, Depends

from app.auth import create_access_token, get_current_user
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenRequest(BaseModel):
    """Token request payload."""

    username: str = Field(..., min_length=1, description="Username for token")


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
async def create_token(req: TokenRequest) -> TokenResponse:
    """Create JWT token for given username (demo: no password check)."""
    token = create_access_token(subject=req.username)
    return TokenResponse(access_token=token)


@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)) -> dict:
    """Return current authenticated user (requires Bearer token)."""
    return {"username": current_user}
