import { useState, useEffect } from "react";
import { AlertTriangle, RefreshCw, Users } from "lucide-react";
import { Bdg } from "../components/shared/Indicators";
import { useAuth } from "../context/AuthContext";
import { getTrainerDashboard } from "../services/businessApi";

const BUSINESS_BASE_URL = import.meta.env.VITE_BUSINESS_API_URL ?? "https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com";

interface LearnerCase {
  learner_id: string;
  sessions_this_week: number;
  engagement_level: string;
  avg_assessment_score: number;
  skill_development_trend: number | null;
  certification_status: string;
}

export default function TrainerConsole() {
  const { userId } = useAuth();
  const [sel, setSel] = useState<string | null>(null);
  const [cases, setCases] = useState<LearnerCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const trainerId = userId ?? "00000000-0000-0000-0000-000000000000";

  useEffect(() => {
    setLoading(true);
    getTrainerDashboard(trainerId)
      .then((data) => {
        const learners = (data.learners ?? []) as LearnerCase[];
        const flagged = learners.filter(
          (l) => l.engagement_level === "Low" || l.avg_assessment_score < 70
        );
        setCases(flagged);
      })
      .catch(() => setError("Couldn't load trainer data. Is the Business Logic service running?"))
      .finally(() => setLoading(false));
  }, [trainerId]);

  const selectedCase = cases.find((c) => c.learner_id === sel);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">Trainer Console</h2>
          <p className="text-muted-foreground text-sm">Review AI-flagged low-confidence or low-engagement learners</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setLoading(true);
              getTrainerDashboard(trainerId)
                .then((data) => {
                  const learners = (data.learners ?? []) as LearnerCase[];
                  setCases(learners.filter((l) => l.engagement_level === "Low" || l.avg_assessment_score < 70));
                })
                .catch(() => {})
                .finally(() => setLoading(false));
            }}
            className="flex items-center gap-2 border border-border bg-muted hover:bg-hover text-foreground text-xs font-bold px-3 py-2 rounded-xl transition-colors"
          >
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
          </button>
          <Bdg label={`${cases.length} pending review`} v={cases.length > 0 ? "warning" : "success"} />
        </div>
      </div>

      {loading && cases.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw size={18} className="animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <AlertTriangle size={28} className="text-rose-400" />
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      ) : cases.length === 0 ? (
        <div className="bg-card border border-border rounded-[14px] p-8 text-center">
          <Users size={32} className="mx-auto text-muted-foreground mb-3" />
          <p className="text-sm font-semibold text-foreground">No flagged learners</p>
          <p className="text-xs text-muted-foreground mt-1">All your assigned learners are performing well.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-5">
          <div className="space-y-2.5">
            {cases.map((c) => (
              <button
                key={c.learner_id}
                onClick={() => setSel(c.learner_id)}
                className={`w-full p-4 rounded-[14px] border text-left transition-all ${
                  sel === c.learner_id ? "border-primary/40 bg-primary/5" : "border-border bg-card hover:border-primary/20"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-foreground flex-shrink-0">
                    {c.learner_id.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-foreground">Learner {c.learner_id.slice(0, 8)}</div>
                    <div className="text-xs text-muted-foreground">
                      Sessions: {c.sessions_this_week}/week · Engagement: {c.engagement_level}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-lg font-bold ${c.avg_assessment_score < 70 ? "text-warning" : "text-foreground"}`}>
                      {Math.round(c.avg_assessment_score)}%
                    </div>
                    <Bdg label="Low" v="warning" />
                  </div>
                </div>
              </button>
            ))}
          </div>

          {selectedCase ? (
            <div className="bg-card border border-border rounded-[14px] p-6 space-y-5" style={{ boxShadow: "var(--card-shadow)" }}>
              <h3 className="font-semibold text-foreground text-sm">Review: Learner {selectedCase.learner_id.slice(0, 8)}</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-muted rounded-xl p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-2">Sessions / Week</div>
                  <div className="text-2xl font-bold text-foreground">{selectedCase.sessions_this_week}</div>
                </div>
                <div className="bg-muted rounded-xl p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-2">Avg Score</div>
                  <div className={`text-2xl font-bold ${selectedCase.avg_assessment_score < 70 ? "text-warning" : "text-foreground"}`}>
                    {Math.round(selectedCase.avg_assessment_score)}%
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-muted rounded-xl p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-2">Engagement</div>
                  <Bdg
                    label={selectedCase.engagement_level}
                    v={selectedCase.engagement_level === "High" ? "success" : selectedCase.engagement_level === "Medium" ? "warning" : "error"}
                  />
                </div>
                <div className="bg-muted rounded-xl p-3 text-center">
                  <div className="text-xs text-muted-foreground mb-2">Certification</div>
                  <Bdg
                    label={selectedCase.certification_status}
                    v={selectedCase.certification_status === "Certified" ? "success" : "default"}
                  />
                </div>
              </div>
              {selectedCase.skill_development_trend !== null && (
                <div className="bg-muted rounded-xl p-3">
                  <div className="text-xs text-muted-foreground mb-1">Skill Development Trend</div>
                  <div className={`text-lg font-bold ${selectedCase.skill_development_trend >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                    {selectedCase.skill_development_trend >= 0 ? "+" : ""}{selectedCase.skill_development_trend}%
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-card border border-border rounded-[14px] flex items-center justify-center text-muted-foreground text-sm" style={{ boxShadow: "var(--card-shadow)" }}>
              Select a learner to review
            </div>
          )}
        </div>
      )}
    </div>
  );
}
