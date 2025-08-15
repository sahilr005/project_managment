from __future__ import annotations
from pydantic import BaseModel,EmailStr,Field
from uuid import UUID
from datetime import datetime
from .common import ORMBase

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str |None = Field(default=None,max_length=120)

class UserUpdate(BaseModel):
    full_name: str|None =Field(default=None,max_length=120)
    is_active: bool| None=None

class UserOut(ORMBase):
    id: UUID
    email: EmailStr
    full_name: str|None
    is_active: bool
    created_at: datetime
    updated_at: datetime