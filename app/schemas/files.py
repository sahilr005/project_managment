from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class FileOut(BaseModel):
    id: UUID
    org_id: UUID
    storage: str
    path: str
    content_type: str |None
    size: int
    sha256: str|None
    scan_status: str
    created_at : datetime
    updated_at: datetime

    class Config:
        from_attributes =True

