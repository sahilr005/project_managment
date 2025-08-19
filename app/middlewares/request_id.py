import time
import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # accept incoming header or generate one
        req_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())

        # bind to structlog contextvars so all logs in this request include it
        structlog.contextvars.bind_contextvars(request_id=req_id)

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        finally:
            # always add header + clean up context, even on exception paths
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status=getattr(locals().get("response", None), "status_code", None),
                duration_ms=duration_ms,
            )
            structlog.contextvars.unbind_contextvars("request_id")

        response.headers["X-Request-Id"] = req_id
        return response
