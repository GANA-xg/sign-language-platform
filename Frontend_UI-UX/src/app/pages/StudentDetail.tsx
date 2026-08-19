import { useState, useEffect } from "react";
import { TrendingUp, Target, Clock, Calendar, RefreshCw, AlertTriangle, Users } from "lucide-react";
import { MCard } from "../components/shared/MCard";
import { Bdg } from "../components/shared/Indicators";
import { getMyStudents } from "../services/api";
import { useAuth } from "../context/AuthContext";

interface Student {
  user_id: string;
  full_name: string;
  email: string;
}

interface StudentAnalytics {
  learner_id: string;
  sessions_this_week: number;
  engagement_level: string;
  avg_assessment_score: number;
  skill_development_trend: number | null;
  certification_status: string;
}

export default function StudentDetail() {
  const { userId } = useAuth();
  const [students, setStudents] = useState<Student[]>([]);
  const [selected, setSelected] = useState<Student | null>(null);
  const [analytics, setAnalytics] = useState<StudentAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    getMyStudents()
      .then((data) => {
        setStudents(data ?? []);
        if (data && data.length > 0) setSelected(data[0]);
      })
      .catch(() => setError("Couldn't load students. Is the Backend API running on port 8000?"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected || !userId) return;
    setAnalyticsLoading(true);
    fetch(`${import.meta.env.VITE_BUSINESS_API_URL ?? "http://127.0.0.1:8002"}/trainer/${userId}/learners/${selected.user_id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token") ?? ""}` },
    })
      .then((r) => r.ok ? r.json() : null)
      .then((data) => setAnalytics(data))
      .catch(() => setAnalytics(null))
      .finally(() => setAnalyticsLoading(false));
  }, [selected, userId]);

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Users size={20} className="text-muted-foreground" />
        <div>
          <h2 className="text-xl font-bold text-foreground">Student Details</h2>
          <p className="text-muted-foreground text-sm">View learner analytics and assessment data</p>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <RefreshCw size={18} className="animate-spin text-muted-foreground" />
        </div>
      )}

      {!loading && error && (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <AlertTriangle size={28} className="text-rose-400" />
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      )}

      {!loading && !error && students.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-16 text-center">
          <Users size={28} className="text-muted-foreground" />
          <p className="text-sm text-muted-foreground">No students assigned yet. Go to Instructor Dashboard to assign learners.</p>
        </div>
      )}

      {!loading && !error && students.length > 0 && (
        <>
          {/* Student selector */}
          <div className="flex gap-2 flex-wrap">
            {students.map((s) => (
              <button
                key={s.user_id}
                onClick={() => setSelected(s)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  selected?.user_id === s.user_id
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted border border-border text-foreground hover:bg-hover"
                }`}
              >
                {s.full_name}
              </button>
            ))}
          </div>

          {selected && (
            <>
              {/* Student header */}
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary/70 to-primary/40 flex items-center justify-center text-xl font-bold text-primary-foreground">
                  {selected.full_name.charAt(0)}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-foreground">{selected.full_name}</h2>
                  <p className="text-muted-foreground text-sm">{selected.email}</p>
                </div>
                {analytics && (
                  <Bdg
                    label={analytics.engagement_level}
                    v={analytics.engagement_level === "High" ? "success" : analytics.engagement_level === "Medium" ? "warning" : "error"}
                  />
                )}
              </div>

              {/* Analytics cards */}
              {analyticsLoading ? (
                <div className="flex items-center gap-2 py-6 text-sm text-muted-foreground">
                  <RefreshCw size={14} className="animate-spin" /> Loading analytics...
                </div>
              ) : analytics ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
                  <MCard icon={TrendingUp} label="Sessions This Week" value={String(analytics.sessions_this_week)} col="cyan" />
                  <MCard icon={Target} label="Avg Assessment Score" value={`${Math.round(analytics.avg_assessment_score)}%`} col="emerald" />
                  <MCard icon={Calendar} label="Engagement" value={analytics.engagement_level} col="amber" />
                  <MCard icon={Clock} label="Certification" value={analytics.certification_status} col="violet" />
                </div>
              ) : (
                <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
                  <p className="text-sm text-muted-foreground">
                    No analytics data available for this student. They may not be assigned to you as a trainer yet.
                  </p>
                </div>
              )}

              {analytics && analytics.skill_development_trend !== null && (
                <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
                  <h3 className="font-semibold text-foreground mb-3 text-sm">Skill Development Trend</h3>
                  <div className={`text-2xl font-bold ${analytics.skill_development_trend >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                    {analytics.skill_development_trend >= 0 ? "+" : ""}{analytics.skill_development_trend}%
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">Improvement over time</p>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
