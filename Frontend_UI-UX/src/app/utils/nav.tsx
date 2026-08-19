import {
  Home,
  BookOpen,
  Camera,
  CheckSquare,
  TrendingUp,
  Award,
  Users,
  Server,
  Trophy,
} from "lucide-react";

import type {
  Role,
  Screen,
} from "./types";


export const NAV: Record<
  Role,
  {
    screen: Screen;
    label: string;
    icon: React.ElementType;
  }[]
> = {
  learner: [
    {
      screen: "learner-dashboard",
      label: "Dashboard",
      icon: Home,
    },
    {
      screen: "courses",
      label: "Courses",
      icon: BookOpen,
    },
    {
      screen: "practice",
      label: "Practice",
      icon: Camera,
    },
    {
      screen: "assessment",
      label: "Assessments",
      icon: CheckSquare,
    },
    {
      screen: "progress",
      label: "Progress",
      icon: TrendingUp,
    },
    {
      screen: "certificates",
      label: "Certificates",
      icon: Award,
    },
    {
      screen: "leaderboard",
      label: "Leaderboard",
      icon: Trophy,
    },
    {
      screen: "certification-exam",
      label: "Certification",
      icon: Award,
    },
  ],

  instructor: [
    {
      screen: "instructor-dashboard",
      label: "Dashboard",
      icon: Home,
    },
    {
      screen: "course-management",
      label: "Courses",
      icon: BookOpen,
    },
    {
      screen: "student-detail",
      label: "Students",
      icon: Users,
    },
  ],

  trainer: [
    {
      screen: "trainer-dashboard",
      label: "Dashboard",
      icon: Home,
    },
  ],

  admin: [
    {
      screen: "admin-dashboard",
      label: "Dashboard",
      icon: Home,
    },
    {
      screen: "user-management",
      label: "Users",
      icon: Users,
    },
    {
      screen: "system-monitoring",
      label: "System",
      icon: Server,
    },
  ],
};


export const SCREEN_LABELS: Record<
  Screen,
  string
> = {
  login: "Login",
  signup: "Sign Up",
  onboarding: "Onboarding",

  "learner-dashboard": "Dashboard",
  courses: "Course Catalog",
  lesson: "Lesson View",
  practice: "Practice",
  assessment: "Assessment",
  feedback: "AI Feedback",
  progress: "Progress & Analytics",
  certificates: "Certificates",
  leaderboard: "Leaderboard",

  "instructor-dashboard":
    "Instructor Dashboard",

  "course-management":
    "Course Management",

  "student-detail":
    "Student Detail",

  "trainer-console":
    "Trainer Console",

  "trainer-dashboard":
    "Accessibility Trainer Dashboard",

  "admin-dashboard":
    "Admin Dashboard",

  "user-management":
    "User Management",

  "system-monitoring":
    "System Monitoring",

  notifications: "Notifications",
  settings: "Settings",

  "camera-permission":
    "Camera Permission",

  "certification-exam":
    "Certification Exam",
};


export const ROLE_CLS: Record<
  Role,
  string
> = {
  learner:
    "bg-primary/10 text-primary",

  instructor:
    "bg-muted text-foreground",

  trainer:
    "bg-success/10 text-success",

  admin:
    "bg-warning/10 text-warning",
};


export const SCREEN_PATH: Record<
  Screen,
  string
> = {
  login: "/login",
  signup: "/signup",
  onboarding: "/onboarding",

  "learner-dashboard":
    "/dashboard",

  courses: "/courses",

  lesson:
    "/courses/lesson",

  practice: "/practice",

  assessment: "/assessment",

  feedback: "/feedback",

  progress: "/progress",

  certificates:
    "/certificates",

  leaderboard:
    "/leaderboard",

  "instructor-dashboard":
    "/instructor",

  "course-management":
    "/instructor/courses",

  "student-detail":
    "/instructor/students",

  "trainer-console":
    "/trainer-console",

  // IMPORTANT:
  // Trainer frontend route is now /trainer.
  "trainer-dashboard":
    "/trainer",

  "admin-dashboard":
    "/admin",

  "user-management":
    "/admin/users",

  "system-monitoring":
    "/admin/system",

  notifications:
    "/notifications",

  settings:
    "/settings",

  "camera-permission":
    "/camera-permission",

  "certification-exam":
    "/certification-exam",
};


export const PATH_SCREEN: Record<
  string,
  Screen
> = Object.fromEntries(
  Object.entries(
    SCREEN_PATH
  ).map(
    ([screen, path]) => [
      path,
      screen as Screen,
    ]
  )
) as Record<
  string,
  Screen
>;