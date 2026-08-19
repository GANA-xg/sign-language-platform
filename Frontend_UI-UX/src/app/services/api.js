// Central API layer — aligned with backend role names.
//
// Backend DB roles:
//   learner
//   instructor
//   trainer
//   admin
//
// Frontend roles use the exact same values.
// There is NO "accessibility_trainer" role.

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const USE_MOCKS = false;

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, options = {}) {
  const token = getToken();

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }

  return res.json();
}

const MOCK_DELAY = 300;
const delay = (v) =>
  new Promise((r) => setTimeout(() => r(v), MOCK_DELAY));


// ─────────────────────────────────────────────────────────────
// ROLE HELPERS
// ─────────────────────────────────────────────────────────────
//
// Backend and frontend use EXACTLY the same role names:
//
// learner
// instructor
// trainer
// admin
//

function toBackendRole(role) {
  return role;
}

function toFrontendRole(backendRoles = []) {
  if (backendRoles.includes("trainer")) return "trainer";
  if (backendRoles.includes("admin")) return "admin";
  if (backendRoles.includes("instructor")) return "instructor";
  if (backendRoles.includes("learner")) return "learner";

  return "learner";
}


// ─────────────────────────────────────────────────────────────
// AUTH
// ─────────────────────────────────────────────────────────────

export async function registerUser({
  name,
  email,
  password,
  role,
}) {
  if (USE_MOCKS) {
    return delay({
      user_id: "00000000-0000-0000-0000-000000000001",
      full_name: name,
      email,
      roles: [role],
      created_at: new Date().toISOString(),
    });
  }

  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({
      full_name: name,
      email,
      password,
      requested_role: toBackendRole(role),
    }),
  });
}


export async function loginUser({
  email,
  password,
  role,
}) {
  if (USE_MOCKS) {
    const mockRole = role ?? "learner";

    const data = {
      access_token: "mock-jwt-token",
      token_type: "bearer",

      user: {
        user_id: "00000000-0000-0000-0000-000000000001",
        full_name: "Maya Chen",
        email,
        roles: [mockRole],
        created_at: new Date().toISOString(),
      },
    };

    const frontendRole = toFrontendRole(data.user.roles);

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", frontendRole);
    localStorage.setItem("user_id", data.user.user_id);

    return {
      ...data,
      role: frontendRole,
    };
  }

  // IMPORTANT:
  // If frontend role is "trainer", backend receives "trainer".
  const backendRole = toBackendRole(role);

  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      role: backendRole,
    }),
  });

  const backendRoles = data.user?.roles ?? [];

  const frontendRole = toFrontendRole(backendRoles);

  localStorage.setItem("token", data.access_token);
  localStorage.setItem("role", frontendRole);
  localStorage.setItem(
    "user_id",
    data.user?.user_id ?? ""
  );

  return {
    ...data,
    role: frontendRole,
  };
}


export async function getProfile() {
  if (USE_MOCKS) {
    return delay({
      user_id: "00000000-0000-0000-0000-000000000001",
      full_name: "Maya Chen",
      email: "maya.chen@example.com",
      roles: [
        localStorage.getItem("role") || "learner",
      ],
      created_at: new Date().toISOString(),
    });
  }

  return request("/auth/profile");
}


export function logoutUser() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  localStorage.removeItem("user_id");
}


export async function updateProfile({
  fullName,
  email,
}) {
  if (USE_MOCKS) {
    return delay({
      user_id: "00000000-0000-0000-0000-000000000001",
      full_name: fullName,
      email,
      roles: [
        localStorage.getItem("role") || "learner",
      ],
      created_at: new Date().toISOString(),
    });
  }

  return request("/auth/me", {
    method: "PUT",
    body: JSON.stringify({
      full_name: fullName,
      email,
    }),
  });
}


export async function changePassword({
  oldPassword,
  newPassword,
}) {
  if (USE_MOCKS) {
    return delay({
      message: "Password changed successfully.",
    });
  }

  return request("/auth/me/password", {
    method: "PUT",
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
    }),
  });
}


// ─────────────────────────────────────────────────────────────
// COURSES / LESSONS
// ─────────────────────────────────────────────────────────────

export async function getCourses() {
  if (USE_MOCKS) {
    return delay([
      {
        id: "1",
        title: "ASL Fundamentals",
        difficulty: "Beginner",
        lessons: 24,
        desc: "Core signs, alphabet, and basic phrases.",
        hrs: "6 hrs",
        pct: 100,
        cat: "ASL",
      },
      {
        id: "2",
        title: "ASL Intermediate",
        difficulty: "Intermediate",
        lessons: 32,
        desc: "Emotions, questions, and sentence structure.",
        hrs: "9 hrs",
        pct: 68,
        cat: "ASL",
      },
      {
        id: "3",
        title: "ASL Advanced Conversation",
        difficulty: "Advanced",
        lessons: 28,
        desc: "Classifiers, complex grammar, and fluent ASL.",
        hrs: "12 hrs",
        pct: 0,
        cat: "ASL",
      },
      {
        id: "4",
        title: "BSL Basics",
        difficulty: "Beginner",
        lessons: 20,
        desc: "Introduction to British Sign Language.",
        hrs: "5 hrs",
        pct: 0,
        cat: "BSL",
      },
      {
        id: "5",
        title: "Medical Sign Language",
        difficulty: "Intermediate",
        lessons: 18,
        desc: "Healthcare vocabulary for clinical environments.",
        hrs: "4 hrs",
        pct: 12,
        cat: "Specialized",
      },
      {
        id: "6",
        title: "Numbers & Math Signs",
        difficulty: "Beginner",
        lessons: 10,
        desc: "Counting, arithmetic, and quantities.",
        hrs: "2 hrs",
        pct: 45,
        cat: "ASL",
      },
    ]);
  }

  return request("/courses");
}


export async function getCourseById(id) {
  if (USE_MOCKS) {
    return delay({
      id,
      title: "Alphabet Basics",
      difficulty: "Beginner",
      description:
        "Learn the alphabet in sign language.",
    });
  }

  return request(`/courses/${id}`);
}


export async function getLessons(moduleId) {
  if (USE_MOCKS) {
    return delay([
      {
        lesson_id: 1,
        module_id: 1,
        title: "Letter A",
        description:
          "Introduction to the sign for A",
        sequence_order: 1,
        difficulty_level: "beginner",
        is_published: true,
        created_at: new Date().toISOString(),
      },
      {
        lesson_id: 2,
        module_id: 1,
        title: "Letter B",
        description:
          "Introduction to the sign for B",
        sequence_order: 2,
        difficulty_level: "beginner",
        is_published: true,
        created_at: new Date().toISOString(),
      },
    ]);
  }

  const qs = moduleId
    ? `?module_id=${moduleId}`
    : "";

  return request(`/courses/lessons${qs}`);
}


export async function getLessonById(id) {
  if (USE_MOCKS) {
    return delay({
      lesson_id: id,
      module_id: 1,
      title: "Letter A",
      description:
        "Introduction to the sign for A",
      sequence_order: 1,
      difficulty_level: "beginner",
      is_published: true,
      created_at: new Date().toISOString(),
    });
  }

  return request(`/courses/lessons/${id}`);
}


export async function createLesson(data) {
  return request("/courses/lessons", {
    method: "POST",
    body: JSON.stringify(data),
  });
}


export async function updateLesson(id, data) {
  return request(`/courses/lessons/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}


export async function deleteLesson(id) {
  return request(`/courses/lessons/${id}`, {
    method: "DELETE",
  });
}


// ─────────────────────────────────────────────────────────────
// INSTRUCTOR
// ─────────────────────────────────────────────────────────────

export async function getMyStudents() {
  if (USE_MOCKS) {
    return delay([
      {
        user_id:
          "00000000-0000-0000-0000-000000000010",
        full_name: "Marcus Johnson",
        email: "marcus@example.com",
      },
      {
        user_id:
          "00000000-0000-0000-0000-000000000011",
        full_name: "Priya Patel",
        email: "priya@example.com",
      },
      {
        user_id:
          "00000000-0000-0000-0000-000000000012",
        full_name: "Leo Finch",
        email: "leo@example.com",
      },
      {
        user_id:
          "00000000-0000-0000-0000-000000000013",
        full_name: "Amara Osei",
        email: "amara@example.com",
      },
      {
        user_id:
          "00000000-0000-0000-0000-000000000014",
        full_name: "Tom Nguyen",
        email: "tom@example.com",
      },
    ]);
  }

  return request("/instructor/students");
}


export async function assignStudent(learnerId) {
  if (USE_MOCKS) {
    return delay({
      message: "Student assigned",
    });
  }

  return request(
    `/instructor/assign-student/${learnerId}`,
    {
      method: "POST",
    }
  );
}


// ─────────────────────────────────────────────────────────────
// ADMIN
// ─────────────────────────────────────────────────────────────

export async function adminListUsers() {
  if (USE_MOCKS) {
    return delay([
      {
        user_id: "1",
        full_name: "Maya Chen",
        email: "maya@example.com",
        is_active: true,
        roles: ["learner"],
      },
      {
        user_id: "2",
        full_name: "Marcus Johnson",
        email: "marcus@example.com",
        is_active: true,
        roles: ["learner"],
      },
      {
        user_id: "3",
        full_name: "Dr. Anya Roberts",
        email: "anya@example.com",
        is_active: true,
        roles: ["instructor"],
      },
      {
        user_id: "4",
        full_name: "Priya Patel",
        email: "priya@example.com",
        is_active: false,
        roles: ["learner"],
      },
      {
        user_id: "5",
        full_name: "Leo Finch",
        email: "leo@example.com",
        is_active: true,
        roles: ["learner"],
      },
      {
        user_id: "6",
        full_name: "Admin User",
        email: "admin@example.com",
        is_active: true,
        roles: ["admin"],
      },
      {
        user_id: "7",
        full_name: "Trainer User",
        email: "trainer@example.com",
        is_active: true,
        roles: ["trainer"],
      },
    ]);
  }

  return request("/admin/users");
}


export async function adminToggleUserStatus(
  userId,
  isActive
) {
  if (USE_MOCKS) {
    return delay({
      message: isActive
        ? "User activated"
        : "User deactivated",
    });
  }

  return request(
    `/admin/users/${userId}/status?is_active=${isActive}`,
    {
      method: "PATCH",
    }
  );
}


export async function adminChangeUserRole(
  userId,
  roleName
) {
  if (USE_MOCKS) {
    return delay({
      message: `Role '${roleName}' added to user`,
    });
  }

  return request(
    `/admin/users/${userId}/role?role_name=${encodeURIComponent(
      roleName
    )}`,
    {
      method: "PATCH",
    }
  );
}


export async function adminBulkAction(
  action,
  userIds
) {
  if (USE_MOCKS) {
    return delay({
      updated_count: userIds.length,
      failed_ids: [],
    });
  }

  return request("/admin/users/bulk-action", {
    method: "POST",
    body: JSON.stringify({
      action,
      user_ids: userIds,
    }),
  });
}


export async function adminBulkUploadLessons(
  csvFile
) {
  const token = getToken();

  const formData = new FormData();

  formData.append(
    "file",
    csvFile,
    csvFile.name
  );

  const res = await fetch(
    `${BASE_URL}/admin/lessons/bulk-upload`,
    {
      method: "POST",
      headers: {
        ...(token
          ? {
              Authorization: `Bearer ${token}`,
            }
          : {}),
      },
      body: formData,
    }
  );

  if (!res.ok) {
    const text = await res.text().catch(() => "");

    throw new Error(
      `Bulk upload failed: ${res.status} ${text}`
    );
  }

  return res.json();
}