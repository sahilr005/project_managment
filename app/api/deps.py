from __future__ import annotations
from fastapi import Depends, Request, HTTPException,Header
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from app.core.security import decode_token
from app.db.models.user import User
from app.db.models.membership import Membership
from app.db.session import get_session
from uuid import UUID

http_bearer = HTTPBearer(auto_error=False)

async def db(request: Request) -> AsyncSession:
    # If an endpoint REQUIRES tenant scoping, you can enforce header presence here:
    # if "X-Org-Id" not in request.headers:
    #     raise HTTPException(status_code=400, detail="X-Org-Id header required")
   
    async with get_session(request) as s:
        yield s

def require_org_id(x_org_id: str = Header(..., alias="X-Org-Id")) -> UUID:
    org_id =x_org_id 
    # org_id = request.headers.get("X-Org-Id")
    if not org_id:
        raise HTTPException(status_code=400, detail="X-Org-Id header required")
    try:
        return UUID(org_id)
    except Exception:
        raise HTTPException(status_code=400, detail="X-Org-Id must be a valid uuid")


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    session: AsyncSession = Depends(db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    u = await session.get(User, UUID(user_id))
    if not u or not u.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return u

def require_role(*roles: str):
    async def _inner(
        user: User = Depends(current_user),
        org_id: UUID = Depends(require_org_id),
        session: AsyncSession = Depends(db),
    ):
        q = select(Membership).where(and_(Membership.org_id==org_id, Membership.user_id==user.id))
        m = (await session.execute(q)).scalar_one_or_none()
        role = m.role if m else "guest"
        if roles and role not in roles:
            raise HTTPException(status_code=403, detail="forbidden")
        return user
    return _inner
