import uuid,structlog
from starlette.middleware.base  import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id= request.headers.get("X-Request-Id") or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=req_id)
        response: Response = await call_next(request)
        response.headers["X-Request-Id"] = req_id
        return response