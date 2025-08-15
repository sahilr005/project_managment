from fastapi import FastAPI
from app.core.logging import configure_logging
from app.core.config import settings
from app.db.models import task,user_cred,user_session
from app.middlewares.request_id import RequestIDMiddleware
from app.api.routes import health
from app.api.routes import orgs,users,memberships
from app.api.routes import projects as projects_router
from app.api.routes import boards as boards_router
from app.api.routes import columns as columns_router
from app.api.routes import tasks as tasks_router
from app.api.routes import comments as comments_router
from app.api.routes import labels as labels_router
from app.api.routes import auth as auth_router

# IMPORT models for Alembic discovery (side-effect import)
from app.db.models import organization,user,membership,project,label,task_comment,task_label,column,task

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
app.include_router(projects_router.router)
app.include_router(boards_router.router)
app.include_router(columns_router.router)
app.include_router(tasks_router.router)
app.include_router(comments_router.router)
app.include_router(labels_router.router)
app.include_router(health.router)
app.include_router(auth_router.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status":"running"
    }