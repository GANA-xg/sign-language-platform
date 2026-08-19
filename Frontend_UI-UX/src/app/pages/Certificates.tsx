import { useState, useEffect } from "react";
import { Award, Download, Share2, CheckCircle, XCircle, Loader2, ChevronRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import {
  getCertificateEligibility,
  generateCertificate,
  getRecommendations,
  getFeedback,
} from "../services/businessApi";
import { getProfile } from "../services/api";
import type { Screen } from "@/app/utils/types";

type EligibilityData = {
  eligible: boolean;
  reasons_failed: string[];
  criteria_met: string[];
};

type Recommendation = {
  sign: string;
  reason: string;
  recent_accuracy: number;
};

type FeedbackItem = {
  feedback_type: "praise" | "improvement" | "correction";
  message: string;
  severity: string;
};

export default function Certificates({ go }: { go: (s: Screen) => void }) {
  const { userId, role } = useAuth();
  const [eligibility, setEligibility] = useState<EligibilityData | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [learnerName, setLearnerName] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uid = userId ?? "00000000-0000-0000-0000-000000000000";

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);

      // Profile — main backend. Fail silently, fall back to role name.
      try {
        const profile = await getProfile();
        setLearnerName(profile.full_name ?? role);
      } catch {
        setLearnerName(role);
      }

      // Certificate eligibility + recommendations — business logic.
      try {
        const [elig, recs] = await Promise.all([
          getCertificateEligibility(uid),
          getRecommendations(uid),
        ]);
        setEligibility(elig);
        setRecommendations(recs.recommendations ?? []);
      } catch (e) {
        setError("Couldn't load certificate data. The Business Logic service is unreachable.");
        setLoading(false);
        return;
      }

      // Feedback — optional, fail silently.
      const recentSessionId = localStorage.getItem("current_session_id");
      if (recentSessionId) {
        try {
          const fb = await getFeedback(recentSessionId);
          setFeedback(fb.feedback ?? []);
        } catch {
          // no feedback yet — that's fine
        }
      }

      setLoading(false);
    };
    fetchAll();
  }, [uid]);

  const handleDownload = async () => {
    if (!eligibility?.eligible) return;
    setDownloading(true);
    try {
      const blob = await generateCertificate(uid, learnerName);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `certificate_${uid.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError("Couldn't generate certificate. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  const feedbackColor = (type: string) =>
    type === "praise" ? "text-emerald-400" : type === "correction" ? "text-rose-400" : "text-amber-400";

  if (loading) {
    return (
      <div className="p-4 md:p-8 max-w-2xl mx-auto space-y-6">
        <div className="bg-card border border-border rounded-[14px] p-6 animate-pulse" style={{ boxShadow: "var(--card-shadow)" }}>
          <div className="flex items-center justify-between mb-4">
            <div className="h-4 w-40 bg-muted rounded" />
            <div className="h-6 w-20 bg-muted rounded-full" />
          </div>
          <div className="space-y-2 mb-5">
            <div className="h-3 w-3/4 bg-muted rounded" />
            <div className="h-3 w-2/3 bg-muted rounded" />
            <div className="h-3 w-1/2 bg-muted rounded" />
          </div>
          <div className="h-10 w-48 bg-muted rounded-xl" />
        </div>
        <div className="bg-card border border-border rounded-[14px] p-6 animate-pulse" style={{ boxShadow: "var(--card-shadow)" }}>
          <div className="h-4 w-48 bg-muted rounded mb-4" />
          <div className="space-y-3">
            <div className="h-3 w-full bg-muted rounded" />
            <div className="h-3 w-5/6 bg-muted rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-rose-400 text-sm">{error}</div>
    );
  }

  return (
    <div className="p-4 md:p-8 max-w-2xl mx-auto space-y-6">

      {/* ── Certificate Eligibility ── */}
      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-foreground text-sm">Certificate Eligibility</h3>
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${eligibility?.eligible ? "bg-emerald-500/10 text-emerald-400" : "bg-muted text-muted-foreground"}`}>
            {eligibility?.eligible ? "Eligible ✓" : "Not Yet"}
          </span>
        </div>

        <div className="space-y-2 mb-5">
          {eligibility?.criteria_met.map((c, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
              <CheckCircle size={13} className="text-emerald-400 flex-shrink-0 mt-0.5" />
              {c}
            </div>
          ))}
          {eligibility?.reasons_failed.map((r, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
              <XCircle size={13} className="text-rose-400 flex-shrink-0 mt-0.5" />
              {r}
            </div>
          ))}
        </div>

        {eligibility?.eligible && (
          <div className="border border-border rounded-[12px] p-4 mb-4 flex items-center gap-4 bg-emerald-500/5">
            <Award size={36} className="text-amber-400 flex-shrink-0" />
            <div>
              <div className="font-bold text-foreground text-sm">Certificate of Achievement</div>
              <div className="text-xs text-muted-foreground">AI-Powered Sign Language Platform · Awarded to {learnerName}</div>
            </div>
          </div>
        )}

        <button
          onClick={handleDownload}
          disabled={!eligibility?.eligible || downloading}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm transition-all ${
            eligibility?.eligible && !downloading
              ? "bg-primary hover:bg-primary/90 text-primary-foreground"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          }`}
        >
          {downloading ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
          {downloading ? "Generating..." : eligibility?.eligible ? "Download Certificate" : "Complete requirements to unlock"}
        </button>
      </div>

      {/* ── Feedback from last session ── */}
      {feedback.length > 0 && (
        <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
          <h3 className="font-semibold text-foreground text-sm mb-4">Latest Session Feedback</h3>
          <div className="space-y-3">
            {feedback.map((f, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className={`text-xs font-semibold uppercase tracking-wide flex-shrink-0 mt-0.5 ${feedbackColor(f.feedback_type)}`}>
                  {f.feedback_type}
                </span>
                <p className="text-xs text-muted-foreground">{f.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Recommendations ── */}
      {recommendations.length > 0 && (
        <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
          <h3 className="font-semibold text-foreground text-sm mb-4">Practice Recommendations</h3>
          <div className="space-y-3">
            {recommendations.map((r, i) => (
              <div key={i} className="flex items-start gap-3 border border-border rounded-xl p-3">
                <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary font-bold text-sm flex-shrink-0">
                  {r.sign}
                </div>
                <div>
                  <div className="text-xs font-semibold text-foreground mb-0.5">Sign "{r.sign}"</div>
                  <div className="text-xs text-muted-foreground">{r.reason}</div>
                  <div className="text-xs text-rose-400 mt-1">Recent accuracy: {r.recent_accuracy}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations.length === 0 && feedback.length === 0 && !eligibility?.eligible && (
        <div className="bg-card border border-border rounded-[14px] p-6 text-center" style={{ boxShadow: "var(--card-shadow)" }}>
          <Award size={32} className="text-muted-foreground mx-auto mb-3" />
          <p className="text-sm text-muted-foreground">Complete practice sessions to unlock feedback and recommendations.</p>
        </div>
      )}

      {/* ── Certification Exam entry point ── */}
      <div className="bg-card border border-border rounded-xl p-5 text-center space-y-3">
        <Award size={24} className="mx-auto text-primary" />
        <div>
          <h3 className="font-semibold text-sm text-foreground">Certification Exam</h3>
          <p className="text-xs text-muted-foreground mt-1">
            Prove your proficiency at Beginner, Intermediate, Advanced, or Professional level.
          </p>
        </div>
        <button
          onClick={() => go("certification-exam")}
          className="w-full py-2.5 rounded-xl bg-primary/10 text-primary font-semibold text-sm hover:bg-primary/20 transition-colors flex items-center justify-center gap-2"
        >
          <ChevronRight size={14} /> Take Certification Exam
        </button>
      </div>
    </div>
  );
}