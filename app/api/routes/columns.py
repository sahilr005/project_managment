from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.api.deps import db, require_org_id,require_role
from app.db.models.column import Column
from app.db.models.board import Board
from app.schemas.columns import ColumnCreate, ColumnUpdate, ColumnOut

router = APIRouter(prefix="/v1/columns", tags=["columns"])

@router.post("", response_model=ColumnOut,dependencies=[Depends(require_role("owner","admin","manager","member"))])
async def create_column(payload: ColumnCreate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    board = await session.get(Board, payload.board_id)
    if not board or board.org_id != org_id:
        raise HTTPException(status_code=404, detail="Board not found")
    c = Column(org_id=org_id, board_id=payload.board_id, name=payload.name, order=payload.order or 0)
    session.add(c); await session.commit(); await session.refresh(c)
    return c

@router.get("", response_model=list[ColumnOut])
async def list_columns(
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
    board_id: UUID | None = None,
):
    q = select(Column).where(Column.org_id == org_id)
    if board_id:
        q = q.where(Column.board_id == board_id)
    q = q.order_by(Column.order.asc(), Column.created_at.asc())
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.get("/{column_id}", response_model=ColumnOut)
async def get_column(
    column_id: UUID,
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
):
    c = await session.get(Column, column_id)
    if not c or c.org_id != org_id:
        raise HTTPException(status_code=404, detail="Column not found")
    return c


@router.patch("/{column_id}", response_model=ColumnOut)
async def update_column(column_id: UUID, payload: ColumnUpdate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    c = await session.get(Column, column_id)
    if not c or c.org_id != org_id:
        raise HTTPException(status_code=404, detail="Column not found")
    if payload.name is not None: c.name = payload.name
    if payload.order is not None: c.order = payload.order
    await session.commit(); await session.refresh(c)
    return c
