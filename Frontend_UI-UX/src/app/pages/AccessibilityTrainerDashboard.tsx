import { useState, useEffect } from "react";
import {
  Users, TrendingUp, Award, CheckCircle, AlertTriangle,
  Activity, Search, ChevronRight, Loader2,
} from "lucide-react";
import { MCard } from "../components/shared/MCard";
import { Bdg, PBar } from "../components/shared/Indicators";
import { useAuth } from "../context/AuthContext";
import {
  assignLearnerToTrainer,
  getTrainerDashboard,
} from "../services/businessApi";

// M4 Day 3 — wired to real data via GET /trainer/{trainer_id}/dashboard
// (trainer_analytics.py, confirmed against real router + schema). Backend
// sends engagement_level/certification_status as "High"/"Medium"/"Low" and
// "Certified"/"In Progress"/"Not Started" — normalized below to the UI's
// existing lowercase/hyphenated variants so EngagementBdg/CertBdg and all
// styling stay untouched.
interface TraineeRow {
  name: string;
  engagement: "high" | "medium" | "low"; // how often they practice
  sessionsThisWeek: number;
  skillDevelopment: number | null; // % improvement over time; null = not enough data yet
  avgAssessmentScore: number;
  certificationStatus: "certified" | "in-progress" | "not-started";
}

type LearnerAnalytics = {
  learner_id: string;
  sessions_this_week: number;
  engagement_level: "High" | "Medium" | "Low";
  avg_assessment_score: number;
  skill_development_trend: number | null;
  certification_status: "Certified" | "In Progress" | "Not Started";
  highest_certified_level?: string | null;
};

function normalizeLearner(l: LearnerAnalytics): TraineeRow {
  return {
    // Backend only returns learner_id (UUID), not a display name yet — real
    // names need a lookup against Intern 2's user data, not
    // wired here. Using a shortened UUID as a placeholder for now.
    name: l.learner_id.slice(0, 8),
    engagement: l.engagement_level.toLowerCase() as TraineeRow["engagement"],
    sessionsThisWeek: l.sessions_this_week,
    skillDevelopment: l.skill_development_trend,
    avgAssessmentScore: Math.round(l.avg_assessment_score),
    certificationStatus:
      l.certification_status === "Certified" ? "certified" :
      l.certification_status === "In Progress" ? "in-progress" : "not-started",
  };
}

function EngagementBdg({ level }: { level: TraineeRow["engagement"] }) {
  const v = level === "high" ? "success" : level === "medium" ? "warning" : "error";
  return <Bdg label={level.charAt(0).toUpperCase() + level.slice(1)} v={v} />;
}

function CertBdg({ status }: { status: TraineeRow["certificationStatus"] }) {
  if (status === "certified") return <Bdg label="Certified" v="success" />;
  if (status === "in-progress") return <Bdg label="In Progress" v="info" />;
  return <Bdg label="Not Started" v="default" />;
}

export default function AccessibilityTrainerDashboard({ go }: { go: (s: any) => void }) {
  const { userId } = useAuth();
  const [search, setSearch] = useState("");
  const [learnerId, setLearnerId] = useState("");
  const [trainees, setTrainees] = useState<TraineeRow[]>([]);
  const [summary, setSummary] = useState({
    assignedCount: 0,
    avgSessions: 0,
    avgScore: 0,
    certifiedCount: 0,
    lowEngagementCount: 0,
  });
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assignError, setAssignError] = useState<string | null>(null);
  const [assignSuccess, setAssignSuccess] = useState<string | null>(null);

  const trainerId = userId ?? "00000000-0000-0000-0000-000000000000";

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getTrainerDashboard(trainerId);
        setTrainees((data.learners ?? []).map(normalizeLearner));
        setSummary({
          assignedCount: data.assigned_learners_count,
          avgSessions: Math.round(data.avg_sessions_per_week),
          avgScore: Math.round(data.avg_assessment_score),
          certifiedCount: data.certified_count,
          lowEngagementCount: data.low_engagement_count,
        });
      } catch (e) {
        setError("Couldn't load trainer dashboard. The Business Logic service is unreachable.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [trainerId]);

  const refreshDashboard = async () => {
    const data = await getTrainerDashboard(trainerId);
    setTrainees((data.learners ?? []).map(normalizeLearner));
    setSummary({
      assignedCount: data.assigned_learners_count,
      avgSessions: Math.round(data.avg_sessions_per_week),
      avgScore: Math.round(data.avg_assessment_score),
      certifiedCount: data.certified_count,
      lowEngagementCount: data.low_engagement_count,
    });
  };

  const handleAssignLearner = async () => {
    if (!learnerId.trim()) {
      setAssignError("Enter a learner UUID first.");
      return;
    }

    setAssigning(true);
    setAssignError(null);
    setAssignSuccess(null);

    try {
      await assignLearnerToTrainer(trainerId, learnerId.trim());
      await refreshDashboard();
      setAssignSuccess("Learner assigned successfully.");
      setLearnerId("");
    } catch (e) {
      setAssignError("Could not assign learner. Check the UUID and try again.");
    } finally {
      setAssigning(false);
    }
  };

  const filteredTrainees = trainees.filter(t =>
    t.name.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <Loader2 size={14} className="animate-spin" />
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return <div className="p-8 text-center text-rose-400 text-sm">{error}</div>;
  }

  return (
    <div className="p-8 space-y-6 max-w-6xl mx-auto">
      <div>
        <h2 className="text-lg font-bold text-foreground">Accessibility Trainer Dashboard</h2>
        <p className="text-muted-foreground text-sm">Learner engagement, skill development, and certification monitoring</p>
      </div>

      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: 'var(--card-shadow)' }}>
        <div className="flex flex-col lg:flex-row lg:items-end gap-3">
          <div className="flex-1">
            <label className="block text-xs font-semibold text-foreground mb-2">Assign learner by UUID</label>
            <input
              value={learnerId}
              onChange={e => setLearnerId(e.target.value)}
              placeholder="Paste learner UUID here"
              className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
            />
          </div>
          <button
            type="button"
            onClick={handleAssignLearner}
            disabled={assigning}
            className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
          >
            {assigning ? "Assigning..." : "Assign Learner"}
          </button>
        </div>
        <div className="mt-3 text-xs text-muted-foreground">
          Use this after creating a learner account. The dashboard will refresh immediately after assignment.
        </div>
        {assignError && (
          <div className="mt-3 text-sm text-rose-400">{assignError}</div>
        )}
        {assignSuccess && (
          <div className="mt-3 text-sm text-emerald-400">{assignSuccess}</div>
        )}
      </div>

      {/* Assessment analytics summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
        <MCard icon={Users}       label="Assigned Learners"    value={String(summary.assignedCount)} col="cyan" />
        <MCard icon={Activity}    label="Avg Sessions / Week"  value={String(summary.avgSessions)} col="violet" />
        <MCard icon={TrendingUp}  label="Avg Assessment Score" value={`${summary.avgScore}%`} col="emerald" />
        <MCard icon={Award}       label="Certified"            value={`${summary.certifiedCount}/${summary.assignedCount}`} col="amber" />
      </div>

      {summary.lowEngagementCount > 0 && (
        <div className="flex items-center gap-2.5 bg-warning/5 border border-warning/30 rounded-xl px-4 py-3">
          <AlertTriangle size={15} className="text-warning flex-shrink-0" />
          <span className="text-sm text-foreground">
            {summary.lowEngagementCount} learner{summary.lowEngagementCount > 1 ? "s" : ""} showing low engagement this week — may need outreach.
          </span>
        </div>
      )}

      {/* Learner engagement / skill development / certification table */}
      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: 'var(--card-shadow)' }}>
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-semibold text-foreground text-sm">Assigned Learners</h3>
          <div className="relative">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search learners..."
              className="bg-muted border border-border rounded-xl pl-8 pr-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary/50 w-48"
            />
          </div>
        </div>

        {trainees.length === 0 ? (
          <p className="text-xs text-muted-foreground py-6 text-center">
            No learners assigned to you yet.
          </p>
        ) : filteredTrainees.length === 0 ? (
          <p className="text-xs text-muted-foreground py-6 text-center">No learners match "{search}"</p>
        ) : (
          <div className="space-y-2">
            {filteredTrainees.map(t => (
              <div key={t.name} className="flex items-center gap-4 p-3.5 rounded-xl bg-muted/50 border border-border/50">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary/70 to-primary/40 flex items-center justify-center text-xs font-bold text-primary-foreground flex-shrink-0">
                  {t.name.charAt(0)}
                </div>
                <div className="w-36 flex-shrink-0">
                  <div className="text-sm font-semibold text-foreground">{t.name}</div>
                  <div className="text-xs text-muted-foreground">{t.sessionsThisWeek} sessions this week</div>
                </div>

                <div className="w-24 flex-shrink-0">
                  <div className="text-xs text-muted-foreground mb-1">Engagement</div>
                  <EngagementBdg level={t.engagement} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-muted-foreground">Skill Development</span>
                    <span className={`text-xs font-semibold ${
                      t.skillDevelopment === null
                        ? "text-muted-foreground"
                        : t.skillDevelopment >= 0 ? "text-emerald-400" : "text-rose-400"
                    }`}>
                      {t.skillDevelopment === null ? "—" : `${t.skillDevelopment >= 0 ? "+" : ""}${t.skillDevelopment}%`}
                    </span>
                  </div>
                  <PBar pct={t.skillDevelopment === null ? 50 : Math.max(0, Math.min(100, 50 + t.skillDevelopment))} />
                </div>

                <div className="w-16 text-center flex-shrink-0">
                  <div className="text-base font-bold text-foreground">{t.avgAssessmentScore}%</div>
                  <div className="text-[10px] text-muted-foreground">avg score</div>
                </div>

                <div className="w-28 flex-shrink-0 text-center">
                  <CertBdg status={t.certificationStatus} />
                </div>

                <ChevronRight size={14} className="text-muted-foreground flex-shrink-0" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
