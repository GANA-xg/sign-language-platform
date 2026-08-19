import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft,
} from "lucide-react";

export default function OnboardingScreen({ onDone }: { onDone: () => void }) {
  const [step, setStep] = useState(0);
  const Qs = [
    { q: "Have you learned any sign language before?", opts: ["Never tried it", "Learned a few basics", "Know conversational ASL", "Advanced / fluent"] },
    { q: "What is your primary goal?", opts: ["Personal communication", "Work with Deaf/HoH community", "Professional certification", "Just exploring"] },
    { q: "How much time can you practice daily?", opts: ["5–10 min / day", "15–20 min / day", "30+ min / day", "Flexible schedule"] },
  ];
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <div className="w-full max-w-md">
        <div className="flex gap-1.5 mb-8">
          {Qs.map((_, i) => (
            <div key={i} className={`h-1 flex-1 rounded-full transition-all ${i <= step ? "bg-primary" : "bg-border"}`} />
          ))}
        </div>
        <div className="text-xs text-muted-foreground mb-2">Question {step + 1} of {Qs.length}</div>
        <h2 className="text-2xl font-bold text-foreground mb-6">{Qs[step].q}</h2>
        <div className="space-y-3">
          {Qs[step].opts.map(opt => (
            <button
              key={opt}
              onClick={() => step < Qs.length - 1 ? setStep(s => s + 1) : onDone()}
              className="w-full p-4 rounded-xl border border-border bg-card hover:border-primary/40 hover:bg-primary/5 text-left text-foreground text-sm font-medium transition-all"
            >
              {opt}
            </button>
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-muted-foreground">
          Your answers help us place you at the right starting level
        </p>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════════════
// B. LEARNER SCREENS
// ══════════════════════════════════════════════════════════════════════════
