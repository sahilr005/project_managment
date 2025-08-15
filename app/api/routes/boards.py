from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from app.api.deps import db, require_org_id, require_role
from app.db.models.board import Board
from app.db.models.project import Project
from app.schemas.boards import BoardCreate, BoardOut

router = APIRouter(prefix="/v1/boards", tags=["boards"])

@router.post("", response_model=BoardOut,dependencies=[Depends(require_role("owner","admin","manager","member"))])
async def create_board(payload: BoardCreate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    proj = await session.get(Project, payload.project_id)
    if not proj or proj.org_id != org_id:
        raise HTTPException(status_code=404, detail="Project not found")
    b = Board(org_id=org_id, project_id=payload.project_id, name=payload.name, type=payload.type)
    session.add(b); await session.commit(); await session.refresh(b)
    return b

@router.get("", response_model=list[BoardOut],dependencies=[Depends(require_role("owner","admin","manager","member"))])
async def list_boards(session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id), project_id: UUID | None = None):
    q = select(Board).where(Board.org_id==org_id)
    if project_id: q = q.where(Board.project_id==project_id)
    rows = (await session.execute(q.order_by(Board.created_at.desc()))).scalars().all()
    return rows
