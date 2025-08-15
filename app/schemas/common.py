from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ORMBase(BaseModel):
    class Config:
        from_attributes = True