
# Project Management SaaS – Backend (FastAPI)

A **multi-tenant, enterprise-grade SaaS backend** for a project management tool (like Jira/Slack).  
Built with **FastAPI, Async SQLAlchemy, PostgreSQL (with Row-Level Security), Alembic, Redis-ready, and JWT auth**.  
Supports **white-label resale**, **real-time collaboration**, and **secure file uploads**.

---

## 🚀 Features

- **Multi-Tenant Isolation**
  - PostgreSQL **Row-Level Security (RLS)** ensures strict tenant/org data separation.
  - Each request is scoped by `X-Org-Id`.

- **Authentication & RBAC**
  - JWT-based auth (access/refresh tokens).
  - Roles: `admin`, `member`, `guest`.

- **Core Project Management**
  - Organizations, users, memberships.
  - Projects → Boards → Columns → Tasks → Comments.
  - Labels, filters, pagination.

- **Files & Attachments**
  - Secure upload (local dev storage).
  - Download with org isolation.
  - Metadata: type, size, hash, virus-scan status.
  - Ready for **S3 + ClamAV** integration.

- **Real-time Collaboration**
  - WebSocket hub with org “rooms”.
  - Broadcast `task.created`, `task.updated`, `comment.created`.

- **Notifications & Webhooks**
  - Email/push (stubbed, extendable).
  - Webhooks with **HMAC signatures**.

- **Rate Limiting**
  - Basic middleware protection.

---

## 📂 Project Structure

```
app/
 ├── api/               # FastAPI routes
 │   ├── routes/        # REST & WS endpoints
 │   └── deps.py        # Common dependencies
 ├── core/              # Security, config, rate-limiter
 ├── db/                # Database setup, models, migrations
 │   ├── models/        # SQLAlchemy models
 │   └── base.py
 ├── schemas/           # Pydantic schemas
 ├── services/          # Business logic (storage, notifications, etc.)
 ├── ws/                # WebSocket hub
 └── main.py            # App entrypoint
```

---

## ⚙️ Tech Stack

- **Framework**: FastAPI (async)
- **Database**: PostgreSQL 15+ (with RLS enabled)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Auth**: JWT (PyJWT + passlib)
- **Cache/Events**: Redis (optional, for scaling WS/ratelimiting)
- **Other**: Pydantic v2, python-multipart (uploads)

---

## 🛠️ Setup & Installation

### 1. Clone & Create venv
```bash
git clone https://github.com/yourusername/project-saas-backend.git
cd project-saas-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure `.env`
Create `.env` file:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/saasdb
JWT_SECRET=super-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=43200
```

### 3. Database & Migrations
```bash
alembic upgrade head
```

### 4. Run the App
```bash
uvicorn app.main:app --reload
```

API docs at:  
➡️ [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📖 API Overview

### Auth
- `POST /v1/auth/signup`
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`

### Orgs & Membership
- `POST /v1/orgs`
- `GET /v1/orgs/{id}`
- `POST /v1/orgs/{id}/invite`

### Projects
- `POST /v1/projects`
- `GET /v1/projects?org_id=...`

### Boards & Tasks
- `POST /v1/projects/{id}/boards`
- `POST /v1/boards/{id}/columns`
- `POST /v1/columns/{id}/tasks`
- `PATCH /v1/tasks/{id}`
- `GET /v1/columns/{id}/tasks`

### Comments
- `POST /v1/tasks/{id}/comments`
- `GET /v1/tasks/{id}/comments`

### Files
- `POST /v1/files/upload` (multipart, requires `X-Org-Id`)
- `GET /v1/files/{id}`
- `GET /v1/files/{id}/download`

### Real-time (WebSockets)
- `ws://127.0.0.1:8000/ws?token=<JWT>&org_id=<ORG_ID>`

Events:
```json
{ "type": "task.created", "task_id": "...", "org_id": "...", ... }
{ "type": "task.updated", "task_id": "...", "status": "done" }
{ "type": "comment.created", "comment_id": "...", "task_id": "..." }
```

---

## 🔐 Security

- All org data is isolated via **Postgres RLS**.  
- Every API call must include:
  - `Authorization: Bearer <access_token>`  
  - `X-Org-Id: <org_uuid>`  

---

## 📈 Roadmap

- [ ] Switch local uploads → S3 + presigned URLs  
- [ ] Background virus scan (ClamAV worker)  
- [ ] Replace in-memory WS hub with Redis pub/sub  
- [ ] Full audit logs  
- [ ] Stripe billing integration (plans, seats, overages)  
- [ ] Multi-region deployment with CDN  

---

## 🧪 Testing

Run tests with `pytest`:
```bash
pytest -v
```

---

## 🏗️ Deployment

- Use **Gunicorn + Uvicorn workers** in production.
- Managed Postgres (Neon, Supabase, RDS).  
- Reverse proxy (NGINX, Traefik).  
- Optional: Docker Compose (for local stack).  

---

## 📄 License
MIT (or your choice for resale/white-label).
