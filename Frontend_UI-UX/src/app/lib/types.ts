export type Screen =
  | "login" | "signup" | "onboarding"
  | "learner-dashboard" | "courses" | "lesson" | "practice"
  | "assessment" | "feedback" | "progress" | "certificates"
  | "leaderboard"
  | "instructor-dashboard" | "course-management" | "student-detail"
  | "trainer-console" | "trainer-dashboard"
  | "admin-dashboard" | "user-management" | "system-monitoring"
  | "notifications" | "settings" | "camera-permission"
  | "certification-exam";
export type Role = "learner" | "instructor" | "trainer" | "admin";
export type BadgeVariant = "default" | "success" | "warning" | "error" | "info";
export type MColor = "cyan" | "emerald" | "violet" | "amber";