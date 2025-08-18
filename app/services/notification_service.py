from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.db.models.notification import Notification
from app.db.models.notification_pref import NotificationPreference

async def ensure_prefs(session: AsyncSession, org_id: UUID, user_id: UUID) -> NotificationPreference:
    q = select(NotificationPreference).where(
        (NotificationPreference.org_id==org_id) & (NotificationPreference.user_id==user_id)
    )
    row = (await session.execute(q)).scalar_one_or_none()
    if row: return row
    row = NotificationPreference(org_id=org_id, user_id=user_id)
    session.add(row); await session.flush(); return row

async def notify_user(session: AsyncSession, org_id: UUID, user_id: UUID, type_: str, payload: dict):
    # create row
    n = Notification(org_id=org_id, user_id=user_id, type=type_, payload=payload)
    session.add(n)
    # load prefs (create default if missing)
    prefs = await ensure_prefs(session, org_id, user_id)
    # In dev: "send" by logging; in prod: push to worker/email
    # You could integrate a real email service here.
    # (Keep it inline for now; it's fast and simple.)
    return n
