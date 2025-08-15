import socket
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])

def _tcp_ping(host:str,port:int, timeout: float=0.2)->bool:
    try:
        with socket.create_connection((host,port), timeout=timeout):
            return True
    except Exception:
        return False
    
@router.get("/healthz")
async def healthz():
    return  {"status":"ok","env":settings.env,"app":settings.app_name}

@router.get("/livez")
async def livez():
    return {"status":"ok"}

@router.get("readyz")
async def readyz():
    deps= {
        "redis": _tcp_ping("localhost",6379),
        "postgres":_tcp_ping("localhost",5432),
    }
    overall = all(deps.values()) if any (deps.values()) else True
    return {"status":"ok" if overall else "Degraded", "deps":deps}