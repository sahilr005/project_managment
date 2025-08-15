from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from app.api.deps import db, require_org_id
from app.db.models.label import Label
from app.db.models.task_label import TaskLabel
from app.db.models.task import Task
from app.schemas.labels import LabelCreate, LabelOut

router = APIRouter(prefix="/v1/labels", tags=["labels"])

@router.post("", response_model=LabelOut)
async def create_label(payload: LabelCreate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = Label(org_id=org_id, project_id=payload.project_id, name=payload.name, color=payload.color)
    session.add(row); await session.commit(); await session.refresh(row); return row

@router.get("", response_model=list[LabelOut])
async def list_labels(project_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    rows = (await session.execute(select(Label).where((Label.org_id==org_id) & (Label.project_id==project_id)))).scalars().all()
    return rows

@router.post("/attach")
async def attach_label(task_id: UUID, label_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    t = await session.get(Task, task_id)
    l = await session.get(Label, label_id)
    if not t or t.org_id != org_id: raise HTTPException(status_code=404, detail="Task not found")
    if not l or l.org_id != org_id: raise HTTPException(status_code=404, detail="Label not found")
    exists = (await session.execute(select(TaskLabel).where(and_(TaskLabel.org_id==org_id, TaskLabel.task_id==task_id, TaskLabel.label_id==label_id)))).scalar_one_or_none()
    if not exists:
        session.add(TaskLabel(org_id=org_id, task_id=task_id, label_id=label_id))
        await session.commit()
    return {"ok": True}

@router.post("/detach")
async def detach_label(task_id: UUID, label_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    q = select(TaskLabel).where(and_(TaskLabel.org_id==org_id, TaskLabel.task_id==task_id, TaskLabel.label_id==label_id))
    row = (await session.execute(q)).scalar_one_or_none()
    if row:
        await session.delete(row); await session.commit()
    return {"ok": True}
