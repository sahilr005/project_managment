from __future__ import annotations
from datetime import datetime,timezone, timedelta
from jose import jwt,JWTError
from typing import Any,Optional
from passlib.context import CryptContext
from app.core.config import settings
import uuid,hashlib

pwd_ctx = CryptContext(
    schemes=["bcrypt"],deprecated="auto")

def hash_password(raw:str) -> str:
    return pwd_ctx.hash(raw)

def verify_password(raw:str,hashed:str)-> bool:
    return pwd_ctx.verify(raw,hashed)

#JWT Setting
ACCESS_TTL_MIN =10
ALGO = "HS256"

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(*,sub:str, org_id: Optional[str]=None,roles:list[str]|None=None,
                       ttl_min: int=ACCESS_TTL_MIN)-> str:
    
    n = now_utc()
    payload: dict[str, Any]={
        "sub":sub,
        "iat": int(n.timestamp()),
        "exp": int((n+timedelta(minutes=ttl_min)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if org_id : payload["org"]= org_id
    if roles: payload["roles"]= roles
    return jwt.encode(payload,settings.jwt_secret,algorithm=ALGO)

def decode_token(token:str)-> dict[str,Any]:
    return jwt.decode(token,settings.jwt_secret,algorithms=[ALGO])

def hash_refresh(token:str)-> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()