"""Hello API request/response models."""

from pydantic import BaseModel, Field, field_validator


class HelloRequest(BaseModel):
    """Hello request payload with validation."""

    name: str = Field(..., min_length=1, max_length=100, description="Name to greet")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name cannot be empty or whitespace only")
        return stripped


class HelloResponse(BaseModel):
    """Hello response schema."""

    message: str = Field(..., description="Greeting message")
