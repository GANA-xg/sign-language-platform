import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft,
} from "lucide-react";
import type { Screen } from "../utils/types";
import { HandOverlay } from "../components/shared/HandOverlay";
import { Bdg, Ring } from "../components/shared/Indicators";
import { FlowStepper } from "../components/shared/FlowStepper";
import { generateFeedback, getAssessment } from "../services/businessApi";

interface FeedbackItem { feedback_type: string; message: string; severity: string; }
interface Assessment {
  correct_predictions: number; total_predictions: number;
  accuracy_percentage: number; score: number; grade: string;
}

export default function FeedbackScreen({ go }: { go: (s: Screen) => void }) {
  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pulls the session_id stashed by PracticeScreen — no router-state
  // plumbing for it yet, this is the simplest reliable hand-off for a
  // single active session. Real feedback requires at least one attempt
  // to have been submitted (assessment must already exist server-side).
  useEffect(() => {
    const sessionId = localStorage.getItem("current_session_id");
    const expectedSign = localStorage.getItem("current_expected_sign") ?? undefined;
    if (!sessionId) {
      setError("No active practice session found. Try a sign in Practice first.");
      setLoading(false);
      return;
    }
    Promise.all([
      generateFeedback(sessionId, expectedSign),
      getAssessment(sessionId).catch(() => null),
    ])
      .then(([fb, assess]) => {
        setItems(fb.feedback ?? []);
        if (assess) setAssessment(assess);
      })
      .catch(() => setError("Couldn't generate feedback. Is the Business Logic service running on port 8002?"))
      .finally(() => setLoading(false));
  }, []);

  const severityStyle = (s: string) =>
    s === "high"   ? "border-rose-900/50 bg-rose-950/20" :
    s === "medium" ? "border-amber-900/50 bg-amber-950/20" :
                      "border-emerald-900/50 bg-emerald-950/20";
  const severityIcon = (s: string) =>
    s === "high"   ? <XCircle size={13} className="text-rose-400" /> :
    s === "medium" ? <AlertTriangle size={13} className="text-amber-400" /> :
                      <CheckCircle size={13} className="text-emerald-400" />;

  return (
    <div className="p-4 md:p-5 max-w-5xl mx-auto space-y-4">
      <FlowStepper active={3} />

      <div className="bg-card border border-border rounded-xl p-5 flex flex-col sm:flex-row items-center sm:items-start gap-4 sm:gap-5">
        <Ring pct={assessment?.accuracy_percentage ?? 0} size={88} />
        <div>
          <h2 className="text-lg font-bold text-foreground">
            {loading ? "Loading feedback..." : assessment ? "Here's how you did" : "No results yet"}
          </h2>
          {assessment && (
            <p className="text-muted-foreground text-sm mt-1">
              {assessment.correct_predictions} of {assessment.total_predictions} correct · Score {assessment.score} · Grade {assessment.grade}
            </p>
          )}
          {error && <p className="text-rose-400 text-sm mt-1">{error}</p>}
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl p-5">
        <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2 text-sm">
          <MessageCircle size={15} className="text-cyan-400" />
          AI Feedback
        </h3>
        {loading && <div className="h-20 bg-[#0e1a30] rounded-lg animate-pulse" />}
        {!loading && items.length === 0 && !error && (
          <p className="text-xs text-muted-foreground">No feedback items generated yet.</p>
        )}
        {!loading && items.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {items.map((item, i) => (
              <div key={i} className={`p-3 rounded-lg border ${severityStyle(item.severity)}`}>
                <div className="flex items-center gap-1.5 mb-1">
                  {severityIcon(item.severity)}
                  <span className="text-xs font-semibold text-foreground capitalize">{item.feedback_type}</span>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{item.message}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button onClick={() => go("practice")} className="flex items-center gap-2 bg-[#0e1a30] border border-border hover:border-cyan-900/40 text-foreground px-4 py-2.5 rounded-xl text-sm font-semibold transition-all">
          <RotateCcw size={14} />
          Try Again
        </button>
        <button onClick={() => go("practice")} className="flex items-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-black px-5 py-2.5 rounded-xl text-sm font-bold transition-colors">
          <SkipForward size={14} />
          Next Sign
        </button>
        <button onClick={() => go("progress")} className="ml-auto flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
          View Progress <TrendingUp size={13} />
        </button>
      </div>
    </div>
  );
}