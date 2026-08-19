from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.routers import trainer
from app.core.limiter import limiter
from app.core.middleware import log_requests
from app.routers import auth, courses, health, predict, instructor, admin, notification, practice, trainer

from fastapi.encoders import jsonable_encoder

app = FastAPI(
    title="Sign Language Platform API",
    description="Backend API for the AI-Powered Sign Language Learning & Assessment Platform.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Rate limiting (Milestone 2 + M3 Day 6 per-user limits live inside routers)
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request logging (existing)
# ---------------------------------------------------------------------------
app.middleware("http")(log_requests)

# ---------------------------------------------------------------------------
# M3 Day 5: Input validation hardening
# ---------------------------------------------------------------------------
MAX_BODY_SIZE = 1_000_000  # 1MB


@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={"detail": "Request body too large"},
        )
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid input", "errors": jsonable_encoder(exc.errors())},
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(instructor.router)
app.include_router(admin.router)
app.include_router(notification.router)
app.include_router(trainer.router)
app.include_router(practice.router)
