# Certification Exam & Reports — Plain English Guide
**AI-Powered Sign Language Learning & Assessment Platform**
Milestone 4 | Business Logic Domain (Intern 4)

---

## Part 1 — Certification Exam

### What is it?
The Certification Exam is a formal test that is **completely separate from regular practice sessions**. In regular practice, a learner works through signs one at a time at their own pace, with instant feedback after each attempt. The Certification Exam is different — it presents a fixed set of signs, scores everything together at the end, and gives a clear **PASS or FAIL** result.

Think of it like the difference between doing homework (practice) and sitting a final exam (certification).

---

### The 4 Levels

| Level | Signs Tested | Pass Score Required | Who It's For |
|---|---|---|---|
| **Beginner** | 8 signs (random from A–Z) | 60% | Just starting out — proves basic familiarity |
| **Intermediate** | 14 signs | 70% | Building confidence — proves solid foundations |
| **Advanced** | 20 signs | 80% | Regular learners — proves strong competency |
| **Professional** | All 26 signs (A–Z) | 85% | Full mastery — the highest certification available |

Each level's signs are **randomly selected** from the full A–Z alphabet that Intern 3's AI model already knows. The Professional level always tests all 26 letters — nothing is left out.

---

### How Scoring Works

The Certification Exam uses the **exact same weighted scoring formula** as regular practice (built in Milestone 2). Each sign attempt is scored out of 100 using four factors:

| Factor | Weight | What it Measures |
|---|---|---|
| Correctness | Core gate | Was the right sign shown? |
| Confidence | 30% | How certain was the AI's prediction? |
| Duration | 20% | Did the learner hold the pose long enough? |
| Hand shape | 25% | How accurate was the hand shape? |
| Finger position | 25% | How accurate was the finger position? |

At the end of the exam, all attempt scores are **averaged** to produce a single final score. If that average meets or exceeds the level's pass threshold, the learner passes.

**Example:** A learner sits the Beginner exam (8 signs). Their attempt scores are:
`94, 94, 30, 94, 94, 94, 94, 94` → Average = **86%** → Beginner threshold is 60% → **PASS**

---

### The Exam Flow (Step by Step)

1. **Start** — Learner picks a level (Beginner/Intermediate/Advanced/Professional). The system assigns a random set of signs for that level and returns them to the frontend.
2. **Attempt** — For each sign in the set, the learner performs the sign on camera. Intern 3's AI predicts what sign was shown. The result is recorded (correct/incorrect + score).
3. **Complete** — Once all signs have been attempted, the learner (or the frontend) calls the complete endpoint. The system calculates the final average score and sets PASS or FAIL.
4. **Certificate** — If the learner passed, the frontend can request a PDF certificate. The system checks the exam was completed and passed, then generates a certificate using the same ReportLab PDF generator built in Milestone 2.

**Rules:**
- Each sign can only be attempted **once** per exam — no second chances mid-exam.
- The exam cannot be marked complete until **every sign** in the set has been attempted.
- A certificate is only issued if the exam is both **completed** and **passed** — a failed attempt returns a clear error with the learner's score and the threshold they needed to reach.

---

### API Endpoints (for Intern 2 / Intern 1 reference)

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/certification/levels` | List all 4 levels with sign counts and thresholds |
| POST | `/certification/start` | Start a new exam for a user at a chosen level |
| POST | `/certification/attempt` | Submit one sign attempt during an in-progress exam |
| POST | `/certification/{exam_id}/complete` | Finalise the exam and get the pass/fail result |
| GET | `/certification/{exam_id}` | Check the current state or final result of an exam |
| GET | `/certification/user/{user_id}/history` | List all completed exams for a learner |
| POST | `/certification/{exam_id}/certificate` | Generate and download the PDF certificate |

---

## Part 2 — Reports & Export System

### What reports are available?

There are **5 report types**, each available as both a **PDF** and an **Excel file**. Every report is generated fresh from the learner's real data — nothing is pre-computed or cached.

---

### Report 1 — Learning Report
**What it shows:** How often the learner practices, how long each session lasts, and how many signs they work on per session.

**Useful for:** Tracking engagement and study habits. A trainer can see at a glance whether a learner is practicing regularly or going long stretches without sessions.

**Endpoint:** `GET /export/{user_id}/learning?format=pdf` or `?format=excel`

---

### Report 2 — Assessment Report
**What it shows:** A session-by-session breakdown of scores. For each practice session: total attempts, correct predictions, accuracy percentage, weighted average score, and letter grade (A/B/C/D/F).

**Useful for:** Identifying whether a learner's performance is improving, declining, or staying flat over time. The overall average score and grade appear at the top of the PDF.

**Endpoint:** `GET /export/{user_id}/assessment?format=pdf` or `?format=excel`

---

### Report 3 — Accuracy Report
**What it shows:** A per-sign breakdown across all sessions combined. For every sign the learner has ever attempted: how many times they tried it, how many times they got it right, their accuracy percentage, and a status label (Weak / OK / Strong). Signs are sorted **weakest first** so problem areas are immediately obvious.

**Status labels:**
- **Weak** — below 60% accuracy (needs focused practice)
- **OK** — 60–79% accuracy (getting there)
- **Strong** — 80%+ accuracy (confident)

**Useful for:** Targeted coaching. A trainer or the learner can immediately see which specific signs need the most work.

**Endpoint:** `GET /export/{user_id}/accuracy?format=pdf` or `?format=excel`

---

### Report 4 — Certification Report
**What it shows:** The learner's full certification exam history — every exam they have completed, with the level, number of signs tested, their score, the pass threshold for that level, whether they passed or failed, and the date.

**Useful for:** Showing formal achievement records. Administrators and trainers can verify which certification levels a learner has officially passed.

**Endpoint:** `GET /export/{user_id}/certification-report?format=pdf` or `?format=excel`

---

### Report 5 — Progress Report (built in Milestone 2, extended in M3/M4)
**What it shows:** A comprehensive summary combining session history, weekly analytics, improvement rate, weak signs, streak, badges earned, and certificate eligibility — the most complete single-learner view available.

**Endpoint:** `GET /progress/{user_id}/report?format=pdf` or `GET /export/{user_id}/progress?format=csv` / `?format=excel`

---

### How to Download a Report

All reports follow the same pattern:

```
GET /export/{user_id}/{report_type}?format=pdf&learner_name=YourName
```

- Replace `{user_id}` with the learner's UUID
- Replace `{report_type}` with: `learning`, `assessment`, `accuracy`, or `certification-report`
- Set `format=pdf` for a PDF or `format=excel` for an Excel file
- The `learner_name` query parameter appears on the PDF cover — optional, defaults to "Learner"

The response is a file download (the browser will prompt to save it, or the frontend can use a Blob URL to trigger download automatically).

---

## Technical Notes (for the team)

- All report data comes from the **same in-memory stores** used everywhere else in the business logic service — no separate data layer needed.
- Once Intern 5's real database is wired in, the stores will be swapped for SQLAlchemy calls; the report functions themselves won't change.
- PDF generation uses **ReportLab** (free, already installed since Milestone 2).
- Excel generation uses **openpyxl** (free, already installed since Milestone 3).
- All PDF reports share a consistent visual style: blue/green headers, alternating row backgrounds, HR dividers, and the platform name in the subtitle.