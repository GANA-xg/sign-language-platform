import { useState, useEffect } from "react";
import {
  Moon, Sun,
} from "lucide-react";
import { useTheme } from "../ThemeProvider";
import { useAuth } from "../context/AuthContext";
import { getProfile, updateProfile, changePassword } from "../services/api";
import { Bdg } from "../components/shared/Indicators";

export default function SettingsScreen() {
  const [emailN, setEmailN] = useState(true);
  const [pushN, setPushN] = useState(true);
  const [auto, setAuto] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { role, login, userId } = useAuth();

  // ── Profile ──────────────────────────────────────────────────────────
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSaved, setProfileSaved] = useState(false);

  useEffect(() => {
    getProfile()
      .then(p => {
        setFullName(p.full_name ?? "");
        setEmail(p.email ?? "");
      })
      .catch(() => setProfileError("Couldn't load your profile."))
      .finally(() => setProfileLoading(false));
  }, []);

  const handleSaveProfile = async () => {
    setProfileError(null);
    setProfileSaved(false);
    setProfileSaving(true);
    try {
      await updateProfile({ fullName: fullName, email: email });
      login(role, undefined, undefined, fullName);
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2500);
    } catch (e) {
      setProfileError("Couldn't save your profile. Please try again.");
    } finally {
      setProfileSaving(false);
    }
  };

  // ── Change Password ───────────────────────────────────────────────────
  const [oldPw, setOldPw] = useState("");
  const [newPw, setNewPw] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [pwSaving, setPwSaving] = useState(false);
  const [pwError, setPwError] = useState<string | null>(null);
  const [pwSaved, setPwSaved] = useState(false);

  const handleChangePassword = async () => {
    setPwError(null);
    setPwSaved(false);
    if (!oldPw) {
      setPwError("Enter your current password.");
      return;
    }
    if (newPw.length < 6) {
      setPwError("New password must be at least 6 characters.");
      return;
    }
    if (newPw !== confirmPw) {
      setPwError("New password and confirmation don't match.");
      return;
    }
    setPwSaving(true);
    try {
      await changePassword({ oldPassword: oldPw, newPassword: newPw });
      setOldPw(""); setNewPw(""); setConfirmPw("");
      setPwSaved(true);
      setTimeout(() => setPwSaved(false), 2500);
    } catch (e) {
      setPwError("Couldn't change your password. Check your current password and try again.");
    } finally {
      setPwSaving(false);
    }
  };

  if (profileLoading) {
    return (
      <div className="p-4 md:p-8 max-w-xl mx-auto space-y-6">
        {/* Profile card skeleton */}
        <div className="bg-card border border-border rounded-[14px] p-6 animate-pulse" style={{ boxShadow: "var(--card-shadow)" }}>
          <div className="h-4 w-20 bg-muted rounded mb-5" />
          <div className="flex items-center gap-4 mb-6">
            <div className="w-14 h-14 rounded-full bg-muted flex-shrink-0" />
            <div className="space-y-2 flex-1">
              <div className="h-4 w-32 bg-muted rounded" />
              <div className="h-3 w-48 bg-muted rounded" />
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div className="h-11 bg-muted rounded-xl" />
            <div className="h-11 bg-muted rounded-xl" />
          </div>
          <div className="h-10 w-32 bg-muted rounded-xl" />
        </div>
        {/* Password card skeleton */}
        <div className="bg-card border border-border rounded-[14px] p-6 animate-pulse" style={{ boxShadow: "var(--card-shadow)" }}>
          <div className="h-4 w-36 bg-muted rounded mb-5" />
          <div className="space-y-3 mb-4">
            <div className="h-11 bg-muted rounded-xl" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="h-11 bg-muted rounded-xl" />
              <div className="h-11 bg-muted rounded-xl" />
            </div>
          </div>
          <div className="h-10 w-36 bg-muted rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 md:p-8 max-w-xl mx-auto space-y-6">

      {/* ── Profile ── */}
      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
        <h3 className="font-semibold text-foreground mb-5 text-sm">Profile</h3>
        <div className="flex items-center gap-4 mb-6">
          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center text-xl font-bold text-primary-foreground">
            {fullName ? fullName[0].toUpperCase() : "?"}
          </div>
          <div>
            <div className="font-bold text-foreground">{profileLoading ? "Loading..." : fullName}</div>
            <div className="text-sm text-muted-foreground">{profileLoading ? "" : email}</div>
          </div>
          <Bdg label={role} v="info" />
          <button className="ml-auto text-xs text-primary border border-primary/30 px-3.5 py-2 rounded-xl hover:bg-primary/5 font-medium">
            Edit Photo
          </button>
        </div>

        {userId && (
          <div className="mb-4 px-3 py-2 bg-muted rounded-xl flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Your ID:</span>
            <code className="text-xs text-foreground font-mono select-all">{userId}</code>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-1.5 block">Full Name</label>
            <input
              value={fullName}
              onChange={e => setFullName(e.target.value)}
              disabled={profileLoading}
              className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground text-sm focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-1.5 block">Email</label>
            <input
              value={email}
              onChange={e => setEmail(e.target.value)}
              disabled={profileLoading}
              className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground text-sm focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
            />
          </div>
        </div>

        {profileError && <p className="text-xs text-destructive mb-3">{profileError}</p>}
        {profileSaved && <p className="text-xs text-emerald-600 mb-3">✓ Profile updated successfully.</p>}

        <button
          onClick={handleSaveProfile}
          disabled={profileLoading || profileSaving}
          className="bg-primary hover:bg-primary/90 disabled:opacity-60 text-primary-foreground font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
        >
          {profileSaving ? "Saving..." : "Save Profile"}
        </button>
      </div>

      {/* ── Change Password ── */}
      <div className="bg-card border border-border rounded-[14px] p-6" style={{ boxShadow: "var(--card-shadow)" }}>
        <h3 className="font-semibold text-foreground mb-5 text-sm">Change Password</h3>
        <div className="space-y-3 mb-4">
          <div>
            <label className="text-xs font-semibold text-muted-foreground mb-1.5 block">Current Password</label>
            <input
              type="password"
              value={oldPw}
              onChange={e => setOldPw(e.target.value)}
              className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground text-sm focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-muted-foreground mb-1.5 block">New Password</label>
              <input
                type="password"
                value={newPw}
                onChange={e => setNewPw(e.target.value)}
                className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground text-sm focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
              />
              <p className="text-[11px] text-muted-foreground mt-1">Minimum 6 characters</p>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground mb-1.5 block">Confirm New Password</label>
              <input
                type="password"
                value={confirmPw}
                onChange={e => setConfirmPw(e.target.value)}
                className="w-full bg-card border border-border rounded-xl px-4 py-3 text-foreground text-sm focus:outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
              />
            </div>
          </div>
        </div>

        {pwError && <p className="text-xs text-destructive mb-3">{pwError}</p>}
        {pwSaved && <p className="text-xs text-emerald-600 mb-3">✓ Password changed successfully.</p>}

        <button
          onClick={handleChangePassword}
          disabled={pwSaving}
          className="bg-primary hover:bg-primary/90 disabled:opacity-60 text-primary-foreground font-semibold px-5 py-2.5 rounded-xl transition-colors text-sm"
        >
          {pwSaving ? "Updating..." : "Change Password"}
        </button>
      </div>

      {/* ── Appearance ── */}
      <div className="bg-card border border-border rounded-[14px] p-6 space-y-5" style={{ boxShadow: "var(--card-shadow)" }}>
        <h3 className="font-semibold text-foreground text-sm">Appearance</h3>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {theme === "dark"
              ? <Moon size={16} className="text-primary" />
              : <Sun size={16} className="text-warning" />}
            <div>
              <div className="text-sm font-semibold text-foreground">Dark mode</div>
              <div className="text-xs text-muted-foreground">
                {theme === "dark" ? "Currently using dark theme" : "Currently using light theme"}
              </div>
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className={`w-11 h-6 rounded-full transition-colors relative flex-shrink-0 ${theme === "dark" ? "bg-primary" : "bg-switch-background"}`}
          >
            <div className={`w-4.5 h-4.5 rounded-full bg-white absolute top-[3px] transition-all shadow-sm ${theme === "dark" ? "left-[22px]" : "left-[3px]"}`} />
          </button>
        </div>
      </div>

      {/* ── Preferences ── */}
      <div className="bg-card border border-border rounded-[14px] p-6 space-y-5" style={{ boxShadow: "var(--card-shadow)" }}>
        <h3 className="font-semibold text-foreground text-sm">Preferences</h3>
        {[
          { lbl: "Email notifications",  desc: "Progress updates and reminders by email",          val: emailN, set: setEmailN },
          { lbl: "Push notifications",   desc: "In-app alerts for streaks, badges, and feedback",  val: pushN,  set: setPushN },
          { lbl: "Auto-capture mode",    desc: "Automatically capture signs without a button tap",  val: auto,   set: setAuto  },
        ].map(p => (
          <div key={p.lbl} className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-foreground">{p.lbl}</div>
              <div className="text-xs text-muted-foreground">{p.desc}</div>
            </div>
            <button
              onClick={() => p.set(!p.val)}
              className={`w-11 h-6 rounded-full transition-colors relative flex-shrink-0 ${p.val ? "bg-primary" : "bg-switch-background"}`}
            >
              <div className={`w-4.5 h-4.5 rounded-full bg-white absolute top-[3px] transition-all shadow-sm ${p.val ? "left-[22px]" : "left-[3px]"}`} />
            </button>
          </div>
        ))}
      </div>

    </div>
  );
}