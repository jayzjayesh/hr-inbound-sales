"""
API key authentication dependency for FastAPI.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.config import get_settings

# HappyRobot will send the API key in this header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str = Security(api_key_header),
) -> str:
    """
    Validate the API key from the request header.
    Returns the key if valid, raises 401 otherwise.
    """
    settings = get_settings()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
        )

    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return api_key
