from fastapi import FastAPI
from app.core.logging import configure_logging
from app.core.config import settings
from app.middlewares.request_id import RequestIDMiddleware
from app.api.routes import health
from app.api.routes import orgs,users,memberships
# IMPORT models for Alembic discovery (side-effect import)
from app.db.models import organization,user,membership

configure_logging()

app = FastAPI(
    title="SaaS Backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(RequestIDMiddleware)

#routes
app.include_router(health.router)
app.include_router(orgs.router)
app.include_router(users.router)
app.include_router(memberships.router)

app.include_router(health.router)

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status":"running"
    }