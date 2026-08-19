import { useState, useEffect } from "react";
import { Users, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp, RefreshCw, Server } from "lucide-react";

const BUSINESS_BASE_URL = import.meta.env.VITE_BUSINESS_API_URL ?? "https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com";
const AI_BASE_URL = import.meta.env.VITE_AI_API_URL ?? "https://ai-signlanguage-platform-si7-team-one-58ie.onrender.com";
const BACKEND_BASE_URL = import.meta.env.VITE_API_URL ?? "https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com";

interface ServiceHealth {
  name: string;
  icon: any;
  healthy: boolean;
  uptime: string;
  lat: number;
  err: number;
  rps: string;
}

export default function SystemMonitoring() {
  const [services, setServices] = useState<ServiceHealth[]>([]);
  const [loading, setLoading] = useState(true);

  const checkServices = async () => {
    setLoading(true);
    const results: ServiceHealth[] = [];

    const check = async (
      name: string,
      icon: any,
      url: string,
      defaultRps: string
    ) => {
      const start = Date.now();
      try {
        const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
        const lat = Date.now() - start;
        results.push({
          name,
          icon,
          healthy: res.ok,
          uptime: res.ok ? "99.9%" : "Degraded",
          lat,
          err: res.ok ? 0.01 : 1.8,
          rps: defaultRps,
        });
      } catch {
        const lat = Date.now() - start;
        results.push({
          name,
          icon,
          healthy: false,
          uptime: "Unreachable",
          lat,
          err: 100,
          rps: "0",
        });
      }
    };

    await Promise.all([
      check("Backend API (Auth)", Users, `${BACKEND_BASE_URL}/health`, "—"),
      check("Business Logic", TrendingUp, `${BUSINESS_BASE_URL}/health`, "—"),
      check("AI/ML Service", Camera, `${AI_BASE_URL}/health`, "—"),
    ]);

    setServices(results);
    setLoading(false);
  };

  useEffect(() => {
    checkServices();
    const interval = setInterval(checkServices, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">System Monitoring</h2>
          <p className="text-muted-foreground text-sm">Live health status of all services</p>
        </div>
        <button
          onClick={checkServices}
          className="flex items-center gap-2 border border-border bg-muted hover:bg-hover text-foreground text-xs font-bold px-4 py-2.5 rounded-xl transition-colors"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </div>

      {loading && services.length === 0 ? (
        <div className="grid grid-cols-3 gap-5">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-card rounded-[14px] p-5 border border-border animate-pulse">
              <div className="h-4 bg-surface rounded w-1/2 mb-4" />
              <div className="h-3 bg-surface rounded w-3/4" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {services.map((svc) => {
            const Icon = svc.icon;
            return (
              <div
                key={svc.name}
                className={`bg-card rounded-[14px] p-5 border ${svc.healthy ? "border-border" : "border-warning/30 bg-warning/5"}`}
                style={{ boxShadow: "var(--card-shadow)" }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-muted flex items-center justify-center flex-shrink-0">
                    <Icon size={15} className="text-muted-foreground" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-foreground truncate">{svc.name}</div>
                    <div className={`text-xs font-semibold ${svc.healthy ? "text-success" : "text-warning"}`}>
                      {svc.healthy ? "● Healthy" : "● Degraded"}
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <div className="text-muted-foreground">Latency</div>
                    <div className={`font-bold ${svc.lat > 200 ? "text-warning" : "text-foreground"}`}>{svc.lat}ms</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Status</div>
                    <div className={`font-bold ${svc.healthy ? "text-foreground" : "text-warning"}`}>{svc.uptime}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
