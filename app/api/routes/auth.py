from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import db, current_user
from app.schemas.auth import SignupIn, LoginIn, TokenPair, RefreshIn, MeOut
from app.services import auth_service

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/signup", response_model=MeOut)
async def signup(payload: SignupIn, session: AsyncSession = Depends(db)):
    u = await auth_service.signup(session=session, email=payload.email, full_name=payload.full_name, password=payload.password)
    return MeOut(id=u.id, email=u.email, full_name=u.full_name)

@router.post("/login", response_model=TokenPair)
async def login(payload: LoginIn, request: Request, session: AsyncSession = Depends(db)):
    ua = request.headers.get("User-Agent")
    ip = request.client.host if request.client else None
    u, access, refresh = await auth_service.login(session=session, email=payload.email, password=payload.password, user_agent=ua, ip=ip)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshIn, session: AsyncSession = Depends(db)):
    u, access, refresh = await auth_service.rotate_refresh(session=session, refresh_token=payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/logout", response_model=dict)
async def logout(payload: RefreshIn, session: AsyncSession = Depends(db)):
    await auth_service.revoke_session(session=session, refresh_token=payload.refresh_token)
    return {"ok": True}

@router.get("/me", response_model=MeOut)
async def me(u = Depends(current_user)):
    return MeOut(id=u.id, email=u.email, full_name=u.full_name)
