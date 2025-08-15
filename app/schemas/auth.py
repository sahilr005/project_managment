from __future__ import annotations
from pydantic import BaseModel,EmailStr,Field
from uuid import UUID

class SignupIn(BaseModel):
    email: EmailStr
    full_name: str|None = Field(default=None,max_length=120)
    password: str = Field(min_length=4)

class LoginIn(BaseModel):
    email : EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str

class MeOut(BaseModel):
    id:UUID
    email: EmailStr
    full_name: str|None