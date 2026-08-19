import time
import logging
from fastapi import Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")


async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f'{request.method} {request.url.path} '
        f'status={response.status_code} duration={duration_ms}ms '
        f'client={request.client.host if request.client else "unknown"}'
    )
    return response