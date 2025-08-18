from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.api.deps import db, require_org_id, require_role
from app.db.models.webhook import Webhook
from app.db.models.webhook_attempt import WebhookAttempt
from app.schemas.webhooks import WebhookCreate, WebhookUpdate, WebhookOut
from app.services.webhook_service import fire_event

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])

# Manage webhooks: admin+
admin_dep = [Depends(require_role("owner","admin"))]

@router.post("", response_model=WebhookOut, dependencies=admin_dep)
async def create_webhook(payload: WebhookCreate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = Webhook(org_id=org_id, url=str(payload.url), secret=payload.secret, events=payload.events, active=True)
    session.add(row); await session.commit(); await session.refresh(row); return row

@router.get("", response_model=list[WebhookOut], dependencies=admin_dep)
async def list_webhooks(session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    rows = (await session.execute(select(Webhook).where(Webhook.org_id==org_id))).scalars().all()
    return rows

@router.patch("/{webhook_id}", response_model=WebhookOut, dependencies=admin_dep)
async def update_webhook(webhook_id: UUID, payload: WebhookUpdate, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Webhook, webhook_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if payload.url is not None: row.url = str(payload.url)
    if payload.secret is not None: row.secret = payload.secret
    if payload.events is not None: row.events = payload.events
    if payload.active is not None: row.active = payload.active
    await session.commit(); await session.refresh(row); return row

@router.delete("/{webhook_id}", status_code=204, dependencies=admin_dep)
async def delete_webhook(webhook_id: UUID, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    row = await session.get(Webhook, webhook_id)
    if not row or row.org_id != org_id:
        raise HTTPException(status_code=404, detail="Webhook not found")
    await session.delete(row); await session.commit(); return None

@router.post("/test", dependencies=admin_dep)
async def test_send(event_type: str, session: AsyncSession = Depends(db), org_id: UUID = Depends(require_org_id)):
    # sends a dummy event to all active hooks
    await fire_event(session, org_id, event_type, {"ok": True, "test": True})
    await session.commit()
    # return recent attempts
    rows = (await session.execute(
        select(WebhookAttempt).where(WebhookAttempt.org_id==org_id).order_by(WebhookAttempt.created_at.desc()).limit(10)
    )).scalars().all()
    return [{"id": str(r.id), "webhook_id": str(r.webhook_id), "code": r.status_code, "success": r.success, "ms": r.duration_ms} for r in rows]
