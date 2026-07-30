"""
Auth service.

Identity (signup/login/password hashing/JWT issuance) is delegated
entirely to Supabase Auth — we never touch raw passwords ourselves.
This service is a thin wrapper around the Supabase client plus the
logic to mirror a new auth user into our `profiles` table.
"""
from __future__ import annotations

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client, create_client

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError, ValidationAppError
from app.core.logging import get_logger
from app.models.profile import Profile
from app.schemas.auth import AuthUser, LoginRequest, SignupRequest, TokenResponse

logger = get_logger(__name__)


def get_supabase_client(settings: Settings | None = None) -> Client:
    settings = settings or get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


class AuthService:
    def __init__(self, db: AsyncSession, settings: Settings | None = None):
        self.db = db
        self.settings = settings or get_settings()
        self.supabase = get_supabase_client(self.settings)

    async def signup(self, payload: SignupRequest) -> TokenResponse:
        result = self.supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {"data": {"full_name": payload.full_name}},
            }
        )
        if result.user is None:
            raise ValidationAppError("Signup failed. The email may already be registered.")

        # Mirror into our profiles table so the rest of the app has a
        # first-class row to attach preferences/jobs/matches to.
        existing = await self.db.execute(select(Profile).where(Profile.id == result.user.id))
        if existing.scalar_one_or_none() is None:
            self.db.add(
                Profile(id=result.user.id, email=payload.email, full_name=payload.full_name)
            )
            await self.db.commit()

        session = result.session
        return TokenResponse(
            access_token=session.access_token if session else "",
            refresh_token=session.refresh_token if session else None,
            expires_in=session.expires_in if session else None,
        )

    async def login(self, payload: LoginRequest) -> TokenResponse:
        try:
            result = self.supabase.auth.sign_in_with_password(
                {"email": payload.email, "password": payload.password}
            )
        except Exception as exc:  # noqa: BLE001
            raise UnauthorizedError("Invalid email or password") from exc

        if result.session is None:
            raise UnauthorizedError("Invalid email or password")

        return TokenResponse(
            access_token=result.session.access_token,
            refresh_token=result.session.refresh_token,
            expires_in=result.session.expires_in,
        )

    async def logout(self, access_token: str) -> None:
        try:
            self.supabase.auth.sign_out()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Logout call failed (non-fatal): %s", exc)


def decode_supabase_jwt(token: str, settings: Settings | None = None) -> AuthUser:
    """
    Verify and decode a Supabase-issued JWT (sent by the desktop client
    on every authenticated request). Raises UnauthorizedError if invalid.
    """
    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    return AuthUser(id=payload["sub"], email=payload["email"])
