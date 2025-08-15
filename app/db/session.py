from __future__ import annotations
from sqlalchemy.ext.asyncio import(
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from app.core.config import settings

engin = create_async_engine(
    settings.database_url,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionMaker = async_sessionmaker(
    engin,expire_on_commit = False,
    class_=AsyncSession
)

# Request-scoped session dependency that ALSO sets the per-connection tenant var.
from fastapi import Request
from sqlalchemy import text
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session(request: Request):
    async with AsyncSessionMaker() as session:
        org_id = request.headers.get("X-Org-Id")
        if org_id:
            await session.execute(
                text("SELECT set_config('app.current_org_id', :org, true)"),
                {"org":str(org_id)}
            )
        yield session
        