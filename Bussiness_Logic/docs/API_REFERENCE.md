# Business Logic Service — API Reference

**Owner:** Intern 4 (Business Logic Developer)
**Base URL (local dev):** `http://127.0.0.1:8002`
**Covers:** Milestone 1, 2, and 3 (Days 1–8)

This document lists every endpoint built by the Business Logic service, grouped by feature area, with example requests and responses. Share this with Frontend (Intern 1) to confirm field names and shapes before wiring up real calls.

---

## Practice Sessions

### `POST /practice/start`
Starts a new practice session.

**Request:**
```json
{
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "lesson_id": 1
}
```

**Response (201):**
```json
{
  "session_id": "fb57e886-a11d-40c9-8e21-ae4f4cf1010a",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "lesson_id": 1,
  "status": "in_progress",
  "started_at": "2026-07-28T05:08:00.564560Z",
  "ended_at": null,
  "duration_seconds": null
}
```

### `POST /practice/end`
Ends a session.

**Request:**
```json
{ "session_id": "fb57e886-a11d-40c9-8e21-ae4f4cf1010a", "status": "completed" }
```
`status` can be `"completed"` or `"abandoned"`.

**Response (200):** same shape as start, with `ended_at` and `duration_seconds` populated.

**Note:** calling `/end` on an already-ended session returns `400` with a clear message. Triggers notification checks automatically (see Notifications section).

### `GET /practice/{session_id}`
Fetch a session's current state.

### `POST /practice/{session_id}/attempt`
Submits one practice attempt — uploads an image, calls the AI service, scores it, returns updated assessment. `multipart/form-data`.

**Form fields:**
- `expected_sign` (string, required) — e.g. `"A"`
- `attempt_started_at` (string, optional) — ISO 8601 timestamp, used to compute hold duration
- `file` (file, required) — the image

**Response (200):**
```json
{
  "predicted_sign": "A",
  "confidence": 0.9997,
  "success": true,
  "message": null,
  "hold_seconds": 2.3,
  "assessment": {
    "session_id": "...",
    "correct_predictions": 1,
    "total_predictions": 1,
    "accuracy_percentage": 100,
    "score": 95.17,
    "grade": "A",
    "completed_at": null
  }
}
```

---

## Assessment (manual/testing endpoint)

### `POST /assessment/attempt`
Records an attempt directly (bypasses AI call) — mainly for testing/demo, and for callers that already have a prediction.

**Request:**
```json
{
  "session_id": "...",
  "expected_sign": "A",
  "predicted_sign": "A",
  "confidence": 0.9
}
```

### `GET /assessment/{session_id}`
Returns the current aggregated assessment for a session.

---

## Feedback

### `POST /feedback/generate`
Generates rule-based feedback for a session (sign-specific tips, covers full A–Z alphabet).

**Request:**
```json
{ "session_id": "...", "expected_sign": "A" }
```

**Response (201):**
```json
{
  "session_id": "...",
  "feedback": [
    {
      "feedback_type": "improvement",
      "message": "For A: make a fist with your thumb resting on the side...",
      "severity": "medium"
    }
  ],
  "generated_at": "2026-07-28T..."
}
```
`feedback_type` is one of: `praise`, `improvement`, `correction`.

### `GET /feedback/{session_id}`
Fetch previously generated feedback.

---

## Analytics

### `GET /analytics/{user_id}`
Lifetime stats.
```json
{
  "user_id": "...",
  "total_sessions": 5,
  "lessons_completed": 5,
  "average_accuracy": 92.5,
  "weak_signs": ["Z"]
}
```

### `GET /analytics/{user_id}/weekly`
Week-by-week breakdown with improvement rate.
```json
{
  "user_id": "...",
  "weeks": [{ "week_label": "2026-W30", "sessions_count": 3, "average_accuracy": 90.0, "weak_signs": [] }],
  "improvement_rate": 12.5,
  "current_week_accuracy": 90.0,
  "previous_week_accuracy": 80.0
}
```

---

## Recommendations

### `GET /recommendations/{user_id}`
Recency-weighted — recent attempts count more than old ones.
```json
{
  "user_id": "...",
  "recommendations": [
    { "sign": "Z", "reason": "Your recent practice shows 0.0% accuracy on sign 'Z'...", "recent_accuracy": 0.0, "attempts_checked": 4.0 }
  ],
  "total_recommended": 1
}
```

---

## Certificates

### `GET /certificates/{user_id}/eligibility`
```json
{
  "user_id": "...",
  "eligible": false,
  "reasons_failed": ["Not enough completed sessions: 1/5"],
  "criteria_met": ["Average accuracy: 100.0% (required: 80.0%)"],
  "checked_at": "2026-07-28T..."
}
```

### `POST /certificates/{user_id}/generate`
Returns a downloadable PDF (blocked with `403` if not eligible).
```json
{ "learner_name": "Gana" }
```

---

## Progress Report

### `GET /progress/{user_id}`
Full JSON summary combining analytics + recommendations + certificate status.

### `POST /progress/{user_id}/pdf`
Downloadable PDF version.
```json
{ "learner_name": "Gana" }
```

---

## Gamification (Badges & Streaks) — M3

### `GET /gamification/{user_id}`
```json
{
  "user_id": "...",
  "streak": { "current_streak": 1, "longest_streak": 1, "last_practiced_date": "2026-07-28" },
  "badges": [
    { "badge_id": "first_step", "name": "First Step", "description": "...", "earned": true, "earned_at": "2026-07-28T..." }
  ],
  "total_badges_earned": 1
}
```
5 badges: `first_step`, `on_a_roll` (3-day streak), `alphabet_master` (10+ signs, 80%+ accuracy), `perfect_session` (100% in a session), `consistent_learner` (5+ completed sessions).

---

## Leaderboard — M3

### `GET /leaderboard?rank_by=accuracy` (or `rank_by=streak`)
```json
{
  "rank_by": "accuracy",
  "entries": [
    { "rank": 1, "user_id": "...", "average_accuracy": 95.0, "current_streak": 2, "total_sessions": 5, "score": 95.0 }
  ],
  "total_learners": 2
}
```

---

## Notifications — M3

### `GET /notifications/{user_id}`
```json
{
  "user_id": "...",
  "notifications": [
    { "notification_id": "6F8BDE76", "notification_type": "badge_earned", "title": "Badge Earned: First Step", "message": "...", "is_read": false, "created_at": "..." }
  ],
  "unread_count": 3,
  "total": 3
}
```
`notification_type`: `badge_earned`, `certificate_ready`, `new_recommendation`, `general`.

### `POST /notifications/{user_id}/read`
Marks all as read.

### `POST /notifications/{user_id}/trigger`
Manually checks for new events (also fires automatically on `/practice/end`).

**Note:** Currently notifications are stored locally in-memory. Set to forward to Intern 2's Notification API once it's confirmed live (`USE_REAL_NOTIFICATION_API` flag in `notification_service.py`).

---

## Export — M3

### `GET /export/{user_id}/progress?format=csv` (or `format=excel`)
Downloads learner's session-by-session progress as CSV or `.xlsx`.

### `GET /export/class/summary?format=csv` (or `format=excel`)
Downloads all-learners summary (instructor view) as CSV or `.xlsx`.

---

## Important Notes for Frontend Integration

1. **All `user_id` fields are UUIDs** (e.g. `3fa85f64-5717-4562-b3fc-2c963f66afa6`) — not simple integers like Intern 2's Course/Lesson IDs.
2. **`lesson_id` is an integer**, matching Intern 2's course schema.
3. **No authentication is currently enforced** on any Business Logic endpoint — auth/JWT integration is pending Intern 2's backend being fully connectable.
4. **All data is in-memory** — restarting the service clears all sessions, badges, notifications, etc. Persistence pending Intern 5's database delivery.
5. **CORS is configured** for `localhost:5173`, `127.0.0.1:5173`, `localhost:3000`, `127.0.0.1:3000` — let us know if your dev server runs on a different port.
6. **AI predictions** currently call Abhinaya's service directly at `127.0.0.1:8001/predict` (temporary — should route through Aashi's backend once her proxy is ready).

---

*Last updated: M3 Day 9*