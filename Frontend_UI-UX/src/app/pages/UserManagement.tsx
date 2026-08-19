import { useState, useEffect } from "react";
import {
  Users, Plus, Search, AlertTriangle, RefreshCw, Loader2,
} from "lucide-react";
import { Bdg } from "../components/shared/Indicators";
import { adminListUsers, adminToggleUserStatus, adminChangeUserRole } from "../services/api";
import type { Role } from "@/app/utils/types";

interface BackendUser {
  user_id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  roles: string[];
}

// Map backend role strings to frontend Role type for display
function displayRole(roles: string[]): string {
  if (roles.includes("admin")) {
    return "admin";
  }

  if (roles.includes("instructor")) {
    return "instructor";
  }

  if (roles.includes("trainer")) {
    return "trainer";
  }

  return "learner";
}

export default function UserManagement() {
  const [search, setSearch] = useState("");
  const [users, setUsers] = useState<BackendUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toggling, setToggling] = useState<string | null>(null); // user_id being toggled

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = () => {
    setLoading(true);
    setError(null);
    adminListUsers()
      .then(data => setUsers(data ?? []))
      .catch(() => setError("Couldn't load users. The backend is unreachable."))
      .finally(() => setLoading(false));
  };

  const handleToggleStatus = async (userId: string, currentlyActive: boolean) => {
    setToggling(userId);
    try {
      await adminToggleUserStatus(userId, !currentlyActive);
      setUsers(prev =>
        prev.map(u => u.user_id === userId ? { ...u, is_active: !currentlyActive } : u)
      );
    } catch (e) {
      alert(`Failed to ${currentlyActive ? "deactivate" : "activate"} user.`);
    } finally {
      setToggling(null);
    }
  };

  const filtered = users.filter(u =>
    u.full_name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full bg-card border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
            placeholder="Search users…"
          />
        </div>
        <button
          onClick={loadUsers}
          className="flex items-center gap-2 bg-muted border border-border hover:bg-hover text-foreground text-xs font-semibold px-4 py-2.5 rounded-xl transition-colors"
        >
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-16">
          <RefreshCw size={20} className="animate-spin text-muted-foreground" />
        </div>
      )}

      {!loading && error && (
        <div className="flex items-center gap-2 py-8 text-sm text-rose-400">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {!loading && !error && (
        <div className="bg-card border border-border rounded-[14px] overflow-hidden" style={{ boxShadow: 'var(--card-shadow)' }}>
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                {["User", "Role", "Status", "Actions"].map((h, i) => (
                  <th key={i} className={`text-xs font-semibold text-muted-foreground p-4 ${i === 3 ? "text-right" : "text-left"}`}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-xs text-muted-foreground">
                    {users.length === 0 ? "No users found." : `No users match "${search}"`}
                  </td>
                </tr>
              )}
              {filtered.map((u, i) => {
                const role = displayRole(u.roles);
                return (
                  <tr key={u.user_id} className={`border-b border-border/50 hover:bg-muted/50 transition-colors ${i === filtered.length - 1 ? "border-0" : ""}`}>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary/70 to-primary/40 flex items-center justify-center text-xs font-bold text-primary-foreground">
                          {u.full_name.charAt(0)}
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-foreground">{u.full_name}</div>
                          <div className="text-xs text-muted-foreground">{u.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <Bdg
                        label={role.charAt(0).toUpperCase() + role.slice(1)}
                        v={role === "admin" ? "warning" : role === "instructor" ? "info" : role === "trainer" ? "success" : "default"}
                      />
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1.5">
                        <div className={`w-1.5 h-1.5 rounded-full ${u.is_active ? "bg-success" : "bg-muted-foreground"}`} />
                        <span className="text-xs text-muted-foreground capitalize">{u.is_active ? "active" : "inactive"}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleToggleStatus(u.user_id, u.is_active)}
                          disabled={toggling === u.user_id}
                          className={`text-xs px-2.5 py-1.5 rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1 ${
                            u.is_active
                              ? "text-rose-400 hover:bg-rose-950/30"
                              : "text-emerald-400 hover:bg-emerald-950/30"
                          }`}
                        >
                          {toggling === u.user_id && <Loader2 size={10} className="animate-spin" />}
                          {u.is_active ? "Deactivate" : "Activate"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <div className="text-xs text-muted-foreground">
        {!loading && `${filtered.length} of ${users.length} users`}
      </div>
    </div>
  );
}