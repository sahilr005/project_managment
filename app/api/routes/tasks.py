from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from uuid import UUID
from datetime import datetime
from app.ws.hub import hub, org_room
from app.api.deps import db, require_org_id,require_role
from app.db.models.task import Task
from app.db.models.project import Project
from app.db.models.board import Board
from app.db.models.column import Column
from app.db.models.user import User
from app.services import notification_service, webhook_service

from app.schemas.tasks import TaskCreate, TaskUpdate, TaskOut

router = APIRouter(prefix="/v1/tasks", tags=["tasks"])

@router.post("", response_model=TaskOut,dependencies=[Depends(require_role("owner","admin","manager","member"))])
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    proj = await session.get(Project, payload.project_id)
    if not proj or proj.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.board_id:
        b = await session.get(Board, payload.board_id)
        if not b or b.org_id != org_id:
            raise HTTPException(status_code=404, detail="Board not found")
    if payload.column_id:
        c = await session.get(Column, payload.column_id)
        if not c or c.org_id != org_id:
            raise HTTPException(status_code=404, detail="Column not found")
    if payload.assignee_id:
        u = await session.get(User, payload.assignee_id)
        if not u:
            raise HTTPException(status_code=404, detail="Assignee not found")

    row = Task(
        org_id=org_id,
        project_id=payload.project_id,
        board_id=payload.board_id,
        column_id=payload.column_id,
        title=payload.title,
        description=payload.description,
        status=payload.status or "todo",
        priority=payload.priority or "medium",
        assignee_id=payload.assignee_id,
        reporter_id=payload.reporter_id,
        due_at=payload.due_at,
        rank=payload.rank or 0,
    )
    session.add(row); await session.commit(); 
    await session.refresh(row)
    # notify assignee (if any)
    if row.assignee_id:
        await notification_service.notify_user(
            session, org_id, row.assignee_id, "task.created",
            {"task_id": str(row.id), "title": row.title, "priority": row.priority}
        )

    # fire outgoing webhooks
    await webhook_service.fire_event(session, org_id, "task.created", {
        "task_id": str(row.id),
        "project_id": str(row.project_id),
        "title": row.title,
        "priority": row.priority,
    })
    await session.commit()
    await hub.broadcast(org_room(str(org_id)), {
        "type": "task.created",
        "org_id": str(org_id),
        "task_id": str(row.id),
        "project_id": str(row.project_id),
        "title": row.title,
        "status": row.status,
        "priority": row.priority,
    })
    return row

@router.get("", response_model=list[TaskOut])
async def list_tasks(
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
    project_id: UUID | None = None,
    assignee_id: UUID | None = None,
    status: str | None = None,
    label_id: UUID | None = None,
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(default=None, description="created_at|id"),
):
    from app.db.models.task_label import TaskLabel
    q = select(Task).where(Task.org_id==org_id)
    if project_id: q = q.where(Task.project_id==project_id)
    if assignee_id: q = q.where(Task.assignee_id==assignee_id)
    if status: q = q.where(Task.status==status)
    if label_id:
        q = q.join(TaskLabel, and_(TaskLabel.org_id==Task.org_id, TaskLabel.task_id==Task.id)).where(TaskLabel.label_id==label_id)

    q = q.order_by(Task.created_at.desc(), Task.id.desc()).limit(limit)
    if cursor:
        ts_str, id_str = cursor.split("|", 1)
        ts = datetime.fromisoformat(ts_str)
        from uuid import UUID as _UUID
        q = q.where((Task.created_at < ts) | ((Task.created_at == ts) & (Task.id < _UUID(id_str))))
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Task, task_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return row

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: UUID, payload: TaskUpdate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Task, task_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.title is not None: row.title = payload.title
    if payload.description is not None: row.description = payload.description
    if payload.status is not None: row.status = payload.status
    if payload.priority is not None: row.priority = payload.priority
    if payload.assignee_id is not None: row.assignee_id = payload.assignee_id
    if payload.reporter_id is not None: row.reporter_id = payload.reporter_id
    if payload.column_id is not None: row.column_id = payload.column_id
    if payload.due_at is not None: row.due_at = payload.due_at
    if payload.rank is not None: row.rank = payload.rank
    await session.commit(); await session.refresh(row)
    await hub.broadcast(org_room(str(org_id)), {
        "type": "task.updated",
        "org_id": str(org_id),
        "task_id": str(row.id),
        "status": row.status,
        "priority": row.priority,
    })
    return row

@router.post("/{task_id}:move", response_model=TaskOut,dependencies=[Depends(require_role("owner","admin","manager","member"))])
async def move_task(task_id: UUID, column_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Task, task_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    col = await session.get(Column, column_id)
    if not col or col.org_id != org_id:
        raise HTTPException(status_code=404, detail="Column not found")
    row.column_id = column_id
    await session.commit(); await session.refresh(row)
    return row
