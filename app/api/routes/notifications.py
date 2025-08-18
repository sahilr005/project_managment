from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from app.api.deps import db, require_org_id, current_user
from app.db.models.notification import Notification
from app.db.models.notification_pref import NotificationPreference
from app.schemas.notifications import NotificationOut, PrefsIn, PrefsOut

router = APIRouter(prefix="/v1/notifications", tags=["notifications"])

@router.get("", response_model=list[NotificationOut], dependencies=[Depends(current_user)])
async def list_notifications(
    session: AsyncSession = Depends(db),
    org_id: UUID = Depends(require_org_id),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    # list notifications for CURRENT user (not everyone)
    user = await current_user()  # not ideal to call directly; but dependency already ran for auth
    q = select(Notification).where((Notification.org_id==org_id) & (Notification.user_id==user.id)).order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    rows = (await session.execute(q)).scalars().all()
    return rows

@router.post("/{notification_id}:read", response_model=dict, dependencies=[Depends(current_user)])
async def mark_read(notification_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    user = await current_user()
    row = await session.get(Notification, notification_id)
    if not row or row.org_id != org_id or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    row.read = True; await session.commit()
    return {"ok": True}

@router.get("/prefs/me", response_model=PrefsOut, dependencies=[Depends(current_user)])
async def get_prefs(session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    user = await current_user()
    q = select(NotificationPreference).where((NotificationPreference.org_id==org_id) & (NotificationPreference.user_id==user.id))
    row = (await session.execute(q)).scalar_one_or_none()
    if not row:
        row = NotificationPreference(org_id=org_id, user_id=user.id)
        session.add(row); await session.commit(); await session.refresh(row)
    return row

@router.patch("/prefs/me", response_model=PrefsOut, dependencies=[Depends(current_user)])
async def update_prefs(payload: PrefsIn, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    user = await current_user()
    q = select(NotificationPreference).where((NotificationPreference.org_id==org_id) & (NotificationPreference.user_id==user.id))
    row = (await session.execute(q)).scalar_one_or_none()
    if not row:
        row = NotificationPreference(org_id=org_id, user_id=user.id)
        session.add(row)
    if payload.email_enabled is not None: row.email_enabled = payload.email_enabled
    if payload.push_enabled is not None: row.push_enabled = payload.push_enabled
    if payload.overrides is not None: row.overrides = payload.overrides
    await session.commit(); await session.refresh(row); return row
