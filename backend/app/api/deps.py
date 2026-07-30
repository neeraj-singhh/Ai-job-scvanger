"""Shared FastAPI dependencies."""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.auth import AuthUser
from app.services.auth_service import decode_supabase_jwt

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthUser:
    """Decode and verify the Supabase JWT from the Authorization header."""
    return decode_supabase_jwt(credentials.credentials)


# Re-exported for convenience so routers only need one import line.
DbSession = AsyncSession
get_db_dep = get_db
