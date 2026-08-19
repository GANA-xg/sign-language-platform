import {
  Navigate,
  Outlet,
  useOutletContext,
} from "react-router";

import { useAuth } from "../context/AuthContext";
import type { Role } from "../utils/types";

const ROLE_HOME: Record<Role, string> = {
  learner: "/dashboard",
  instructor: "/instructor",
  trainer: "/trainer",
  admin: "/admin",
};

export function RoleRoute({
  allow,
}: {
  allow: Role[];
}) {
  const { role, loading } = useAuth();

  const ctx = useOutletContext<{
    go: Function;
  }>();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-muted-foreground text-sm">
        Loading...
      </div>
    );
  }

  if (!allow.includes(role)) {
    return (
      <Navigate
        to={ROLE_HOME[role] ?? "/dashboard"}
        replace
      />
    );
  }

  return <Outlet context={ctx} />;
}