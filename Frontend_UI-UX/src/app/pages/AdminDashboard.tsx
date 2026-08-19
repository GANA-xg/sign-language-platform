import { useState, useEffect } from "react";
import {
  Users, TrendingUp, Activity, Search, Server,
} from "lucide-react";
import {
  AreaChart, Area, ResponsiveContainer, XAxis, YAxis,
  CartesianGrid, Tooltip,
} from "recharts";
import { MCard } from "../components/shared/MCard";
import { Bdg } from "../components/shared/Indicators";
import { useIsDark } from "../lib/useIsDark";
import {
  adminListUsers,
  adminToggleUserStatus,
} from "../services/api";

const BUSINESS_BASE_URL = import.meta.env.VITE_BUSINESS_API_URL ?? "http://127.0.0.1:8002";
const AI_BASE_URL = import.meta.env.VITE_AI_API_URL ?? "http://127.0.0.1:8001";

interface BackendUser {
  user_id: string;
  full_name: string;
  email: string;
  is_active: boolean;
  roles: string[];
}

interface ServiceStatus {
  name: string;
  healthy: boolean;
  uptime: string;
  rps: string;
}

export default function AdminDashboard() {
  const dark = useIsDark();
  const grid = dark ? "rgba(255,255,255,0.05)" : "#EBEBEB";
  const tick = dark ? "#9CA3AF" : "#6A6A6A";
  const tipBg = dark ? "#1C1C1E" : "#FFFFFF";
  const tipBorder = dark ? "rgba(255,255,255,0.08)" : "#DDDDDD";

  const [users, setUsers] = useState<BackendUser[]>([]);
  const [userSearch, setUserSearch] = useState("");
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [services, setServices] = useState<ServiceStatus[]>([]);

  useEffect(() => {
    adminListUsers()
      .then((data) => setUsers(data ?? []))
      .catch(() => setUsers([]))
      .finally(() => setLoadingUsers(false));
  }, []);

  useEffect(() => {
    const checkServices = async () => {
      const results: ServiceStatus[] = [];

      const check = async (name: string, url: string, fallbackRps: string) => {
        try {
          const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
          results.push({ name, healthy: res.ok, uptime: res.ok ? "99.9%" : "Degraded", rps: fallbackRps });
        } catch {
          results.push({ name, healthy: false, uptime: "Unreachable", rps: fallbackRps });
        }
      };

      await Promise.all([
        check("Backend API", "http://localhost:8000/health", "—"),
        check("Business Logic", `${BUSINESS_BASE_URL}/health`, "—"),
        check("AI/ML Service", `${AI_BASE_URL}/health`, "—"),
      ]);

      setServices(results);
    };

    checkServices();
    const interval = setInterval(checkServices, 30000);
    return () => clearInterval(interval);
  }, []);

  const activeUsers = users.filter((u) => u.is_active).length;
  const totalUsers = users.length;

  const filteredUsers = users.filter((user) => {
    const query = userSearch.trim().toLowerCase();
    if (!query) return true;
    return user.full_name.toLowerCase().includes(query) || user.email.toLowerCase().includes(query);
  });

  const getRole = (roles: string[]): string => {
    if (roles.includes("admin")) return "admin";
    if (roles.includes("instructor")) return "instructor";
    if (roles.includes("trainer")) return "trainer";
    return "learner";
  };

  const toggleActive = async (userId: string, currentlyActive: boolean) => {
    try {
      await adminToggleUserStatus(userId, !currentlyActive);
      setUsers((prev) =>
        prev.map((u) => (u.user_id === userId ? { ...u, is_active: !currentlyActive } : u))
      );
    } catch {
      // keep current state
    }
  };

  const healthyCount = services.filter((s) => s.healthy).length;

  return (
    <div className="p-4 md:p-8 space-y-6 md:space-y-8 max-w-7xl mx-auto">

      {/* STATS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
        <MCard
          icon={Users}
          label="Total Users"
          value={loadingUsers ? "…" : String(totalUsers)}
          delta={`${activeUsers} active`}
          col="cyan"
        />
        <MCard
          icon={Server}
          label="Services Healthy"
          value={services.length > 0 ? `${healthyCount}/${services.length}` : "…"}
          delta={services.length > 0 ? (healthyCount === services.length ? "All nominal" : "Degraded") : "Checking..."}
          col={healthyCount === services.length ? "emerald" : "amber"}
        />
        <MCard
          icon={Activity}
          label="Backend API"
          value={services.find(s => s.name === "Backend API")?.healthy ? "Online" : "Offline"}
          delta={services.find(s => s.name === "Backend API")?.uptime ?? "Checking..."}
          col={services.find(s => s.name === "Backend API")?.healthy ? "emerald" : "amber"}
        />
        <MCard
          icon={TrendingUp}
          label="AI/ML Service"
          value={services.find(s => s.name === "AI/ML Service")?.healthy ? "Online" : "Offline"}
          delta={services.find(s => s.name === "AI/ML Service")?.uptime ?? "Checking..."}
          col={services.find(s => s.name === "AI/ML Service")?.healthy ? "emerald" : "amber"}
        />
      </div>

      {/* SERVICE STATUS */}
      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
        <h3 className="font-semibold text-foreground mb-5 text-sm">Service Status</h3>
        {services.length === 0 ? (
          <div className="py-4 text-center text-xs text-muted-foreground">Checking services...</div>
        ) : (
          <div className="space-y-3">
            {services.map((service) => (
              <div key={service.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <Server size={14} className="text-muted-foreground" />
                  <span className="text-xs text-foreground">{service.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground">{service.rps}</span>
                  <span className="text-xs text-muted-foreground">{service.uptime}</span>
                  <div className={`w-2 h-2 rounded-full ${service.healthy ? "bg-emerald-400" : "bg-rose-400"}`} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* USER MANAGEMENT */}
      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-semibold text-foreground text-sm">User Management</h3>
          <div className="relative">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              value={userSearch}
              onChange={(event) => setUserSearch(event.target.value)}
              placeholder="Search users…"
              className="bg-muted border border-border rounded-xl pl-8 pr-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary/50 w-48"
            />
          </div>
        </div>

        {loadingUsers ? (
          <div className="py-8 text-center text-xs text-muted-foreground">Loading users…</div>
        ) : (
          <div className="space-y-2">
            {filteredUsers.map((user) => {
              const roleStr = getRole(user.roles);
              const roleLabel = roleStr.charAt(0).toUpperCase() + roleStr.slice(1);
              const roleVariant =
                roleStr === "admin" ? "warning"
                : roleStr === "instructor" ? "info"
                : roleStr === "trainer" ? "success"
                : "default";

              return (
                <div key={user.user_id} className="flex items-center gap-3 p-3 rounded-xl hover:bg-muted/50 transition-colors">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary/70 to-primary/40 flex items-center justify-center text-xs font-bold text-primary-foreground flex-shrink-0">
                    {user.full_name?.charAt(0)?.toUpperCase() ?? "U"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-foreground truncate">{user.full_name}</div>
                    <div className="text-[10px] text-muted-foreground truncate">{user.email}</div>
                  </div>
                  <Bdg label={roleLabel} v={roleVariant} />
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${user.is_active ? "bg-emerald-400" : "bg-muted-foreground"}`} />
                  <button
                    onClick={() => toggleActive(user.user_id, user.is_active)}
                    className={`text-[10px] px-2 py-1 rounded-lg transition-colors flex-shrink-0 ${
                      user.is_active
                        ? "text-rose-400 hover:bg-rose-950/30"
                        : "text-emerald-400 hover:bg-emerald-950/30"
                    }`}
                  >
                    {user.is_active ? "Deactivate" : "Activate"}
                  </button>
                </div>
              );
            })}

            {filteredUsers.length === 0 && (
              <div className="py-6 text-center text-xs text-muted-foreground">
                {users.length === 0 ? "No users found — backend may not be running." : `No users match "${userSearch}"`}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
