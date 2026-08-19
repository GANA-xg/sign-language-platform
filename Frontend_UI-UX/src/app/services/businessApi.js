// Business Logic service client
// Practice / Assessment / Feedback / Analytics / Progress /
// Certificate / Recommendation / Gamification / Leaderboard /
// Notifications / Export / Trainer Analytics / Certification.
//
// Business Logic service:
//   Development: https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com
//   Production: VITE_BUSINESS_API_URL
//
// Backend API:
//   Development: https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com
//
// IMPORTANT ROLE:
//   trainer
//
// There is NO "accessibility_trainer" role.
//
// Trainer dashboard:
//   GET  /trainer/{trainer_id}/dashboard
//
// Trainer learners:
//   GET  /trainer/{trainer_id}/learners
//
// Trainer assignment:
//   POST /trainer/assign-student/{learner_id}


// ─────────────────────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────────────────────

const BUSINESS_BASE_URL =
  import.meta.env.VITE_BUSINESS_API_URL ??
  "https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com";

const BACKEND_BASE_URL =
  import.meta.env.VITE_API_URL ??
  "https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com";

export const BUSINESS_USE_MOCKS = false;

const delay = (value) =>
  new Promise((resolve) =>
    setTimeout(() => resolve(value), 300)
  );


// ─────────────────────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────────────────────

function getAuthHeaders() {
  const token =
    localStorage.getItem("token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}


// ─────────────────────────────────────────────────────────────
// BUSINESS REQUEST
// ─────────────────────────────────────────────────────────────

async function businessRequest(
  path,
  options = {}
) {
  const isFormData =
    options.body instanceof FormData;

  const token =
    localStorage.getItem("token");

  const headers = {
    ...(isFormData
      ? {}
      : {
          "Content-Type":
            "application/json",
        }),

    ...(token
      ? {
          Authorization:
            `Bearer ${token}`,
        }
      : {}),

    ...(options.headers || {}),
  };

  const response = await fetch(
    `${BUSINESS_BASE_URL}${path}`,
    {
      ...options,
      headers,
    }
  );

  if (!response.ok) {
    const text =
      await response
        .text()
        .catch(() => "");

    throw new Error(
      `Business service ${path} failed: ${response.status} ${text}`
    );
  }

  return response.json();
}

async function backendRequest(
  path,
  options = {}
) {
  const isFormData =
    options.body instanceof FormData;

  const token =
    localStorage.getItem("token");

  const headers = {
    ...(isFormData
      ? {}
      : {
          "Content-Type":
            "application/json",
        }),

    ...(token
      ? {
          Authorization:
            `Bearer ${token}`,
        }
      : {}),

    ...(options.headers || {}),
  };

  const response = await fetch(
    `${BACKEND_BASE_URL}${path}`,
    {
      ...options,
      headers,
    }
  );

  if (!response.ok) {
    const text =
      await response
        .text()
        .catch(() => "");

    throw new Error(
      `Backend service ${path} failed: ${response.status} ${text}`
    );
  }

  return response.json();
}


// ─────────────────────────────────────────────────────────────
// PRACTICE
// ─────────────────────────────────────────────────────────────

// POST /practice/start
// Body:
// {
//   user_id: UUID,
//   lesson_id: int
// }

export async function startPracticeSession(
  userId,
  lessonId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      session_id:
        "00000000-0000-0000-0000-000000000001",
      user_id: userId,
      lesson_id: lessonId,
      status: "in_progress",
      started_at:
        new Date().toISOString(),
      ended_at: null,
      duration_seconds: null,
    });
  }

  return businessRequest(
    "/practice/start",
    {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        lesson_id: lessonId,
      }),
    }
  );
}


// POST /practice/end
// Body:
// {
//   session_id: UUID,
//   status: "completed" | "abandoned"
// }

export async function endPracticeSession(
  sessionId,
  status = "completed"
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      session_id: sessionId,
      status,
      ended_at:
        new Date().toISOString(),
    });
  }

  return businessRequest(
    "/practice/end",
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        status,
      }),
    }
  );
}


// POST /practice/{session_id}/attempt
//
// multipart/form-data:
//   expected_sign
//   attempt_started_at
//   file

export async function submitPracticeAttempt(
  sessionId,
  expectedSign,
  imageBlob,
  attemptStartedAt
) {
  if (BUSINESS_USE_MOCKS) {
    const correct =
      Math.random() > 0.3;

    return delay({
      success: true,
      predicted_sign: correct
        ? expectedSign
        : "X",
      confidence: correct
        ? 0.88
        : 0.52,
      hold_seconds: 1.4,

      assessment: {
        session_id: sessionId,
        correct_predictions:
          correct ? 1 : 0,
        total_predictions: 1,
        accuracy_percentage:
          correct ? 100 : 0,
        score: correct ? 88 : 40,
        grade: correct ? "A" : "C",
        completed_at: null,
      },
    });
  }

  const formData =
    new FormData();

  formData.append(
    "expected_sign",
    expectedSign
  );

  if (attemptStartedAt) {
    formData.append(
      "attempt_started_at",
      attemptStartedAt
    );
  }

  formData.append(
    "file",
    imageBlob,
    "frame.jpg"
  );

  return businessRequest(
    `/practice/${sessionId}/attempt`,
    {
      method: "POST",
      body: formData,
    }
  );
}


// POST /assessment/attempt

export async function recordWordAssessment(
  sessionId,
  expectedSign,
  predictedSign,
  confidence
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      session_id: sessionId,
      correct_predictions: 1,
      total_predictions: 1,
      accuracy_percentage:
        confidence * 100,
      score:
        confidence * 100,
      grade: "A",
      completed_at: null,
    });
  }

  return businessRequest(
    "/assessment/attempt",
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        expected_sign: expectedSign,
        predicted_sign:
          predictedSign,
        confidence,
      }),
    }
  );
}


// ─────────────────────────────────────────────────────────────
// ASSESSMENT
// ─────────────────────────────────────────────────────────────

export async function getAssessment(
  sessionId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      session_id: sessionId,
      correct_predictions: 3,
      total_predictions: 4,
      accuracy_percentage: 75,
      score: 78,
      grade: "B",
      completed_at: null,
    });
  }

  return businessRequest(
    `/assessment/${sessionId}`
  );
}


// ─────────────────────────────────────────────────────────────
// FEEDBACK
// ─────────────────────────────────────────────────────────────

export async function generateFeedback(
  sessionId,
  expectedSign
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      session_id: sessionId,

      feedback: [
        {
          feedback_type: "praise",
          message:
            "Nice work holding the sign steady.",
          severity: "low",
        },
        {
          feedback_type: "improvement",
          message:
            "Try keeping your fingers a bit closer together.",
          severity: "medium",
        },
      ],

      generated_at:
        new Date().toISOString(),
    });
  }

  return businessRequest(
    "/feedback/generate",
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        expected_sign:
          expectedSign,
      }),
    }
  );
}


export async function getFeedback(
  sessionId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      session_id: sessionId,

      feedback: [
        {
          feedback_type: "praise",
          message: "Nice work!",
          severity: "low",
        },
      ],

      generated_at:
        new Date().toISOString(),
    });
  }

  return businessRequest(
    `/feedback/${sessionId}`
  );
}


// ─────────────────────────────────────────────────────────────
// ANALYTICS
// ─────────────────────────────────────────────────────────────

// GET /analytics/{user_id}

export async function getUserAnalytics(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      total_sessions: 24,
      lessons_completed: 18,
      average_accuracy: 91,
      weak_signs: [
        "R",
        "M",
        "N",
        "Q",
        "X",
      ],
    });
  }

  return businessRequest(
    `/analytics/${userId}`
  );
}


// GET /analytics/{user_id}/weekly

export async function getWeeklyAnalytics(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,

      weeks: [
        {
          week_label: "Wk 1",
          sessions_count: 3,
          average_accuracy: 72,
          weak_signs: ["R", "X"],
        },
        {
          week_label: "Wk 2",
          sessions_count: 4,
          average_accuracy: 78,
          weak_signs: ["M", "N"],
        },
        {
          week_label: "Wk 3",
          sessions_count: 5,
          average_accuracy: 83,
          weak_signs: ["Q"],
        },
        {
          week_label: "Wk 4",
          sessions_count: 6,
          average_accuracy: 88,
          weak_signs: [],
        },
        {
          week_label: "Wk 5",
          sessions_count: 4,
          average_accuracy: 91,
          weak_signs: [],
        },
      ],

      improvement_rate: 19,
      current_week_accuracy: 91,
      previous_week_accuracy: 88,
    });
  }

  return businessRequest(
    `/analytics/${userId}/weekly`
  );
}


// ─────────────────────────────────────────────────────────────
// PROGRESS
// ─────────────────────────────────────────────────────────────

export async function getProgressReport(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      generated_at:
        new Date().toISOString(),

      total_sessions: 24,
      completed_sessions: 21,
      total_practice_time_seconds:
        86400,

      average_accuracy: 91,
      grade: "A",

      distinct_signs_practiced: 18,

      weak_signs: [
        "R",
        "M",
        "N",
        "Q",
        "X",
      ],

      strong_signs: [
        "A",
        "B",
        "C",
        "D",
        "E",
        "L",
        "Y",
      ],

      current_week_accuracy: 91,
      improvement_rate: 19,

      recommended_for_practice: [
        "R",
        "M",
        "N",
      ],

      certificate_eligible: false,

      certificate_reasons_failed: [
        "Average accuracy below 80% for letters R, M, N",
      ],
    });
  }

  return businessRequest(
    `/progress/${userId}`
  );
}


// POST /progress/{user_id}/pdf

export async function downloadProgressPDF(
  userId,
  learnerName
) {
  if (BUSINESS_USE_MOCKS) {
    return delay(null);
  }

  const response = await fetch(
    `${BUSINESS_BASE_URL}/progress/${userId}/pdf`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",

        ...getAuthHeaders(),
      },

      body: JSON.stringify({
        learner_name:
          learnerName,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Progress PDF failed: ${response.status}`
    );
  }

  return response.blob();
}


// ─────────────────────────────────────────────────────────────
// CERTIFICATE ELIGIBILITY
// ─────────────────────────────────────────────────────────────

export async function getCertificateEligibility(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      eligible: false,

      reasons_failed: [
        "Average accuracy below 80% for letters R, M, N",
      ],

      criteria_met: [
        "Completed minimum 10 sessions",
        "Practiced at least 15 signs",
      ],

      checked_at:
        new Date().toISOString(),
    });
  }

  return businessRequest(
    `/certificates/${userId}/eligibility`
  );
}


// POST /certificates/{user_id}/generate

export async function generateCertificate(
  userId,
  learnerName
) {
  if (BUSINESS_USE_MOCKS) {
    return delay(null);
  }

  const response = await fetch(
    `${BUSINESS_BASE_URL}/certificates/${userId}/generate`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",

        ...getAuthHeaders(),
      },

      body: JSON.stringify({
        learner_name:
          learnerName,
      }),
    }
  );

  if (!response.ok) {
    const error =
      await response
        .json()
        .catch(() => ({}));

    throw new Error(
      error?.detail?.message ??
        `Certificate generation failed: ${response.status}`
    );
  }

  return response.blob();
}


// ─────────────────────────────────────────────────────────────
// RECOMMENDATIONS
// ─────────────────────────────────────────────────────────────

export async function getRecommendations(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      recommendations: [],
      total_recommended: 0,
    });
  }

  return businessRequest(
    `/recommendations/${userId}`
  );
}


// ─────────────────────────────────────────────────────────────
// GAMIFICATION
// ─────────────────────────────────────────────────────────────

export async function getGamification(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,

      streak: {
        current_streak: 14,
        longest_streak: 21,
        last_practiced_date:
          new Date().toISOString(),
      },

      badges: [],
      total_badges_earned: 0,
    });
  }

  return businessRequest(
    `/gamification/${userId}`
  );
}


// ─────────────────────────────────────────────────────────────
// LEADERBOARD
// ─────────────────────────────────────────────────────────────

export async function getLeaderboard(
  rankBy = "accuracy"
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      rank_by: rankBy,
      entries: [],
      total_learners: 0,
    });
  }

  return businessRequest(
    `/leaderboard?rank_by=${encodeURIComponent(
      rankBy
    )}`
  );
}


// ─────────────────────────────────────────────────────────────
// NOTIFICATIONS
// ─────────────────────────────────────────────────────────────

export async function getNotifications(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      notifications: [],
      unread_count: 0,
      total: 0,
    });
  }

  return businessRequest(
    `/notifications/${userId}`
  );
}


export async function markNotificationsRead(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      notifications: [],
      unread_count: 0,
      total: 0,
    });
  }

  return businessRequest(
    `/notifications/${userId}/read`,
    {
      method: "POST",
    }
  );
}


export async function triggerNotifications(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      user_id: userId,
      notifications: [],
      unread_count: 0,
      total: 0,
    });
  }

  return businessRequest(
    `/notifications/${userId}/trigger`,
    {
      method: "POST",
    }
  );
}


// ─────────────────────────────────────────────────────────────
// EXPORTS
// ─────────────────────────────────────────────────────────────

export async function downloadLearnerProgressExport(
  userId,
  format = "csv"
) {
  if (BUSINESS_USE_MOCKS) {
    return delay(null);
  }

  const response = await fetch(
    `${BUSINESS_BASE_URL}/export/${userId}/progress?format=${encodeURIComponent(
      format
    )}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      `Export failed: ${response.status}`
    );
  }

  return response.blob();
}


export async function downloadClassSummaryExport(
  format = "csv"
) {
  if (BUSINESS_USE_MOCKS) {
    return delay(null);
  }

  const response = await fetch(
    `${BUSINESS_BASE_URL}/export/class/summary?format=${encodeURIComponent(
      format
    )}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      `Class export failed: ${response.status}`
    );
  }

  return response.blob();
}


export async function exportClassSummary(
  format = "csv"
) {
  if (BUSINESS_USE_MOCKS) {
    const csv =
      "Student,Accuracy,Streak\n" +
      "Marcus Johnson,88,7\n" +
      "Priya Patel,62,2";

    return new Blob(
      [csv],
      {
        type: "text/csv",
      }
    );
  }

  const response = await fetch(
    `${BUSINESS_BASE_URL}/export/class/summary?format=${encodeURIComponent(
      format
    )}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    throw new Error(
      `Export failed: ${response.status}`
    );
  }

  return response.blob();
}


// ─────────────────────────────────────────────────────────────
// TRAINER ANALYTICS
// ─────────────────────────────────────────────────────────────
//
// IMPORTANT:
//
// Backend role:
//     trainer
//
// NOT:
//     accessibility_trainer
//
// Dashboard:
//     GET /trainer/{trainer_id}/dashboard
//
// Learners:
//     GET /trainer/{trainer_id}/learners
//
// Assignment:
//     POST /trainer/assign-student/{learner_id}


// GET /trainer/{trainer_id}/dashboard

export async function getTrainerDashboard(
  trainerId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      trainer_id: trainerId,

      assigned_learners_count: 5,

      avg_sessions_per_week: 4.2,

      avg_assessment_score: 79.4,

      certified_count: 2,

      low_engagement_count: 1,

      learners: [],
    });
  }

  return businessRequest(
    `/trainer/${trainerId}/dashboard`
  );
}


// GET /trainer/{trainer_id}/learners

export async function getTrainerLearners(
  trainerId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay([]);
  }

  return businessRequest(
    `/trainer/${trainerId}/learners`
  );
}


// GET /trainer/{trainer_id}/learners/{learner_id}

export async function getTrainerLearnerAnalytics(
  trainerId,
  learnerId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      learner_id: learnerId,
      sessions_this_week: 4,
      engagement_level: "High",
      avg_assessment_score: 82,
      skill_development_trend: 12,
      certification_status:
        "In Progress",
      highest_certified_level:
        null,
    });
  }

  return businessRequest(
    `/trainer/${trainerId}/learners/${learnerId}`
  );
}


// POST /trainer/assign-student/{learner_id}
//
// The trainer ID is taken from the authenticated
// user on the backend.
//
// Do NOT send:
//     trainer_id
//
// Do NOT use:
//     /trainer/assign
//
// Correct:
//     /trainer/assign-student/{learner_id}

export async function assignLearnerToTrainer(
  trainerId,
  learnerId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      trainer_id: trainerId,
      learner_id: learnerId,
      assigned_at:
        new Date().toISOString(),
    });
  }

  return backendRequest(
    `/trainer/assign-student/${learnerId}`,
    {
      method: "POST",
    }
  );
}


// DELETE /trainer/{trainer_id}/learners/{learner_id}

export async function removeLearnerFromTrainer(
  trainerId,
  learnerId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      message:
        "Student removed",
      trainer_id: trainerId,
      learner_id: learnerId,
    });
  }

  return businessRequest(
    `/trainer/${trainerId}/learners/${learnerId}`,
    {
      method: "DELETE",
    }
  );
}


// ─────────────────────────────────────────────────────────────
// CERTIFICATION EXAM
// ─────────────────────────────────────────────────────────────

// GET /certification/levels

export async function getCertificationLevels() {
  if (BUSINESS_USE_MOCKS) {
    return delay([
      {
        level: "beginner",
        num_signs: 5,
        pass_threshold: 0.7,
        description:
          "Signs A–E. 70% weighted-score threshold.",
      },
      {
        level: "intermediate",
        num_signs: 10,
        pass_threshold: 0.75,
        description:
          "Signs A–J. 75% weighted-score threshold.",
      },
      {
        level: "advanced",
        num_signs: 18,
        pass_threshold: 0.8,
        description:
          "Signs A–R. 80% weighted-score threshold.",
      },
      {
        level: "professional",
        num_signs: 26,
        pass_threshold: 0.85,
        description:
          "Full alphabet A–Z. 85% weighted-score threshold.",
      },
    ]);
  }

  return businessRequest(
    "/certification/levels"
  );
}


// POST /certification/start

export async function startCertificationExam(
  userId,
  level
) {
  if (BUSINESS_USE_MOCKS) {
    const signsMap = {
      beginner: [
        "A",
        "B",
        "C",
        "D",
        "E",
      ],

      intermediate: [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
      ],

      advanced: [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
      ],

      professional:
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split(
          ""
        ),
    };

    return delay({
      exam_id:
        "00000000-0000-0000-0000-000000000099",

      user_id: userId,

      level,

      required_signs:
        signsMap[level] ?? [
          "A",
          "B",
          "C",
          "D",
          "E",
        ],

      status: "in_progress",

      started_at:
        new Date().toISOString(),
    });
  }

  return businessRequest(
    "/certification/start",
    {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        level,
      }),
    }
  );
}


// POST /certification/attempt

export async function recordCertificationAttempt(
  examId,
  expectedSign,
  predictedSign,
  confidence,
  holdSeconds = null
) {
  if (BUSINESS_USE_MOCKS) {
    const isCorrect =
      predictedSign === expectedSign;

    return delay({
      exam_id: examId,
      expected_sign: expectedSign,
      predicted_sign:
        predictedSign,

      is_correct: isCorrect,

      attempt_score:
        isCorrect ? 88 : 40,

      signs_completed: 1,
      signs_remaining: 4,

      exam_status:
        "in_progress",
    });
  }

  return businessRequest(
    "/certification/attempt",
    {
      method: "POST",
      body: JSON.stringify({
        exam_id: examId,
        expected_sign:
          expectedSign,
        predicted_sign:
          predictedSign,
        confidence,
        hold_seconds:
          holdSeconds,
      }),
    }
  );
}


// POST /certification/{exam_id}/complete

export async function completeCertificationExam(
  examId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay({
      exam_id: examId,

      user_id:
        "00000000-0000-0000-0000-000000000001",

      level: "beginner",

      score: 82.5,
      accuracy_percentage: 80.0,

      correct_predictions: 4,
      total_predictions: 5,

      pass_threshold: 70.0,

      passed: true,

      completed_at:
        new Date().toISOString(),

      certificate_id: null,
    });
  }

  return businessRequest(
    `/certification/${examId}/complete`,
    {
      method: "POST",
    }
  );
}


// GET /certification/user/{user_id}/history

export async function getCertificationHistory(
  userId
) {
  if (BUSINESS_USE_MOCKS) {
    return delay([]);
  }

  return businessRequest(
    `/certification/user/${userId}/history`
  );
}


// POST /certification/{exam_id}/certificate

export async function downloadCertificationCertificate(
  examId,
  learnerName
) {
  if (BUSINESS_USE_MOCKS) {
    const text =
      `[Mock Certification Certificate PDF for exam ${examId}]`;

    return delay(
      new Blob(
        [text],
        {
          type: "application/pdf",
        }
      )
    );
  }

  const response = await fetch(
    `${BUSINESS_BASE_URL}/certification/${examId}/certificate`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",

        ...getAuthHeaders(),
      },

      body: JSON.stringify({
        learner_name:
          learnerName,
      }),
    }
  );

  if (!response.ok) {
    const text =
      await response
        .text()
        .catch(() => "");

    throw new Error(
      `Certification certificate failed: ${response.status} ${text}`
    );
  }

  return response.blob();
}


// ─────────────────────────────────────────────────────────────
// REPORT DOWNLOADS
// ─────────────────────────────────────────────────────────────

async function downloadReportBlob(
  path
) {
  const response = await fetch(
    `${BUSINESS_BASE_URL}${path}`,
    {
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  if (!response.ok) {
    const text =
      await response
        .text()
        .catch(() => "");

    throw new Error(
      `Report download failed: ${response.status} ${text}`
    );
  }

  return response.blob();
}


// Learning Report

export async function downloadLearningReport(
  userId,
  learnerName = "Learner",
  format = "pdf"
) {
  if (BUSINESS_USE_MOCKS) {
    const text =
      `[Mock Learning ${format.toUpperCase()} Report for ${learnerName}]`;

    const mime =
      format === "excel"
        ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        : "application/pdf";

    return delay(
      new Blob(
        [text],
        {
          type: mime,
        }
      )
    );
  }

  return downloadReportBlob(
    `/export/${userId}/learning?format=${encodeURIComponent(
      format
    )}&learner_name=${encodeURIComponent(
      learnerName
    )}`
  );
}


// Assessment Report

export async function downloadAssessmentReport(
  userId,
  learnerName = "Learner",
  format = "pdf"
) {
  if (BUSINESS_USE_MOCKS) {
    const text =
      `[Mock Assessment ${format.toUpperCase()} Report for ${learnerName}]`;

    const mime =
      format === "excel"
        ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        : "application/pdf";

    return delay(
      new Blob(
        [text],
        {
          type: mime,
        }
      )
    );
  }

  return downloadReportBlob(
    `/export/${userId}/assessment?format=${encodeURIComponent(
      format
    )}&learner_name=${encodeURIComponent(
      learnerName
    )}`
  );
}


// Accuracy Report

export async function downloadAccuracyReport(
  userId,
  learnerName = "Learner",
  format = "pdf"
) {
  if (BUSINESS_USE_MOCKS) {
    const text =
      `[Mock Accuracy ${format.toUpperCase()} Report for ${learnerName}]`;

    const mime =
      format === "excel"
        ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        : "application/pdf";

    return delay(
      new Blob(
        [text],
        {
          type: mime,
        }
      )
    );
  }

  return downloadReportBlob(
    `/export/${userId}/accuracy?format=${encodeURIComponent(
      format
    )}&learner_name=${encodeURIComponent(
      learnerName
    )}`
  );
}


// Certification Report
// This is the report, NOT the certificate PDF.

export async function downloadCertificationReport(
  userId,
  learnerName = "Learner",
  format = "pdf"
) {
  if (BUSINESS_USE_MOCKS) {
    const text =
      `[Mock Certification ${format.toUpperCase()} Report for ${learnerName}]`;

    const mime =
      format === "excel"
        ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        : "application/pdf";

    return delay(
      new Blob(
        [text],
        {
          type: mime,
        }
      )
    );
  }

  return downloadReportBlob(
    `/export/${userId}/certification-report?format=${encodeURIComponent(
      format
    )}&learner_name=${encodeURIComponent(
      learnerName
    )}`
  );
}
