from __future__ import annotations
import hmac, hashlib, time
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.db.models.webhook import Webhook
from app.db.models.webhook_attempt import WebhookAttempt

def _sign(secret: str, body: bytes) -> str:
    sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

async def fire_event(session: AsyncSession, org_id: UUID, event_type: str, payload: dict):
    # load active webhooks for org subscribed to this event
    q = select(Webhook).where(
        (Webhook.org_id==org_id) & (Webhook.active==True) & (Webhook.events.contains([event_type]))
    )
    hooks = (await session.execute(q)).scalars().all()
    if not hooks:
        return

    body = (payload | {"type": event_type, "org_id": str(org_id)})

    # Send sequentially (simple); consider background worker for scale
    async with httpx.AsyncClient(timeout=8.0) as client:
        for h in hooks:
            t0 = time.perf_counter()
            status_code = None
            success = False
            error = None
            try:
                b = httpx.ByteStream.from_bytes_json(body)  # small convenience to get bytes
            except Exception:
                import json
                raw = json.dumps(body).encode("utf-8")
            else:
                raw = b._stream  # type: ignore

            try:
                resp = await client.post(
                    h.url,
                    content=raw,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": _sign(h.secret, raw),
                        "X-Webhook-Event": event_type,
                    },
                )
                status_code = resp.status_code
                success = 200 <= resp.status_code < 300
            except Exception as e:
                error = str(e)
            dt = int((time.perf_counter() - t0) * 1000)
            session.add(WebhookAttempt(
                org_id=org_id,
                webhook_id=h.id,
                event_type=event_type,
                status_code=status_code,
                success=success,
                error=error,
                duration_ms=dt,
            ))
    # attempts stored; caller should commit the session
