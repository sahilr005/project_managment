from __future__ import annotations
from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class OrgCreate(BaseModel):
    name: str = Field(min_length=2,max_length=120)
    domain: str| None = Field(default=None,max_length=255)

class OrgUpdate(BaseModel):
    name: str|None = Field(default=None, min_length=2, max_length=120)
    domain: str|None =Field(decimal_places=None)

class OrgOut(ORMBase):
    id:UUID
    name: str
    domain: str|None
    created_at: datetime
    updated_at: datetime
    