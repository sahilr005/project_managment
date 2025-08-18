import time
from collections import defaultdict, deque
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60, window_sec: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window_sec
        self.store = defaultdict(deque)  # key -> deque[timestamps]

    async def dispatch(self, request: Request, call_next):
        # key by (ip, path) – you can key by user id if authenticated
        ip = request.client.host if request.client else "unknown"
        key = f"{ip}:{request.url.path}"
        now = time.time()
        q = self.store[key]
        # prune old
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        q.append(now)
        return await call_next(request)
