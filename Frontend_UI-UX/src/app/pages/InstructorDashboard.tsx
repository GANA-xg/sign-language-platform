import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle,
  ChevronRight,
  Plus,
  RefreshCw,
  Search,
  BookOpen,
  Users,
  TrendingUp,
} from "lucide-react";
import type { Screen } from "@/app/utils/types";
import { MCard } from "../components/shared/MCard";
import { assignStudent, getMyStudents } from "../services/api";

interface Student {
  user_id: string;
  full_name: string;
  email: string;
}

export default function InstructorDashboard({
  go,
}: {
  go: (s: Screen) => void;
}) {
  const [search, setSearch] = useState("");
  const [learnerId, setLearnerId] = useState("");
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [assigning, setAssigning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assignError, setAssignError] = useState<string | null>(null);
  const [assignSuccess, setAssignSuccess] = useState<string | null>(null);

  const loadStudents = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await getMyStudents();
      setStudents(data ?? []);
    } catch {
      setError("Couldn't load students. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  const filtered = useMemo(
    () =>
      students.filter(
        (s) =>
          s.full_name.toLowerCase().includes(search.toLowerCase()) ||
          s.email.toLowerCase().includes(search.toLowerCase())
      ),
    [students, search]
  );

  const handleAssign = async () => {
    const trimmed = learnerId.trim();

    if (!trimmed) {
      setAssignError("Enter a learner UUID first.");
      return;
    }

    setAssigning(true);
    setAssignError(null);
    setAssignSuccess(null);

    try {
      await assignStudent(trimmed);
      setAssignSuccess("Learner assigned successfully.");
      setLearnerId("");
      await loadStudents();
    } catch {
      setAssignError("Could not assign learner. Check the UUID and try again.");
    } finally {
      setAssigning(false);
    }
  };

  const totalStudents = students.length;

  return (
    <div className="p-4 md:p-8 space-y-6 md:space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold text-foreground">
            Instructor Dashboard
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Manage assigned learners, open course tools, and jump into student reviews.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => go("course-management")}
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-muted px-4 py-2.5 text-xs font-semibold text-foreground hover:bg-hover transition-colors"
          >
            <BookOpen size={14} />
            Manage Courses
          </button>
          <button
            type="button"
            onClick={() => go("student-detail")}
            className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            <Users size={14} />
            View Student Detail
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
        <MCard
          icon={Users}
          label="Total Students"
          value={String(totalStudents)}
          delta="assigned to you"
          col="cyan"
        />
        <MCard
          icon={TrendingUp}
          label="Avg Class Progress"
          value="—"
          delta="connect analytics"
          col="emerald"
        />
        <MCard
          icon={AlertTriangle}
          label="At-Risk Students"
          value="—"
          delta="connect analytics"
          col="amber"
        />
        <MCard
          icon={CheckCircle}
          label="Completions"
          value="—"
          delta="connect analytics"
          col="violet"
        />
      </div>

      <div
        className="bg-card border border-border rounded-[14px] p-6"
        style={{ boxShadow: "var(--card-shadow)" }}
      >
        <div className="flex flex-col gap-3">
          <h3 className="font-semibold text-foreground text-sm">
            Assign Learner
          </h3>
          <div className="flex flex-col lg:flex-row lg:items-end gap-3">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-foreground mb-2">
                Learner UUID
              </label>
              <input
                value={learnerId}
                onChange={(e) => setLearnerId(e.target.value)}
                placeholder="Paste learner UUID here"
                className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
              />
            </div>
            <button
              type="button"
              onClick={handleAssign}
              disabled={assigning}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-60 transition-colors"
            >
              <Plus size={14} />
              {assigning ? "Assigning..." : "Assign Learner"}
            </button>
          </div>
          <div className="text-xs text-muted-foreground">
            Use this after creating a learner account. The dashboard refreshes immediately after assignment.
          </div>
          {assignError && (
            <div className="text-sm text-rose-400">{assignError}</div>
          )}
          {assignSuccess && (
            <div className="text-sm text-emerald-400">{assignSuccess}</div>
          )}
        </div>
      </div>

      <div
        className="bg-card border border-border rounded-[14px] p-6"
        style={{ boxShadow: "var(--card-shadow)" }}
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-5 gap-3">
          <h3 className="font-semibold text-foreground text-sm">
            My Students
          </h3>
          <div className="flex gap-2.5 items-center">
            <button
              type="button"
              onClick={loadStudents}
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-muted px-3 py-2 text-xs font-semibold text-foreground hover:bg-hover transition-colors"
            >
              <RefreshCw size={13} />
              Refresh
            </button>
            <div className="relative">
              <Search
                size={13}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
              />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by name or email..."
                className="bg-muted border border-border rounded-xl pl-8 pr-3 py-2 text-xs text-foreground focus:outline-none focus:border-primary/50 w-56"
              />
            </div>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <RefreshCw size={18} className="animate-spin text-muted-foreground" />
          </div>
        )}

        {!loading && error && (
          <div className="flex items-center gap-2 py-6 text-sm text-rose-400">
            <AlertTriangle size={16} /> {error}
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <p className="text-xs text-muted-foreground py-6 text-center">
            {students.length === 0
              ? "No students assigned to you yet. Use the assign learner box above to link a learner."
              : `No students match "${search}"`}
          </p>
        )}

        <div className="space-y-2">
          {filtered.map((s) => (
            <button
              key={s.user_id}
              type="button"
              onClick={() => go("student-detail")}
              className="w-full flex items-center gap-4 p-3.5 rounded-xl bg-muted/50 hover:bg-muted border border-border/50 hover:border-primary/30 transition-all text-left"
            >
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary/70 to-primary/40 flex items-center justify-center text-xs font-bold text-primary-foreground flex-shrink-0">
                {s.full_name.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-foreground">
                  {s.full_name}
                </div>
                <div className="text-xs text-muted-foreground">
                  {s.email}
                </div>
              </div>
              <ChevronRight size={14} className="text-muted-foreground flex-shrink-0" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
