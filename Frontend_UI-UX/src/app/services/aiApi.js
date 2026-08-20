// AI/CV service client — talks directly to Intern 3's standalone
// FastAPI service (production). Confirmed against real api.py (2026-08-16).
//
// Endpoints:
//   GET  /            — health check
//   GET  /health      — model status
//   POST /predict     — static A–Z letter prediction (image upload)
//   POST /predict-word — dynamic word prediction (video upload)
//                        words: HELLO, THANKYOU, SORRY, YES, NO
//   GET  /history     — in-memory prediction history
//   DELETE /history   — clear history
//   GET  /analytics   — session analytics
//   GET  /dashboard   — analytics + recent predictions
//
// Confidence scaling:
//   /predict     returns confidence as 0–100 (e.g. 91.23) → normalised to 0.0–1.0
//                    for Business Logic service compatibility via predictSign().
//   /predict-word returns confidence as 0–100 (dynamic_inference.py * 100)
//                    kept as-is for PracticeScreen display via predictWord().
//
// M4 Day 5: AI_BASE_URL reads from VITE_AI_API_URL env var for production.

const AI_BASE_URL = import.meta.env.VITE_AI_API_URL ?? "https://ai-signlanguage-platform-si7-team-one-58ie.onrender.com";
export const AI_USE_MOCKS = false;

const delay = (v) => new Promise((r) => setTimeout(() => r(v), 400));

async function aiRequest(path, options = {}) {
  const res = await fetch(`${AI_BASE_URL}${path}`, options);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`AI service ${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

// /predict returns confidence as 0–100; normalise to 0.0–1.0 for consistency
// with Business Logic service + CertificationExam expectations.
function normaliseConfidence(raw) {
  if (typeof raw !== "number") return 0;
  return raw > 1 ? raw / 100 : raw;
}

// ── POST /predict ────────────────────────────────────────────────────────────
// Send a captured frame (Blob/File) → static A–Z letter prediction.
// Real response (api.py 2026-08-16):
//   success, prediction, confidence (0–100), confidence_level, status,
//   feedback, possible_issue, recommendation, suggestion,
//   hand_position, vertical_position, hand_distance, gesture_quality,
//   processing_time_ms
// We normalise confidence to 0.0–1.0 before returning.
export async function predictSign(imageBlob) {
  if (AI_USE_MOCKS) {
    return delay({
      success: true,
      prediction: "A",
      confidence: 0.91,
      confidence_level: "High",
      status: "Correct",
      feedback: "Excellent! Gesture detected clearly.",
      possible_issue: "No major issues detected.",
      recommendation: "Keep your hand steady for best results.",
      suggestion: "Keep your hand steady for best results.",
      processing_time_ms: 42.3,
      hand_position: "centered",
      vertical_position: "middle",
      hand_distance: "optimal",
      gesture_quality: "good",
    });
  }
  const formData = new FormData();
  formData.append("file", imageBlob, "frame.jpg");
  const data = await aiRequest("/predict", { method: "POST", body: formData });
  return {
    ...data,
    confidence: normaliseConfidence(data.confidence),
  };
}

// ── POST /predict-word ────────────────────────────────────────────────────────
// Send a short video clip (Blob/File, .mp4/.avi/.mov) → dynamic word prediction.
// Words: HELLO, THANKYOU, SORRY, YES, NO
// Real response (api.py 2026-08-16):
//   success, prediction (string|null), confidence (0–100), sequence_shape, processing_time_ms
export async function predictWord(videoBlob, filename = "gesture.mp4") {
  if (AI_USE_MOCKS) {
    return delay({
      success: true,
      prediction: "HELLO",
      confidence: 87,
      sequence_shape: [30, 63],
      processing_time_ms: 312.5,
    });
  }
  const formData = new FormData();
  formData.append("file", videoBlob, filename);
  const data = await aiRequest("/predict-word", { method: "POST", body: formData });
  return {
    ...data,
  };
}

// ── GET /history ──────────────────────────────────────────────────────────────
export async function getHistory() {
  if (AI_USE_MOCKS) {
    return delay({ total_predictions: 0, history: [] });
  }
  return aiRequest("/history");
}

// ── DELETE /history ───────────────────────────────────────────────────────────
export async function clearHistory() {
  if (AI_USE_MOCKS) {
    return delay({ success: true, message: "Prediction history cleared successfully." });
  }
  return aiRequest("/history", { method: "DELETE" });
}

// ── GET /analytics ────────────────────────────────────────────────────────────
export async function getAnalytics() {
  if (AI_USE_MOCKS) {
    return delay({
      total_predictions: 0,
      average_confidence: 0,
      high_confidence_predictions: 0,
      low_confidence_predictions: 0,
      most_predicted_sign: null,
    });
  }
  return aiRequest("/analytics");
}

// ── GET /dashboard ────────────────────────────────────────────────────────────
export async function getDashboard() {
  if (AI_USE_MOCKS) {
    return delay({
      analytics: {
        total_predictions: 0, average_confidence: 0,
        high_confidence_predictions: 0, low_confidence_predictions: 0,
        most_predicted_sign: null,
      },
      recent_predictions: [],
    });
  }
  return aiRequest("/dashboard");
}
// Keep-alive ping to prevent cold starts
export function startKeepAlive() {
  const ping = () => fetch(`${AI_BASE_URL}/health`).catch(() => {});
  ping(); // immediate
  setInterval(ping, 10 * 60 * 1000); // every 10 min
}
