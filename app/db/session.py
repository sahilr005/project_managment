from __future__ import annotations
from sqlalchemy.ext.asyncio import(
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from app.core.config import settings
import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import ssl
import certifi

def _connect_args_for_pooler(url: str):
    # If using Supabase pooler, disable prepared statements
    connect_args: dict = {}
    if "pooler.supabase.com" in url:
        connect_args["statement_cache_size"] = 0
    # Ensure SSL for Supabase when using asyncpg (sslmode is not supported by asyncpg)
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if "supabase.co" in hostname or "pooler.supabase.com" in hostname:
        if getattr(settings, "db_ssl_allow_self_signed", False):
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        else:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
        connect_args["ssl"] = ssl_context
    return connect_args

def _to_async_url(url: str) -> str:
    # Convert driver
    converted = url
    if url.startswith("postgresql://"):
        converted = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Strip unsupported query params for asyncpg (e.g., sslmode)
    parsed = urlparse(converted)
    query_params = [(k, v) for k, v in parse_qsl(parsed.query) if k.lower() != "sslmode"]
    new_query = urlencode(query_params)
    cleaned = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))
    return cleaned

async_database_url = _to_async_url(settings.database_url)

engin = create_async_engine(
    async_database_url,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args_for_pooler(async_database_url),
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
        