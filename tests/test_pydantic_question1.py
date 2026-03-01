"""Tests for Pydantic question1 UserRegistration validation (parametrize)."""

import pytest

from tests.pydantic.question1 import UserRegistration, validate_user


@pytest.mark.parametrize(
    "data,expect_success",
    [
        (
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "Pass123!",
                "age": 25,
                "full_name": "Alice Smith",
            },
            True,
        ),
        (
            {
                "username": "bob_123",
                "email": "bob@domain.co",
                "password": "Secure1@",
                "age": 30,
                "full_name": "Bob Jones",
            },
            True,
        ),
        ({"username": "ab", "email": "x@y.z", "password": "P1!", "age": 20, "full_name": "X"}, False),
        ({"username": "1invalid", "email": "x@y.z", "password": "P1!", "age": 20, "full_name": "X"}, False),
        ({"username": "ok", "email": "bad", "password": "P1!", "age": 20, "full_name": "X"}, False),
        ({"username": "ok", "email": "x@y.z", "password": "weak", "age": 20, "full_name": "X"}, False),
        ({"username": "ok", "email": "x@y.z", "password": "P1!", "age": 17, "full_name": "X"}, False),
        ({"username": "ok", "email": "x@y.z", "password": "P1!", "age": 20, "full_name": ""}, False),
    ],
)
def test_validate_user(data: dict, expect_success: bool) -> None:
    """validate_user returns (True, instance) or (False, error_message)."""
    ok, result = validate_user(data)
    assert ok == expect_success
    if expect_success:
        assert isinstance(result, UserRegistration)
    else:
        assert isinstance(result, str)
