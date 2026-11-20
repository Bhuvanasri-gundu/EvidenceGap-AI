"""FastAPI middleware for request timing, trace tracking, and error handling."""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("backend.middleware")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Tracks request duration and attaches unique X-Request-ID headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-MS"] = str(duration_ms)

        logger.debug(
            "%s %s - status: %d - elapsed: %sms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
