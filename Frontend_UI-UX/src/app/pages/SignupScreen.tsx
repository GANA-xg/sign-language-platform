import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft,
} from "lucide-react";
import type { Role } from "../lib/types";
import { registerUser, loginUser } from "../services/api";

export default function SignupScreen({
  onSignup, goLogin,
}: { onSignup: (role: Role, token: string, userId: string) => void; goLogin: () => void }) {
  const [role, setRole] = useState<Role>("learner");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSignup = async () => {
    setLoading(true);
    setError(null);
    try {
      await registerUser({ name, email, password, role });
      // Registration doesn't return a token — log in immediately after
      // to get a real access token, matching the role just registered.
      const loginData = await loginUser({ email, password, role });
      onSignup(loginData.role as Role, loginData.access_token, loginData.user?.user_id);
    } catch (e) {
      setError(e.message || "Couldn't create your account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const ROLES: { v: Role; label: string; desc: string; icon: React.ElementType }[] = [
    { v: "learner",    label: "Learner",               desc: "Learn at your own pace",     icon: BookOpen },
    { v: "instructor", label: "Instructor",             desc: "Teach and manage classes",   icon: Users },
    { v: "trainer",    label: "Accessibility Trainer",  desc: "Validate AI assessments",    icon: UserCheck },
    { v: "admin",      label: "Administrator",          desc: "Manage platform and users",  icon: Shield },
  ];
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <div className="w-full max-w-lg">
        <div className="flex items-center gap-2.5 mb-8">
          <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center text-base">✋</div>
          <span className="font-bold text-lg text-foreground">SignPath AI</span>
        </div>
        <h2 className="text-2xl font-bold text-foreground mb-1">Create your account</h2>
        <p className="text-muted-foreground text-sm mb-6">Choose your role to get started</p>

        <div className="grid grid-cols-2 gap-3 mb-6">
          {ROLES.map(({ v, label, desc, icon: Icon }) => (
            <button
              key={v} onClick={() => setRole(v)}
              className={`p-4 rounded-xl border text-left transition-all ${
                role === v
                  ? "border-primary/60 bg-primary/10"
                  : "border-border bg-[#0e1a30] hover:border-primary/20"
              }`}
            >
              <Icon size={17} className={role === v ? "text-primary mb-2" : "text-muted-foreground mb-2"} />
              <div className="text-sm font-semibold text-foreground">{label}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{desc}</div>
            </button>
          ))}
        </div>

        <div className="space-y-3 mb-5">
          <div>
            <label className="text-xs font-semibold text-foreground mb-1.5 block">Full name</label>
            <input
              value={name} onChange={e => setName(e.target.value)}
              className="w-full bg-[#0e1a30] border border-border rounded-lg px-4 py-2.5 text-foreground text-sm focus:outline-none focus:border-primary/50"
              placeholder="Maya Chen"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-foreground mb-1.5 block">Email</label>
            <input
              value={email} onChange={e => setEmail(e.target.value)}
              className="w-full bg-[#0e1a30] border border-border rounded-lg px-4 py-2.5 text-foreground text-sm focus:outline-none focus:border-primary/50"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-foreground mb-1.5 block">Password</label>
            <input
              type="password"
              value={password} onChange={e => setPassword(e.target.value)}
              className="w-full bg-[#0e1a30] border border-border rounded-lg px-4 py-2.5 text-foreground text-sm focus:outline-none focus:border-primary/50"
              placeholder="Min. 8 characters"
            />
          </div>
        </div>

        {error && (
          <div className="mb-4 px-3 py-2.5 rounded-lg bg-rose-950/40 border border-rose-900/40 text-rose-400 text-xs">
            {error}
          </div>
        )}

        <button
          onClick={handleSignup}
          disabled={loading}
          className="w-full bg-primary hover:bg-primary-active disabled:opacity-60 disabled:cursor-not-allowed text-black font-bold py-3 rounded-xl transition-colors mb-4 text-sm"
        >
          {loading ? "Creating account..." : "Create account"}
        </button>
        <p className="text-center text-xs text-muted-foreground">
          Already have an account?{" "}
          <button onClick={goLogin} className="text-primary hover:text-primary-active font-semibold">Sign in</button>
        </p>
      </div>
    </div>
  );
}
