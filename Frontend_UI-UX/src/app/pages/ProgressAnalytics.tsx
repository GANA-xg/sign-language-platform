import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft, RefreshCw,
  Loader2,
} from "lucide-react";
import {
  BarChart, Bar, ResponsiveContainer, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, AreaChart, Area, LineChart, Line,
} from "recharts";
import { MCard } from "../components/shared/MCard";
import { Bdg } from "../components/shared/Indicators";
import { useAuth } from "../context/AuthContext";
import {
  getProgressReport, getWeeklyAnalytics, getUserAnalytics, downloadProgressPDF,
  downloadLearnerProgressExport,
  downloadLearningReport,
  downloadAssessmentReport,
  downloadAccuracyReport,
  downloadCertificationReport,
} from "../services/businessApi";
import { getAnalytics } from "../services/aiApi";

interface ProgressReport {
  total_sessions: number; completed_sessions: number;
  total_practice_time_seconds: number; average_accuracy: number;
  grade: string; distinct_signs_practiced: number;
  weak_signs: string[]; strong_signs: string[];
  current_week_accuracy: number | null; improvement_rate: number | null;
  recommended_for_practice: string[];
  certificate_eligible: boolean; certificate_reasons_failed: string[];
}

interface WeeklyData { week_label: string; average_accuracy: number; sessions_count: number; }

export default function ProgressAnalytics() {
  const { userId, fullName } = useAuth();
  const [report, setReport] = useState<ProgressReport | null>(null);
  const [weeklyData, setWeeklyData] = useState<WeeklyData[]>([]);
  const [ai, setAi] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [csvLoading, setCsvLoading] = useState(false);
  // M4 Day 3 — tracks which report type+format is currently downloading
  const [reportLoading, setReportLoading] = useState<string | null>(null);

  const uid = userId ?? "00000000-0000-0000-0000-000000000001";

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getProgressReport(uid),
      getWeeklyAnalytics(uid),
      getAnalytics().catch(() => null),
    ])
      .then(([rep, weekly, aiData]) => {
        setReport(rep);
        setWeeklyData(weekly.weeks ?? []);
        if (aiData) setAi(aiData);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [uid]);

  const handleDownloadPDF = async () => {
    setPdfLoading(true);
    try {
      const blob = await downloadProgressPDF(uid, fullName ?? "Learner");
      if (blob) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "progress_report.pdf"; a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      alert("Couldn't generate PDF. Is the Business Logic service running?");
    } finally {
      setPdfLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    setCsvLoading(true);
    try {
      const blob = await downloadLearnerProgressExport(uid, "csv");
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "progress_report.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      alert("Couldn't export CSV right now.");
    } finally {
      setCsvLoading(false);
    }
  };

  // M4 Day 3 — download any of the 5 report types as PDF or Excel
  // Confirmed against real export router (export.py):
  //   GET /export/{user_id}/learning?format=pdf|excel
  //   GET /export/{user_id}/assessment?format=pdf|excel
  //   GET /export/{user_id}/accuracy?format=pdf|excel
  //   GET /export/{user_id}/certification-report?format=pdf|excel
  const handleDownloadReport = async (
    type: "learning" | "assessment" | "accuracy" | "certification",
    format: "pdf" | "excel"
  ) => {
    const key = `${type}-${format}`;
    setReportLoading(key);
    try {
      const name = fullName ?? "Learner";
      let blob: Blob;
      if (type === "learning")       blob = await downloadLearningReport(uid, name, format);
      else if (type === "assessment") blob = await downloadAssessmentReport(uid, name, format);
      else if (type === "accuracy")  blob = await downloadAccuracyReport(uid, name, format);
      else                           blob = await downloadCertificationReport(uid, name, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${type}_report_${uid.slice(0, 8)}.${format === "excel" ? "xlsx" : "pdf"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert(`Couldn't download ${type} report. The Business Logic service is unreachable.`);
    } finally {
      setReportLoading(null);
    }
  };

  const practiceHours = report
    ? Math.round(report.total_practice_time_seconds / 3600 * 10) / 10
    : 0;

  const chartData = weeklyData.map(w => ({
    date: w.week_label,
    accuracy: Math.round(w.average_accuracy),
  }));

  return (
    <div className="p-6 space-y-5 max-w-6xl mx-auto">
      {loading && (
        <div className="flex items-center justify-center py-20">
          <RefreshCw size={20} className="animate-spin text-muted-foreground" />
        </div>
      )}

      {!loading && error && (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <AlertTriangle size={28} className="text-rose-400" />
          <p className="text-sm text-muted-foreground">Couldn't load your progress data. The Business Logic service is unreachable.</p>
        </div>
      )}

      {!loading && !error && report && (
        <>
          {/* ── REAL DATA from Business Logic /progress/{user_id} ── */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MCard icon={BookOpen}   label="Lessons Completed"   value={String(report.completed_sessions)} col="cyan" />
            <MCard icon={Target}     label="Average Accuracy"    value={`${Math.round(report.average_accuracy)}%`} delta={`Grade ${report.grade}`} col="emerald" />
            <MCard icon={Clock}      label="Practice Time"       value={`${practiceHours}h`} col="violet" />
            <MCard icon={TrendingUp} label="Improvement Rate"    value={report.improvement_rate != null ? `+${Math.round(report.improvement_rate)}%` : "—"} col="amber" />
          </div>

          {/* Real weekly accuracy chart */}
          {chartData.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="font-semibold text-foreground mb-4 text-sm">Accuracy Over Time</h3>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                    <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} width={30} />
                    <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }} />
                    <Line type="monotone" dataKey="accuracy" stroke="var(--primary)" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="font-semibold text-foreground mb-4 text-sm">Weak Signs</h3>
                {report.weak_signs.length === 0 ? (
                  <div className="flex items-center justify-center h-40 text-xs text-muted-foreground">No weak signs — great work!</div>
                ) : (
                  <div className="flex flex-wrap gap-2 pt-2">
                    {report.weak_signs.map(s => (
                      <div key={s} className="flex items-center gap-2 bg-rose-950/20 border border-rose-900/30 rounded-xl px-3 py-2">
                        <div className="w-7 h-7 rounded-lg bg-rose-950/40 border border-rose-900/40 flex items-center justify-center text-xs font-bold text-rose-400">{s}</div>
                        <span className="text-xs text-rose-400">Needs practice</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {report.recommended_for_practice.length > 0 && (
            <div className="bg-card border border-border rounded-xl p-5">
              <h3 className="font-semibold text-foreground mb-3 text-sm">Recommended for Practice</h3>
              <div className="flex flex-wrap gap-2">
                {report.recommended_for_practice.map(s => (
                  <span key={s} className="px-3 py-1.5 bg-primary/10 border border-primary/30 text-primary text-xs font-semibold rounded-lg">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Certificate eligibility */}
          <div className={`bg-card border rounded-xl p-5 ${report.certificate_eligible ? "border-emerald-900/40" : "border-border"}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-foreground text-sm mb-1">Certificate Eligibility</h3>
                {report.certificate_eligible
                  ? <p className="text-xs text-emerald-400">You qualify for a certificate! Go to Certificates to download it.</p>
                  : <p className="text-xs text-muted-foreground">{report.certificate_reasons_failed[0] ?? "Keep practicing to qualify."}</p>
                }
              </div>
              <Bdg label={report.certificate_eligible ? "Eligible" : "Not Yet"} v={report.certificate_eligible ? "success" : "default"} />
            </div>
          </div>

          {/* Progress report export (existing — CSV + PDF) */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleDownloadCSV}
              disabled={csvLoading || !report}
              className="flex items-center gap-2 bg-card border border-border hover:bg-hover disabled:opacity-60 text-foreground font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
            >
              <Download size={14} />
              {csvLoading ? "Exporting CSV..." : "Export Report CSV"}
            </button>
            <button
              onClick={handleDownloadPDF}
              disabled={pdfLoading}
              className="flex items-center gap-2 bg-primary hover:bg-primary/90 disabled:opacity-60 text-primary-foreground font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
            >
              <Download size={14} />
              {pdfLoading ? "Generating PDF..." : "Download Progress Report PDF"}
            </button>
          </div>

          {/* ── M4 Day 3: All 5 Report Types ────────────────────────────────────
              Wired to real export router (export.py):
                GET /export/{uid}/learning, /assessment, /accuracy, /certification-report
              Each available as PDF or Excel. Progress report (above) covers the 5th type.
          ── */}
          <div className="bg-card border border-border rounded-xl p-5 space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-foreground">All Reports</h3>
              <p className="text-xs text-muted-foreground mt-0.5">
                Download any of the 5 report types as PDF or Excel.
              </p>
            </div>

            <div className="divide-y divide-border/50">
              {(["learning", "assessment", "accuracy", "certification"] as const).map(type => (
                <div key={type} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                  <span className="text-sm capitalize text-foreground">{type} Report</span>
                  <div className="flex gap-2">
                    {(["pdf", "excel"] as const).map(fmt => {
                      const key = `${type}-${fmt}`;
                      const busy = reportLoading === key;
                      return (
                        <button
                          key={fmt}
                          onClick={() => handleDownloadReport(type, fmt)}
                          disabled={!!reportLoading}
                          className="px-3 py-1.5 text-xs rounded-lg border border-border bg-muted/50 hover:bg-muted text-foreground disabled:opacity-40 transition-colors flex items-center gap-1.5"
                        >
                          {busy
                            ? <Loader2 size={10} className="animate-spin" />
                            : <Download size={10} />
                          }
                          {fmt.toUpperCase()}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* ── AI service session stats (live, resets on restart) ── */}
      {ai && (
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground text-sm">Live AI Session Stats</h3>
            <Bdg label="Live from AI service" v="info" />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div><div className="text-2xl font-bold text-foreground">{ai.total_predictions}</div><div className="text-xs text-muted-foreground">Predictions</div></div>
            <div><div className="text-2xl font-bold text-foreground">{Math.round(ai.average_confidence * 100)}%</div><div className="text-xs text-muted-foreground">Avg confidence</div></div>
            <div><div className="text-2xl font-bold text-emerald-400">{ai.high_confidence_predictions}</div><div className="text-xs text-muted-foreground">High confidence</div></div>
            <div><div className="text-2xl font-bold text-foreground">{ai.most_predicted_sign ?? "—"}</div><div className="text-xs text-muted-foreground">Most practiced</div></div>
          </div>
        </div>
      )}
    </div>
  );
}