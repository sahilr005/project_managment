from __future__ import annotations
import uuid, secrets
from datetime import timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models.user import User
from app.db.models.user_cred import UserCredential
from app.db.models.user_session import UserSession
from app.core.security import hash_password, verify_password, create_access_token, now_utc, hash_refresh

REFRESH_TTL_DAYS = 30

async def signup(*, session: AsyncSession, email: str, full_name: str | None, password: str) -> User:
    exists = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")
    u = User(email=email, full_name=full_name)
    session.add(u); await session.flush()
    cred = UserCredential(user_id=u.id, password_hash=hash_password(password))
    session.add(cred)
    await session.commit()
    return u

async def login(*, session: AsyncSession, email: str, password: str, user_agent: str | None, ip: str | None):
    u = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    cred = (await session.execute(select(UserCredential).where(UserCredential.user_id == u.id))).scalar_one_or_none()
    if not cred or not verify_password(password, cred.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create refresh (opaque random) and DB session
    refresh = secrets.token_urlsafe(48)
    rs = UserSession(
        user_id=u.id,
        refresh_token_hash=hash_refresh(refresh),
        user_agent=user_agent,
        ip=ip,
        expires_at=now_utc() + timedelta(days=REFRESH_TTL_DAYS),
    )
    session.add(rs); await session.commit()

    access = create_access_token(sub=str(u.id))
    return u, access, refresh

async def rotate_refresh(*, session: AsyncSession, refresh_token: str):
    from app.core.security import decode_token  # not needed for refresh (opaque), kept for reference

    h = hash_refresh(refresh_token)
    qs = select(UserSession).where(UserSession.refresh_token_hash == h, UserSession.revoked == False)  # noqa: E712
    srow = (await session.execute(qs)).scalar_one_or_none()
    if not srow or srow.expires_at <= now_utc():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = await session.get(User, srow.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    # rotate: revoke current, issue new
    srow.revoked = True
    import secrets
    new_refresh = secrets.token_urlsafe(48)
    from datetime import timedelta
    new_session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_refresh(new_refresh),
        user_agent=srow.user_agent,
        ip=srow.ip,
        expires_at=now_utc() + timedelta(days=REFRESH_TTL_DAYS),
    )
    session.add(new_session)
    access = create_access_token(sub=str(user.id))
    await session.commit()
    return user, access, new_refresh

async def revoke_session(*, session: AsyncSession, refresh_token: str):
    h = hash_refresh(refresh_token)
    qs = select(UserSession).where(UserSession.refresh_token_hash == h, UserSession.revoked == False)  # noqa: E712
    srow = (await session.execute(qs)).scalar_one_or_none()
    if not srow:
        return
    srow.revoked = True
    await session.commit()
