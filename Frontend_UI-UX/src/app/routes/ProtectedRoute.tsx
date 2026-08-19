import { Navigate, Outlet } from "react-router";
import { useAuth } from "../context/AuthContext";

// Wraps /dashboard, /courses, /practice, etc. Redirects unauthenticated
// users to /login, per SRS item: "route protection not done yet".
export function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-muted-foreground text-sm">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
