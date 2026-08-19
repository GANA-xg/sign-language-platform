import { useState, useEffect } from "react";
import {
  BookOpen, Camera, CheckSquare, Clock, Zap, Target,
  ArrowRight, Lock, Award,
} from "lucide-react";
import type { Screen } from "@/app/utils/types";
import { MCard } from "../components/shared/MCard";
import { Bdg, PBar, Ring } from "../components/shared/Indicators";
import { getDashboard } from "../services/aiApi";
import { useAuth } from "../context/AuthContext";
import { getGamification, getWeeklyAnalytics, getUserAnalytics } from "../services/businessApi";
import {
  LineChart, Line, BarChart, Bar, ResponsiveContainer,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";

interface RecentPrediction {
  prediction: string;
  confidence: number;
  confidence_level: string;
  status: string;
  gesture_quality: string;
  processing_time_ms: number;
}

export default function LearnerDashboard({ go }: { go: (s: Screen) => void }) {
  const { userId } = useAuth();
  const [recent, setRecent] = useState<RecentPrediction[]>([]);
  const [loadingRecent, setLoadingRecent] = useState(true);
  const [gamification, setGamification] = useState<any>(null);
  const [loadingGamification, setLoadingGamification] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [weekly, setWeekly] = useState<any[]>([]);
  const [loadingAnalytics, setLoadingAnalytics] = useState(true);

  useEffect(() => {
    getDashboard()
      .then(d => setRecent(d.recent_predictions ?? []))
      .catch(() => setRecent([]))
      .finally(() => setLoadingRecent(false));
  }, []);

  useEffect(() => {
    if (!userId) return;
    getGamification(userId)
      .then(setGamification)
      .catch(() => setGamification(null))
      .finally(() => setLoadingGamification(false));
  }, [userId]);

  useEffect(() => {
    if (!userId) return;
    Promise.all([
      getUserAnalytics(userId).catch(() => null),
      getWeeklyAnalytics(userId).catch(() => null),
    ])
      .then(([userAnalytics, weeklyData]) => {
        setAnalytics(userAnalytics);
        setWeekly(weeklyData?.weeks ?? []);
      })
      .finally(() => setLoadingAnalytics(false));
  }, [userId]);

  const accuracy = analytics?.average_accuracy ?? 0;
  const signsLearned = analytics?.lessons_completed ?? 0;
  const totalSessions = analytics?.total_sessions ?? 0;
  const streak = gamification?.streak?.current_streak ?? 0;

  const accuracyChartData = weekly.map((w: any) => ({
    date: w.week_label,
    accuracy: w.average_accuracy,
  }));

  const lessonsChartData = weekly.map((w: any) => ({
    week: w.week_label,
    count: w.sessions_count,
  }));

  return (
    <div className="p-6 space-y-5 max-w-6xl mx-auto">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Welcome back 👋</h2>
          <p className="text-muted-foreground text-sm mt-1">
            {streak > 0 ? `You are on a ${streak}-day streak — keep it up!` : "Start practicing to build your streak!"}
          </p>
        </div>
        {streak > 0 && (
          <div className="flex items-center gap-2 bg-amber-950/30 border border-amber-900/40 rounded-xl px-4 py-2">
            <Zap size={17} className="text-amber-400" />
            <span className="text-amber-400 font-bold">{streak}</span>
            <span className="text-muted-foreground text-sm">day streak</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MCard icon={Target}   label="Overall Accuracy"  value={`${accuracy}%`}     delta={accuracy > 0 ? "lifetime" : "start practicing"} col="cyan" />
        <MCard icon={BookOpen} label="Signs Learned"     value={`${signsLearned}`}  delta={`${totalSessions} sessions`}                col="emerald" />
        <MCard icon={Clock}    label="Total Sessions"    value={`${totalSessions}`} delta="all time"                                   col="violet" />
        <MCard icon={Award}    label="Badges Earned"     value={`${gamification?.total_badges_earned ?? 0}`} delta="lifetime"            col="amber" />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-card border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">Continue Learning</h3>
            <Bdg label="In Progress" v="info" />
          </div>
          <div className="flex items-start gap-4">
            <div className="w-20 h-14 bg-gradient-to-br from-cyan-900/60 to-violet-900/60 rounded-lg flex items-center justify-center flex-shrink-0">
              <BookOpen size={22} className="text-cyan-400" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-semibold text-foreground">ASL Intermediate — Module 4</h4>
              <p className="text-xs text-muted-foreground mt-0.5 mb-3">Describing emotions and mental states</p>
              <PBar pct={68} />
              <div className="flex items-center justify-between mt-1.5">
                <span className="text-xs text-muted-foreground">68% complete · 6 lessons left</span>
                <button
                  onClick={() => go("lesson")}
                  className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-semibold"
                >
                  Resume <ArrowRight size={11} />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5 flex flex-col items-center justify-center">
          <Ring pct={73} size={88} />
          <div className="mt-3 text-center">
            <div className="text-sm font-semibold text-foreground">Module Progress</div>
            <div className="text-xs text-muted-foreground">Module 4 of 6</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Accuracy Over Time</h3>
          {loadingAnalytics ? (
            <div className="h-[180px] bg-muted rounded-lg animate-pulse" />
          ) : accuracyChartData.length === 0 ? (
            <div className="h-[180px] flex items-center justify-center text-sm text-muted-foreground">
              Complete sessions to see accuracy trends
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={accuracyChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} width={30} />
                <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="accuracy" stroke="var(--primary)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Sessions Per Week</h3>
          {loadingAnalytics ? (
            <div className="h-[180px] bg-muted rounded-lg animate-pulse" />
          ) : lessonsChartData.length === 0 ? (
            <div className="h-[180px] flex items-center justify-center text-sm text-muted-foreground">
              Complete sessions to see weekly trends
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={lessonsChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="week" tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} width={30} />
                <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" fill="var(--primary)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">Badges & Streaks</h3>
            <Bdg label={streak > 0 ? `${streak} day streak` : "No streak yet"} v={streak > 0 ? "success" : "default"} />
          </div>
          {loadingGamification && <div className="h-40 bg-muted rounded-lg animate-pulse" />}
          {!loadingGamification && !gamification && (
            <p className="text-xs text-muted-foreground">Couldn't load badges/streak data — is the Business Logic service running?</p>
          )}
          {!loadingGamification && gamification && (
            <>
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="rounded-xl border border-border bg-muted p-3 text-center">
                  <div className="text-xs text-muted-foreground">Current</div>
                  <div className="text-2xl font-bold text-foreground mt-1">{gamification.streak.current_streak}</div>
                  <div className="text-xs text-muted-foreground mt-1">days</div>
                </div>
                <div className="rounded-xl border border-border bg-muted p-3 text-center">
                  <div className="text-xs text-muted-foreground">Best</div>
                  <div className="text-2xl font-bold text-foreground mt-1">{gamification.streak.longest_streak}</div>
                  <div className="text-xs text-muted-foreground mt-1">days</div>
                </div>
                <div className="rounded-xl border border-border bg-muted p-3 text-center">
                  <div className="text-xs text-muted-foreground">Unlocked</div>
                  <div className="text-2xl font-bold text-foreground mt-1">{gamification.total_badges_earned}</div>
                  <div className="text-xs text-muted-foreground mt-1">badges</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {gamification.badges.map((badge: any) => (
                  <div
                    key={badge.badge_id}
                    className={`rounded-lg border p-3 transition-all ${
                      badge.earned
                        ? "border-amber-500/30 bg-amber-500/5"
                        : "border-border bg-muted opacity-70"
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <div className="w-9 h-9 rounded-full bg-background flex items-center justify-center text-base flex-shrink-0" />
                      <div className="min-w-0">
                        <div className="text-sm font-semibold text-foreground flex items-center gap-1">
                          {badge.name}
                          {!badge.earned && <Lock size={12} className="text-muted-foreground" />}
                        </div>
                        <div className="text-[11px] text-muted-foreground mt-0.5">{badge.description}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="font-semibold text-foreground mb-4">Recommended Next</h3>
          <div className="space-y-2">
            {[
              { title: "Numbers 1–20",   type: "practice",   time: "8 min",  diff: "Beginner" },
              { title: "Color Signs",    type: "lesson",     time: "12 min", diff: "Beginner" },
              { title: "Module 4 Quiz",  type: "assessment", time: "15 min", diff: "Intermediate" },
            ].map(item => (
              <button
                key={item.title}
                onClick={() => go(item.type as Screen)}
                className="w-full flex items-center gap-3 p-3 rounded-lg bg-muted hover:bg-hover border border-border/50 hover:border-primary/20 transition-all text-left"
              >
                <div className="w-8 h-8 rounded-lg bg-background flex items-center justify-center">
                  {item.type === "practice" ? <Camera size={13} className="text-cyan-400" /> :
                   item.type === "assessment" ? <CheckSquare size={13} className="text-emerald-400" /> :
                   <BookOpen size={13} className="text-violet-400" />}
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-foreground">{item.title}</div>
                  <div className="text-xs text-muted-foreground capitalize">{item.type} · {item.time}</div>
                </div>
                <Bdg label={item.diff} v={item.diff === "Beginner" ? "info" : "warning"} />
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-foreground">Recent AI Predictions</h3>
          <Bdg label="Live from AI service" v="info" />
        </div>
        {loadingRecent && <div className="h-12 bg-muted rounded-lg animate-pulse" />}
        {!loadingRecent && recent.length === 0 && (
          <p className="text-xs text-muted-foreground">No predictions yet this session — try the Practice screen.</p>
        )}
        {!loadingRecent && recent.length > 0 && (
          <div className="space-y-2">
            {recent.map((r, i) => (
              <div key={i} className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-muted flex items-center justify-center font-bold text-cyan-400">
                  {r.prediction}
                </div>
                <div className="flex-1 text-muted-foreground">
                  {Math.round(r.confidence * 100)}% confidence · {r.gesture_quality}
                </div>
                <Bdg label={r.confidence_level} v={r.confidence_level === "High" ? "success" : "warning"} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
