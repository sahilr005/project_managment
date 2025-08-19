from fastapi import FastAPI
from app.core.logging import configure_logging
from app.core.config import settings
from app.db.models import task,user_cred,user_session,notification, notification_pref, webhook, webhook_attempt
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
from app.api.routes import files as files_router
from app.api.routes import ws as ws_router
from app.api.routes import notifications as notifications_router
from app.api.routes import webhooks as webhooks_router
from app.middlewares.rate_limit import RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.db.models import File

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
origins = [
      "http://localhost:8080",
  "http://127.0.0.1:8080",
  "http://127.0.0.1:54372",
    "http://localhost:5500",   # e.g. Flutter web dev server
    "http://127.0.0.1:5500",
    "http://localhost:3000",   # another dev port
    "http://127.0.0.1:3000",
    "http://your-domain.com",  # production
]

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:*", "http://127.0.0.1:*"],
    allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"],
    allow_headers=["Authorization","Content-Type","X-Org-Id"],
    allow_credentials=False
)

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
app.include_router(files_router.router)
app.include_router(ws_router.router)
app.include_router(notifications_router.router)
app.include_router(webhooks_router.router)

app.add_middleware(RateLimitMiddleware, limit=120, window_sec=60)  # 120 req/min per IP per path

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status":"running"
    }