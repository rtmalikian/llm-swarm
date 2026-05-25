import os
from typing import Dict

from fastapi import Header, HTTPException, status


def configured_api_key() -> str:
    """Return the optional shared API key used for swarm requests."""
    return os.getenv("SWARM_API_KEY", "").strip()


def auth_headers() -> Dict[str, str]:
    """Return Authorization headers for outgoing swarm requests when configured."""
    api_key = configured_api_key()
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


async def require_swarm_api_key(authorization: str = Header(default="")) -> None:
    """Require a bearer token only when SWARM_API_KEY is configured.

    Leaving SWARM_API_KEY unset preserves the prototype's unauthenticated local
    development behavior. Setting it enables a shared secret for tracker and
    node-to-node HTTP calls.
    """
    api_key = configured_api_key()
    if not api_key:
        return

    expected = f"Bearer {api_key}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid swarm API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
