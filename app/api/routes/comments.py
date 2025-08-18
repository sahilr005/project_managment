from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.services import notification_service, webhook_service
from app.db.models.task import Task
from app.ws.hub import hub, org_room
from app.api.deps import db, require_org_id
from app.db.models.task import Task
from app.db.models.task_comment import TaskComment
from app.schemas.comments import CommentCreate, CommentOut

router = APIRouter(prefix="/v1/comments", tags=["comments"])

@router.post("", response_model=CommentOut)
async def add_comment(payload: CommentCreate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    t = await session.get(Task, payload.task_id)
    if not t or t.org_id != org_id:
        raise HTTPException(status_code=404, detail="Task not found")
    c = TaskComment(org_id=org_id, task_id=payload.task_id, user_id=payload.user_id, body=payload.body)
    session.add(c); await session.commit(); await session.refresh(c); 

    t = await session.get(Task, c.task_id)
    if t and t.assignee_id:
        await notification_service.notify_user(
            session, org_id, t.assignee_id, "comment.created",
            {"task_id": str(t.id), "comment_id": str(c.id)}
        )

    await webhook_service.fire_event(session, org_id, "comment.created", {
        "task_id": str(t.id) if t else None,
        "comment_id": str(c.id),
    })
    await session.commit()
    await hub.broadcast(org_room(str(org_id)), {
        "type": "comment.created",
        "org_id": str(org_id),
        "task_id": str(c.task_id),
        "comment_id": str(c.id),
    })
    return c

@router.get("", response_model=list[CommentOut])
async def list_comments(task_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    q = select(TaskComment).where((TaskComment.org_id==org_id) & (TaskComment.task_id==task_id)).order_by(TaskComment.created_at.asc())
    rows = (await session.execute(q)).scalars().all()
    return rows
