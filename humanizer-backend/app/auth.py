import secrets

from fastapi import Header, HTTPException

from .config import ADMIN_API_KEY, ENV


def verify_admin(x_admin_key: str | None = Header(None), authorization: str | None = Header(None)) -> bool:
    """Dependency to verify admin access.

    Behavior:
    - If `ADMIN_API_KEY` is configured, require either `x-admin-key` header equal to it
      or `Authorization: Bearer <key>`.
    - If not configured, allow only when `ENV=='development'`.
    """
    if ADMIN_API_KEY:
        if x_admin_key is not None and secrets.compare_digest(x_admin_key, ADMIN_API_KEY):
            return True
        if authorization and authorization.lower().startswith("bearer "):
            parts = authorization.split(" ", 1)
            if len(parts) == 2 and secrets.compare_digest(parts[1], ADMIN_API_KEY):
                return True
        raise HTTPException(status_code=401, detail="unauthorized")

    # No admin key configured: only allow in development for convenience
    if ENV == "development":
        return True

    raise HTTPException(status_code=404, detail="not_found")
