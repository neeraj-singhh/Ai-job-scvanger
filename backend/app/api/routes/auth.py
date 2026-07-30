from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_dep
from app.schemas.auth import AuthUser, LoginRequest, SignupRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(payload: SignupRequest, db: AsyncSession = Depends(get_db_dep)) -> TokenResponse:
    return await AuthService(db).signup(payload)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db_dep)) -> TokenResponse:
    return await AuthService(db).login(payload)


@router.post("/logout", status_code=204)
async def logout(
    current_user: AuthUser = Depends(get_current_user), db: AsyncSession = Depends(get_db_dep)
) -> None:
    await AuthService(db).logout(access_token="")
