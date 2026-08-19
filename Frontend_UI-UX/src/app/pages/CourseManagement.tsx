import { useState, useEffect } from "react";
import {
  BookOpen,
  Plus,
  Pencil,
  Trash2,
  X,
  RefreshCw,
  AlertTriangle,
  Save,
} from "lucide-react";
import { Bdg } from "../components/shared/Indicators";
import {
  getCourses,
  getLessons,
  createLesson,
  updateLesson,
  deleteLesson,
} from "../services/api";

interface Course {
  id: string | number;
  title: string;
  difficulty: string;
  lessons?: number;
  desc?: string;
  hrs?: string;
  pct?: number;
  cat?: string;
}

interface LessonForm {
  module_id: number;
  title: string;
  description: string;
  sequence_order: number;
  difficulty_level: string;
  category: string;
  is_published: boolean;
}

const EMPTY_FORM: LessonForm = {
  module_id: 1,
  title: "",
  description: "",
  sequence_order: 1,
  difficulty_level: "beginner",
  category: "Alphabet",
  is_published: true,
};

export default function CourseManagement() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<LessonForm>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getCourses()
      .then((data) => setCourses(data ?? []))
      .catch(() =>
        setError("Couldn't load courses. Is the Backend API running on port 8000?")
      )
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const openAdd = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setShowForm(true);
  };

  const openEdit = (c: Course) => {
    setEditingId(c.id as number);
    setForm({
      module_id: c.id as number,
      title: c.title,
      description: c.desc ?? "",
      sequence_order: 1,
      difficulty_level: (c.difficulty ?? "beginner").toLowerCase(),
      category: c.cat ?? "Alphabet",
      is_published: true,
    });
    setShowForm(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      if (editingId !== null) {
        await updateLesson(editingId, {
          module_id: form.module_id,
          title: form.title,
          description: form.description || null,
          sequence_order: form.sequence_order,
          difficulty_level: form.difficulty_level,
          category: form.category,
          is_published: form.is_published,
        });
      } else {
        await createLesson({
          module_id: form.module_id,
          title: form.title,
          description: form.description || null,
          sequence_order: form.sequence_order,
          difficulty_level: form.difficulty_level,
          category: form.category,
          is_published: form.is_published,
        });
      }
      setShowForm(false);
      load();
    } catch {
      setError("Failed to save. Check your connection and try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      await deleteLesson(id);
      load();
    } catch {
      setError("Failed to delete. Check your connection and try again.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-foreground">My Courses</h2>
        <div className="flex gap-2">
          <button
            onClick={load}
            className="flex items-center gap-2 border border-border bg-muted hover:bg-hover text-foreground text-xs font-bold px-4 py-2.5 rounded-xl transition-colors"
          >
            <RefreshCw size={14} /> Refresh
          </button>
          <button
            onClick={openAdd}
            className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-bold px-4 py-2.5 rounded-xl transition-colors"
          >
            <Plus size={14} /> Add Course
          </button>
        </div>
      </div>

      {loading && (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="bg-card border border-border rounded-[14px] p-5 animate-pulse"
            >
              <div className="h-4 bg-surface rounded w-1/3 mb-2" />
              <div className="h-3 bg-surface rounded w-1/2" />
            </div>
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="flex flex-col items-center gap-3 py-16 text-center">
          <AlertTriangle size={28} className="text-rose-400" />
          <p className="text-sm text-muted-foreground">{error}</p>
          <button
            onClick={load}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold bg-primary text-black hover:bg-primary-active transition-colors"
          >
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      )}

      {!loading && !error && courses.length === 0 && (
        <div className="flex flex-col items-center gap-2 py-16 text-center">
          <BookOpen size={28} className="text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            No courses found. Create one to get started.
          </p>
        </div>
      )}

      {!loading && !error && courses.length > 0 && (
        <div className="space-y-3">
          {courses.map((c) => (
            <div
              key={c.id}
              className="bg-card border border-border rounded-[14px] p-5 flex items-center gap-4"
              style={{ boxShadow: "var(--card-shadow)" }}
            >
              <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                <BookOpen size={17} className="text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-foreground text-sm">
                  {c.title}
                </div>
                <div className="text-xs text-muted-foreground">
                  {c.lessons ?? "—"} lessons · {c.difficulty ?? "Beginner"}
                  {c.hrs ? ` · ${c.hrs}` : ""}
                </div>
              </div>
              <Bdg
                label={c.difficulty ?? "Beginner"}
                v={
                  c.difficulty === "Beginner"
                    ? "success"
                    : c.difficulty === "Intermediate"
                    ? "warning"
                    : "info"
                }
              />
              <div className="flex gap-2">
                <button
                  onClick={() => openEdit(c)}
                  className="text-xs bg-muted border border-border px-3 py-2 rounded-xl text-muted-foreground hover:text-foreground hover:border-primary/30 transition-colors flex items-center gap-1.5"
                >
                  <Pencil size={12} /> Edit
                </button>
                <button
                  onClick={() => handleDelete(c.id as number)}
                  disabled={deletingId === c.id}
                  className="text-xs bg-muted border border-border px-3 py-2 rounded-xl text-rose-400 hover:text-rose-300 hover:border-rose-400/30 disabled:opacity-50 transition-colors flex items-center gap-1.5"
                >
                  <Trash2 size={12} /> {deletingId === c.id ? "..." : "Delete"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Add / Edit Modal ── */}
      {showForm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setShowForm(false)}
        >
          <div
            className="bg-card border border-border rounded-2xl w-full max-w-lg mx-4 p-6 space-y-5"
            style={{ boxShadow: "var(--card-shadow)" }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-foreground">
                {editingId !== null ? "Edit Course" : "Add Course"}
              </h3>
              <button
                onClick={() => setShowForm(false)}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-foreground mb-1.5">
                  Title *
                </label>
                <input
                  value={form.title}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, title: e.target.value }))
                  }
                  placeholder="e.g. Letter A"
                  className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1.5">
                    Module ID
                  </label>
                  <input
                    type="number"
                    value={form.module_id}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        module_id: Number(e.target.value),
                      }))
                    }
                    className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1.5">
                    Sequence Order
                  </label>
                  <input
                    type="number"
                    value={form.sequence_order}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        sequence_order: Number(e.target.value),
                      }))
                    }
                    className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1.5">
                    Difficulty
                  </label>
                  <select
                    value={form.difficulty_level}
                    onChange={(e) =>
                      setForm((f) => ({
                        ...f,
                        difficulty_level: e.target.value,
                      }))
                    }
                    className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-foreground mb-1.5">
                    Category
                  </label>
                  <select
                    value={form.category}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, category: e.target.value }))
                    }
                    className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50"
                  >
                    <option value="Alphabet">Alphabet</option>
                    <option value="Numbers">Numbers</option>
                    <option value="Phrases">Phrases</option>
                    <option value="Specialized">Specialized</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-foreground mb-1.5">
                  Description
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, description: e.target.value }))
                  }
                  placeholder="Optional course description..."
                  rows={3}
                  className="w-full bg-muted border border-border rounded-xl px-3 py-2 text-sm text-foreground focus:outline-none focus:border-primary/50 resize-none"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.is_published}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, is_published: e.target.checked }))
                  }
                  className="accent-primary"
                />
                <label className="text-xs font-semibold text-foreground">
                  Published
                </label>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 text-xs font-semibold text-muted-foreground hover:text-foreground rounded-xl border border-border bg-muted hover:bg-hover transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !form.title.trim()}
                className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-primary-foreground bg-primary hover:bg-primary/90 disabled:opacity-50 rounded-xl transition-colors"
              >
                <Save size={13} />
                {saving
                  ? "Saving..."
                  : editingId !== null
                  ? "Save Changes"
                  : "Create Course"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
