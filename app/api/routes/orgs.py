from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.api.deps import db
from app.db.models.organization import Organization
from app.schemas.orgs import OrgCreate,OrgUpdate,OrgOut

router = APIRouter(prefix="/v1/organizations",tags=["organizations"])

@router.post("",response_model=OrgOut)
async def create_org(payload: OrgCreate, session: AsyncSession=Depends(db)):
    org= Organization(name=payload.name, domain=payload.domain)
    session.add(org)
    await session.commit()
    await session.refresh(org)
    return org

@router.get("",response_model=list[OrgOut])
async def list_orgs(
session: AsyncSession =Depends(db),
limit: int = Query(50, ge=1,le=200),
offset: int= Query(0,ge=0)
):
    q = select(Organization).order_by(Organization.created_at.desc()).limit(limit).offset(offset)
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.get("/{org_id}",response_model=OrgOut)
async def get_org(org_id:UUID, session: AsyncSession= Depends(db)):
    row = await session.get(Organization,org_id)
    if not row:
        raise HTTPException(status_code=404,detail="Organization not found")
    return row

@router.patch("/{org_id}",response_model=OrgOut)
async def update_org(org_id: UUID, payload: OrgUpdate, session: AsyncSession = Depends(db)):
    row = await session.get(Organization,org_id)
    if not row:
        raise HTTPException(status_code=404,detail="Organization not found")
    if payload.name is not None:
        row.name= payload.name
    if payload.domain is not None:
        row.domain = payload.domain
    await session.commit()
    await session.refresh(row)
    return row

@router.delete("/{org_id}",status_code=204)
async def delete_org(org_id:UUID, session: AsyncSession=Depends(db)):
    row = await session.get(Organization,org_id)
    if not row:
        raise HTTPException(status_code=404,detail="Organization not found")
    await session.delete(row)
    await session.commit()
    return None

