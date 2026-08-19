import { useState, useEffect } from "react";
import {
  Home, BookOpen, Camera, CheckSquare, MessageCircle, TrendingUp,
  Award, Users, Settings, Bell, ChevronRight, Play, RotateCcw,
  ArrowRight, Eye, EyeOff, Clock, Zap, Target, Activity,
  Shield, Server, UserCheck, LogOut, Plus, Search, Filter,
  Download, Share2, AlertTriangle, CheckCircle, XCircle, Info,
  SkipForward, Calendar, Lock, Mail, Check, ChevronLeft,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getNotifications, markNotificationsRead } from "../services/businessApi";

export default function NotificationsPanel() {
  const { userId } = useAuth();
  const [notifs, setNotifs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    getNotifications(userId)
      .then((data) => {
        setNotifs((data.notifications ?? []).map((n: any) => ({
          type: n.notification_type === "badge_earned" ? "achievement" : n.notification_type === "certificate_ready" ? "system" : n.notification_type === "new_recommendation" ? "feedback" : "system",
          title: n.title,
          desc: n.message,
          t: new Date(n.created_at).toLocaleString(),
          read: n.is_read,
        })));
      })
      .finally(() => setLoading(false));
  }, [userId]);

  const markAllRead = () => {
    if (!userId) return;
    markNotificationsRead(userId).finally(() => {
      setNotifs(prev => prev.map(n => ({ ...n, read: true })));
    });
  };

  return (
    <div className="p-8 max-w-2xl mx-auto space-y-3">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-bold text-foreground">Notifications</h2>
        <button onClick={markAllRead} className="text-xs text-primary hover:text-primary/80 font-semibold">Mark all read</button>
      </div>
      {loading ? (
        <div className="p-6 text-center text-sm text-muted-foreground">Loading notifications…</div>
      ) : notifs.length === 0 ? (
        <div className="p-6 text-center space-y-2 rounded-xl border border-border bg-card">
          <div className="text-sm font-semibold text-foreground">You’re all caught up</div>
          <div className="text-sm text-muted-foreground">No unread notifications right now. New updates will appear here.</div>
        </div>
      ) : (
        notifs.map((n, i) => (
          <div key={i} className={`p-4 rounded-xl border transition-all ${n.read ? "border-border bg-card opacity-60" : "border-primary/20 bg-primary/5"}`}>
            <div className="flex items-start gap-3.5">
              <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                n.type === "achievement" ? "bg-warning/10" :
                n.type === "feedback"    ? "bg-primary/10" :
                "bg-muted"
              }`}>
                {n.type === "achievement" ? <Award size={14} className="text-warning" /> :
                 n.type === "feedback"    ? <MessageCircle size={14} className="text-primary" /> :
                 <Info size={14} className="text-muted-foreground" />}
              </div>
              <div className="flex-1">
                <div className="text-sm font-semibold text-foreground flex items-center gap-2">
                  {n.title}
                  {!n.read && <div className="w-2 h-2 rounded-full bg-primary" />}
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">{n.desc}</div>
              </div>
              <span className="text-xs text-muted-foreground flex-shrink-0">{n.t}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
