import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft, RefreshCw,
} from "lucide-react";
import type { Screen } from "../lib/types";
import { Bdg, PBar } from "../components/shared/Indicators";
import { getCourses } from "../services/api";

// Course shape as returned by Intern 2's /courses endpoint today:
// { id, title, difficulty }. Fields the UI wants but the contract
// doesn't provide yet (desc, hrs, pct, cat, lessons) get safe fallback
// defaults below — swap these out once the backend contract grows.
interface UiCourse {
  id: string | number; title: string; desc: string;
  lessons: number; hrs: string; diff: string; pct: number; cat: string;
}

function toUiCourse(c: any): UiCourse {
  return {
    id: c.id,
    title: c.title,
    desc: c.desc ?? "Lesson content for this course.",
    lessons: c.lessons ?? 0,
    hrs: c.hrs ?? "—",
    diff: c.difficulty ?? c.diff ?? "Beginner",
    pct: c.pct ?? 0,
    cat: c.cat ?? "ASL",
  };
}

export default function CourseCatalog({ go }: { go: (s: Screen) => void }) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [courses, setCourses] = useState<UiCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getCourses()
      .then(data => setCourses(data.map(toUiCourse)))
      .catch(() => setError("Couldn't load courses. Check your connection and try again."))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filters = ["All", "ASL", "BSL", "Specialized", "Beginner", "Intermediate", "Advanced"];
  const filtered = courses.filter(c =>
    (filter === "All" || c.cat === filter || c.diff === filter) &&
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-4 md:p-6 space-y-4 md:space-y-5 max-w-6xl mx-auto">
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            className="w-full bg-[#0e1a30] border border-border rounded-lg pl-9 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:border-primary/50"
            placeholder="Search courses..."
          />
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {filters.map(f => (
            <button
              key={f} onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filter === f ? "bg-primary text-black" : "bg-[#0e1a30] text-muted-foreground border border-border hover:text-foreground"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-card border border-border rounded-xl overflow-hidden animate-pulse">
              <div className="h-24 bg-surface" />
              <div className="p-4 space-y-2">
                <div className="h-3.5 bg-surface rounded w-3/4" />
                <div className="h-3 bg-surface rounded w-full" />
                <div className="h-3 bg-surface rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
          <AlertTriangle size={28} className="text-rose-400" />
          <p className="text-sm text-muted-foreground max-w-sm">{error}</p>
          <button
            onClick={load}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-primary text-black hover:bg-primary-active transition-colors"
          >
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
          <BookOpen size={28} className="text-muted-foreground" />
          <p className="text-sm text-muted-foreground">No courses match your search/filter.</p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map(c => (
            <div key={c.id} className="bg-card border border-border rounded-xl overflow-hidden hover:border-primary/50 transition-all group">
              <div className="h-24 bg-gradient-to-br from-[#0e1a30] to-[#162035] flex items-center justify-center relative">
                <BookOpen size={32} className="text-muted-soft group-hover:text-muted transition-colors" />
                <div className="absolute top-2.5 left-2.5 flex gap-1.5">
                  <Bdg label={c.diff} v={c.diff === "Beginner" ? "info" : c.diff === "Intermediate" ? "warning" : "error"} />
                  <Bdg label={c.cat} />
                </div>
                {c.pct === 100 && (
                  <div className="absolute top-2.5 right-2.5 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                    <Check size={10} className="text-black" />
                  </div>
                )}
              </div>
              <div className="p-4">
                <h4 className="font-semibold text-foreground mb-1 text-sm">{c.title}</h4>
                <p className="text-xs text-muted-foreground mb-3 leading-relaxed">{c.desc}</p>
                <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
                  <span>{c.lessons} lessons</span>
                  <span className="text-border">·</span>
                  <span>{c.hrs}</span>
                </div>
                {c.pct > 0 && c.pct < 100 && (
                  <div className="mb-3">
                    <PBar pct={c.pct} />
                    <span className="text-xs text-muted-foreground mt-1 block">{c.pct}% complete</span>
                  </div>
                )}
                <button
                  onClick={() => go("lesson")}
                  className={`w-full py-2 rounded-lg text-xs font-semibold transition-all ${
                    c.pct === 100
                      ? "bg-surface text-muted-foreground"
                      : c.pct > 0
                      ? "bg-primary text-black hover:bg-primary-active"
                      : "bg-surface text-foreground hover:bg-surface-strong border border-border"
                  }`}
                >
                  {c.pct === 100 ? "Review" : c.pct > 0 ? "Continue" : "Start Course"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
