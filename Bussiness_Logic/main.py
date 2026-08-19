from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    practice, assessment, feedback, analytics, recommendation,
    certificate, progress, gamification, leaderboard, notification,
    export, certification, trainer_analytics,
)

app = FastAPI(title="Practice Service (dev)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(practice.router)
app.include_router(assessment.router)
app.include_router(feedback.router)
app.include_router(analytics.router)
app.include_router(recommendation.router)
app.include_router(certificate.router)
app.include_router(progress.router)
app.include_router(gamification.router)
app.include_router(leaderboard.router)
app.include_router(notification.router)
app.include_router(export.router)
app.include_router(certification.router)
app.include_router(trainer_analytics.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "practice"}