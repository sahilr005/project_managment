from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from app.api.deps import db, require_org_id
from app.db.models.project import Project
from app.schemas.projects import ProjectCreate, ProjectUpdate, ProjectOut

router = APIRouter(prefix="/v1/projects", tags=["projects"])

@router.post("", response_model=ProjectOut)
async def create_project(
    payload: ProjectCreate,
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
):
    # enforce unique (org, key)
    exists = (await session.execute(
        select(Project).where(and_(Project.org_id==org_id, Project.key==payload.key))
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Project key exists")

    row = Project(org_id=org_id, name=payload.name, key=payload.key)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

@router.get("", response_model=list[ProjectOut])
async def list_projects(
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(default=None, description="opaque 'created_at,id' cursor"),
):
    q = select(Project).where(Project.org_id==org_id).order_by(Project.created_at.desc(), Project.id.desc()).limit(limit)
    # simple cursor: "timestamp|uuid"
    if cursor:
        ts_str, id_str = cursor.split("|", 1)
        from datetime import datetime
        ts = datetime.fromisoformat(ts_str)
        from uuid import UUID as _UUID
        q = q.where((Project.created_at < ts) | ((Project.created_at == ts) & (Project.id < _UUID(id_str))))
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Project, project_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return row

@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: UUID, payload: ProjectUpdate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Project, project_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None: row.name = payload.name
    if payload.status is not None: row.status = payload.status
    await session.commit()
    await session.refresh(row)
    return row

@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Project, project_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    await session.delete(row); await session.commit()
    return None
