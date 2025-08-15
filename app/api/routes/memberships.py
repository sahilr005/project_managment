from __future__ import annotations
from fastapi import APIRouter,Depends,HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,and_
from uuid import UUID
from app.api.deps import db, require_org_id
from app.db.models.membership import Membership
from app.db.models.user import User
from app.schemas.memberships import MembershipCreate,MembershipOut

router = APIRouter(prefix="/v1/memberships",tags=["memberships"])

@router.post("",response_model=MembershipOut)
async def add_member(
    payload: MembershipCreate,
    session:AsyncSession =Depends(db),
    org_id: UUID =Depends(require_org_id)
):
    u = await session.get(User,payload.user_id)
    if not u:
        raise HTTPException(status_code=404,detail="User not found")
    # to Avoid duplicates
    q= select(Membership).where(
        and_(Membership.org_id == org_id,
             Membership.user_id==payload.user_id)
    )
    exists = (await session.execute(q)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="User Already a Member")
    
    m = Membership(org_id=org_id, user_id=payload.user_id, role=payload.role)
    session.add(m)
    await session.commit()
    # Re-select to let RLS apply + return through model
    created = (await session.execute(q)).scalar_one()
    return created
    

@router.get("", response_model=list[MembershipOut])
async def list_members(
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = select(Membership).where(Membership.org_id == org_id).order_by(Membership.created_at.desc()).limit(limit).offset(offset)
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.delete("/{user_id}", status_code=204)
async def remove_member(
    user_id: UUID,
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
):
    q = select(Membership).where(
        (Membership.org_id == org_id) & (Membership.user_id == user_id)
    )
    row = (await session.execute(q)).scalar_one_or_none()
    if not row:
        # Either not a member OR RLS hid it; both are 404 to the caller
        raise HTTPException(status_code=404, detail="Membership not found")
    await session.delete(row)
    await session.commit()
    return None