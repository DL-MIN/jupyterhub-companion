"""
This module provides an authentication mechanism for FastAPI using an API key.
It checks the provided API key against a secret key stored in an environment variable.
If the keys do not match, it raises an HTTP 401 Unauthorized exception.
"""

import hmac
import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")
API_KEY = os.getenv("API_KEY", None)
if not API_KEY or len(API_KEY) < 16:
    raise ValueError("API_KEY environment variable not set or shorter than 16 characters")


def api_auth(key: str = Security(API_KEY_HEADER)) -> None:
    """
    Authenticate the API key provided in the request header.

    Args:
        key (str): The API key to authenticate.

    Raises:
        HTTPException: If the API key is invalid.
    """
    if not hmac.compare_digest(API_KEY, key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
