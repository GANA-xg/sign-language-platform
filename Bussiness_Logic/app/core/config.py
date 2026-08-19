"""
Centralized Environment Configuration (Milestone 4, Day 6)

Business logic must work correctly against the LIVE deployed AI service
and LIVE database (Render/Railway/Fly.io + Supabase/Neon/etc.), not just
localhost. Previously AI_PREDICT_URL was hardcoded in ai_client.py, which
would break the moment Intern 3's service moved off 127.0.0.1.

All values fall back to the existing local-dev defaults, so nothing
breaks for anyone still developing locally — only the .env / real
environment variables need to be set once deployed.
"""

import os

# ── AI Service (Intern 3) ────────────────────────────────────────────
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8001/predict")
USE_MOCK_AI = os.getenv("USE_MOCK_AI", "false").lower() == "true"

# ── Database (Intern 5) ──────────────────────────────────────────────
# Not yet consumed anywhere (models are still in-memory stubs per M1-M4
# design), but read here now so the swap to real DB calls doesn't also
# require hunting down a hardcoded connection string later.
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ── Backend API (Intern 2) ───────────────────────────────────────────
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

# ── Request timeouts ──────────────────────────────────────────────────
AI_SERVICE_TIMEOUT_SECONDS = float(os.getenv("AI_SERVICE_TIMEOUT_SECONDS", "10.0"))