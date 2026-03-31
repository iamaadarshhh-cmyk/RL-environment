# server/middleware.py

import time
from fastapi import FastAPI, Request
from loguru import logger


def setup_middleware(app: FastAPI):
    """Setup all middleware for the app."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log every request and response time."""

        start_time = time.time()
        response = await call_next(request)
        process_time = round(time.time() - start_time, 4)

        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} "
            f"({process_time}s)"
        )

        return response