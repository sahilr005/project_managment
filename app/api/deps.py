from __future__ import annotations
from fastapi import Depends, Request, HTTPException,Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from uuid import UUID

async def db(request: Request) -> AsyncSession:
    # If an endpoint REQUIRES tenant scoping, you can enforce header presence here:
    # if "X-Org-Id" not in request.headers:
    #     raise HTTPException(status_code=400, detail="X-Org-Id header required")
   
    async with get_session(request) as s:
        yield s

def require_org_id(x_org_id: str = Header(..., alias="X-Org-Id")) -> UUID:
    org_id =x_org_id # request.headers.get("X-Org-Id")
    if not org_id:
        raise HTTPException(status_code=400, detail="X-Org-Id header required")
    try:
        return UUID(org_id)
    except Exception:
        raise HTTPException(status_code=400, detail="X-Org-Id must be a valid uuid")
