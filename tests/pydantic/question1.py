# Problem: Create Pydantic Models with Custom Validation for User Registration
# Approach: Use Pydantic v2 BaseModel with field_validator decorators.
# The validate_user function creates UserRegistration and handles ValidationError.
# Complexity: O(1) time and space for each validation check (constant time string operations).
# Steps:
# 1. Define the UserRegistration model with fields and their types.
# 2. Add field_validator decorators for each field to implement custom validation logic.
# 3. Implement the validate_user function to catch ValidationError and return appropriate tuple.

from pydantic import BaseModel, ValidationError, field_validator


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    age: int
    full_name: str

    # Validate username: 3-20 chars, alphanumeric + underscores, starts with letter
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not (3 <= len(v) <= 20):
            raise ValueError('Username must be between 3 and 20 characters')
        if not v[0].isalpha():
            raise ValueError('Username must start with a letter')
        if not all(c.isalnum() or c == '_' for c in v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v

    # Validate email: contains exactly one @, has domain with at least one . after @, no spaces
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if ' ' in v:
            raise ValueError('Email cannot contain spaces')
        if v.count('@') != 1:
            raise ValueError('Email must contain exactly one @')
        local, domain = v.split('@')
        if '.' not in domain:
            raise ValueError('Email domain must contain at least one .')
        return v

    # Validate password: min 8 chars, at least one uppercase, lowercase, digit, and special char
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        special_chars = '!@#$%^&*'
        if not any(c in special_chars for c in v):
            raise ValueError(f'Password must contain at least one special character from: {special_chars}')
        return v

    # Validate age: between 18 and 120 inclusive
    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if not (18 <= v <= 120):
            raise ValueError('Age must be between 18 and 120')
        return v

    # Validate full_name: non-empty after stripping whitespace, automatically strip
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        stripped = v.strip()
        if not stripped:
            raise ValueError('Full name cannot be empty')
        return stripped


def validate_user(data: dict) -> tuple[bool, str | object]:
    """Attempt to create a UserRegistration from the given dict.
    Returns (True, user_instance) on success, or (False, error_message) on failure.
    """
    try:
        user = UserRegistration(**data)
        return True, user
    except ValidationError as e:
        return False, str(e)
