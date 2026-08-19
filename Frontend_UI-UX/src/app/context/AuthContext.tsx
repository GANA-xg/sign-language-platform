import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { Role } from "../lib/types";
import { logoutUser } from "../services/api";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface AuthState {
  isAuthenticated: boolean;
  role: Role;
  userId: string | null; // real UUID from backend's UserResponse — needed by
                          // Business Logic's /practice/start (user_id: UUID)
  
  fullName: string | null;
  loading: boolean;
  login: (role: Role, token?: string, userId?: string, fullName?: string) => void;
  logout: () => void;
  setRole: (r: Role) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [role, setRoleState] = useState<Role>("learner");
  const [userId, setUserId] = useState<string | null>(null);
  const [fullName, setFullName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedRole = localStorage.getItem("role") as Role | null;
    const storedUserId = localStorage.getItem("user_id");

    if (!token) {
      setLoading(false);
      return;
    }

    // Restore session immediately from localStorage — user stays logged in
    // while we verify in the background.
    setIsAuthenticated(true);
    setRoleState(storedRole || "learner");
    setUserId(storedUserId);

    // Verify token with the backend. Only force-logout on a real 401/403
    // (bad/expired token). Network errors or 5xx keep the session alive so
    // a backend restart or flaky connection doesn't log the user out.
    fetch(`${BASE_URL}/auth/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (res.status === 401 || res.status === 403) {
          // Token is genuinely invalid — log out.
          logoutUser();
          setIsAuthenticated(false);
          return null;
        }
        return res.ok ? res.json() : null;
      })
      .then((profile) => {
        if (profile?.full_name) setFullName(profile.full_name);
      })
      .catch(() => {
        // Network error / backend down — keep session, don't log out.
      })
      .finally(() => setLoading(false));
  }, []);

  const login = (r: Role, token?: string, uid?: string, name?: string) => {
    if (token) localStorage.setItem("token", token);
    localStorage.setItem("role", r);
    setRoleState(r);
    if (uid) {
      localStorage.setItem("user_id", uid);
      setUserId(uid);
    }
    if (name) setFullName(name);
    setIsAuthenticated(true);
  };

  const logout = () => {
    logoutUser();
    localStorage.removeItem("user_id");
    setUserId(null);
    setIsAuthenticated(false);
  };

  const setRole = (r: Role) => {
    localStorage.setItem("role", r);
    setRoleState(r);
  };

  return (
      <AuthContext.Provider value={{ isAuthenticated, role, userId, fullName, loading, login, logout, setRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}