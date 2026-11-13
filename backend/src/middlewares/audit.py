import logging
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.database import insert_row

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            try:
                user = getattr(request.state, "user", {})
                insert_row("audit", uuid4().hex, {"method": request.method, "path": request.url.path,
                    "status": response.status_code, "actor": user.get("email", "anonymous")})
            except Exception: logging.exception("Audit persistence failed")
        return response
