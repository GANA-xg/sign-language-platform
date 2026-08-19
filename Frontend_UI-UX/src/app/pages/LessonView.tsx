import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft,
} from "lucide-react";
import type { Screen } from "@/app/utils/types";
import { HandOverlay } from "../components/shared/HandOverlay";
import { Bdg, PBar } from "../components/shared/Indicators";
import { getLessonById } from "../services/api";

export default function LessonView({ go }: { go: (s: Screen) => void }) {
  const [active, setActive] = useState(3);
  const [lessonTitle, setLessonTitle] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);
    getLessonById("1")
      .then(l => setLessonTitle(l.lesson_name))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const steps = [
    { id: 1, title: "Introduction to Emotions", done: true },
    { id: 2, title: "Happy, Sad, Angry",         done: true },
    { id: 3, title: "Fear, Surprise, Disgust",   done: false },
    { id: 4, title: "Complex Feelings",          done: false },
    { id: 5, title: "Emotional Nuance",          done: false },
    { id: 6, title: "Module Quiz",               done: false },
  ];
  return (
    <div className="flex flex-col md:flex-row h-full overflow-hidden">
      <div className="w-full md:w-56 border-b md:border-b-0 md:border-r border-border bg-[#0a1425] flex flex-col md:p-3 p-3 flex-shrink-0">
        <div className="mb-4 px-1">
          <div className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Module 4</div>
          <div className="font-semibold text-foreground text-sm">Emotions & Mental States</div>
          <PBar pct={33} cls="mt-2" />
          <div className="text-xs text-muted-foreground mt-1">2 of 6 complete</div>
        </div>
        <div className="space-y-0.5 flex-1 overflow-y-auto">
          {steps.map(s => (
            <button
              key={s.id} onClick={() => setActive(s.id)}
              className={`w-full flex items-center gap-2.5 p-2.5 rounded-lg text-left transition-all ${
                active === s.id ? "bg-primary/10 border border-primary/30" : "hover:bg-[#162035]"
              }`}
            >
              <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                s.done ? "bg-emerald-500" : active === s.id ? "border-2 border-primary" : "border-2 border-[#1a2844]"
              }`}>
                {s.done && <Check size={9} className="text-black" />}
                {!s.done && active === s.id && <div className="w-1.5 h-1.5 rounded-full bg-primary" />}
              </div>
              <span className={`text-xs font-medium ${active === s.id ? "text-primary" : s.done ? "text-muted-foreground" : "text-foreground"}`}>
                {s.title}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-2xl mx-auto">
          {error && (
            <div className="mb-4 rounded-xl border border-amber-900/30 bg-amber-950/20 px-4 py-3 text-sm text-amber-200">
              We couldn’t load the lesson details right now. Showing the lesson layout so you can still keep going.
            </div>
          )}
          <div className="flex items-center gap-2 mb-4">
            <Bdg label="Lesson 3" v="info" />
            <Bdg label="8 min" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-5">
            {loading
              ? <span className="inline-block h-7 w-64 bg-surface rounded animate-pulse" />
              : error
              ? <span className="text-rose-400 text-base">Couldn't load lesson title</span>
              : lessonTitle}
          </h2>

          <div className="aspect-video bg-[#0e1a30] rounded-xl mb-6 flex items-center justify-center relative overflow-hidden border border-border">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-violet-900/10" />
            <button className="w-12 h-12 bg-primary hover:bg-primary-active rounded-full flex items-center justify-center transition-colors relative z-10">
              <Play size={18} className="text-black ml-0.5" />
            </button>
            <div className="absolute bottom-3 left-4 text-xs text-muted-foreground">
              Instructor: Dr. Anya Roberts · 3:42
            </div>
          </div>

          <p className="text-muted-foreground text-sm leading-relaxed mb-5">
            In this lesson we explore three powerful emotional signs — FEAR, SURPRISE, and DISGUST. These signs rely heavily on facial expression, which carries as much meaning as the hand shape itself in ASL.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            {["FEAR", "SURPRISE", "DISGUST"].map(sign => (
              <div key={sign} className="bg-[#0e1a30] border border-border rounded-lg p-4 text-center">
                <div className="w-14 h-14 mx-auto mb-3 flex items-center justify-center overflow-hidden">
                  <HandOverlay w={56} h={56} animated={false} />
                </div>
                <div className="font-semibold text-foreground text-sm">{sign}</div>
                <div className="text-xs text-muted-foreground mt-0.5">Tap to practice</div>
              </div>
            ))}
          </div>

          {!loading && !error && (
            <div className="mb-6 rounded-xl border border-dashed border-border bg-muted/20 px-4 py-4 text-sm text-muted-foreground">
              If a lesson video or practice content is missing, you’ll see a friendly fallback instead of a blank screen.
            </div>
          )}

          <h4 className="font-semibold text-foreground mb-2 text-sm">Key Points</h4>
          <ul className="space-y-2 mb-6">
            {[
              "Facial expression carries 70% of the meaning in emotional signs",
              "FEAR uses both hands raised, fingers spread wide, with wide open eyes",
              "SURPRISE is a quick upward flick from both index fingers at the chin",
              "DISGUST involves a twisting motion near the mouth or nose area",
            ].map(p => (
              <li key={p} className="flex items-start gap-2 text-sm text-muted-foreground">
                <div className="w-1.5 h-1.5 rounded-full bg-primary mt-1.5 flex-shrink-0" />
                {p}
              </li>
            ))}
          </ul>

          <div className="flex items-center justify-between pt-4 border-t border-border">
            <button className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
              <ChevronLeft size={15} />
              Previous Lesson
            </button>
            <button
              onClick={() => go("camera-permission")}
              className="flex items-center gap-2 bg-primary hover:bg-primary-active text-black font-bold px-5 py-2.5 rounded-xl transition-colors text-sm"
            >
              <Camera size={15} />
              Start Practice
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
