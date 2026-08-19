import { useState, useRef, useEffect } from "react";
import { LogOut, Menu, Bell, Award, MessageCircle, Info } from "lucide-react";
import type { Role, Screen } from "@/app/utils/types";
import { SCREEN_LABELS, ROLE_CLS } from "@/app/utils/nav";
import { useAuth } from "../../context/AuthContext";
import { getNotifications, markNotificationsRead } from "../../services/businessApi";

function NotifIcon({ type }: { type: string }) {
  if (type === "achievement") return <Award size={13} className="text-warning" />;
  if (type === "feedback")    return <MessageCircle size={13} className="text-primary" />;
  return <Info size={13} className="text-muted-foreground" />;
}

function NotifIconBg({ type }: { type: string }) {
  if (type === "achievement") return "bg-warning/10";
  if (type === "feedback")    return "bg-primary/10";
  return "bg-muted";
}

export function TopBar({
  role, screen, onLogout, onMenuToggle,
}: { role: Role; screen: Screen; onLogout: () => void; onMenuToggle: () => void }) {
  const { userId } = useAuth();
  const [notifs, setNotifs] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const unread = notifs.filter(n => !n.read).length;

  useEffect(() => {
    if (!open || !userId) return;
    setLoading(true);
    getNotifications(userId)
      .then((data) => {
        setNotifs((data.notifications ?? []).map((n: any) => ({
          id: n.notification_id,
          type: n.notification_type === "badge_earned" ? "achievement" : n.notification_type === "certificate_ready" ? "system" : n.notification_type === "new_recommendation" ? "feedback" : "system",
          title: n.title,
          desc: n.message,
          t: new Date(n.created_at).toLocaleString(),
          read: n.is_read,
        })));
      })
      .catch(() => setNotifs([]))
      .finally(() => setLoading(false));
  }, [open, userId]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    if (open) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  const markAllRead = () => {
    if (!userId) return;
    markNotificationsRead(userId).finally(() => setNotifs(prev => prev.map(n => ({ ...n, read: true }))));
  };
  const markRead = (id: number) => setNotifs(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));

  return (
    <div className="h-16 border-b border-border bg-navbar flex items-center px-4 md:px-6 gap-3 md:gap-4 flex-shrink-0">
      <button
        onClick={onMenuToggle}
        className="md:hidden p-2 -ml-2 rounded-lg hover:bg-hover text-muted-foreground hover:text-foreground transition-colors"
        aria-label="Toggle menu"
      >
        <Menu size={20} strokeWidth={1.5} />
      </button>

      <div className="flex-1 text-base font-semibold text-foreground">
        {SCREEN_LABELS[screen]}
      </div>

      <span className={`text-xs px-3 py-1.5 rounded-full font-medium capitalize ${ROLE_CLS[role]}`}>
        {role}
      </span>

      {/* M3 Day 2: Notification Bell with dropdown */}
      <div className="relative" ref={ref}>
        <button
          onClick={() => setOpen(o => !o)}
          aria-label={`Notifications${unread > 0 ? `, ${unread} unread` : ""}`}
          className="relative p-2 rounded-lg hover:bg-hover text-muted-foreground hover:text-foreground transition-colors"
        >
          <Bell size={18} strokeWidth={1.5} />
          {unread > 0 && (
            <span className="absolute top-1 right-1 w-4 h-4 bg-primary text-primary-foreground text-[9px] font-bold rounded-full flex items-center justify-center leading-none">
              {unread}
            </span>
          )}
        </button>

        {open && (
          <div className="absolute right-0 top-full mt-2 w-80 bg-card border border-border rounded-xl shadow-lg z-50 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <span className="text-sm font-semibold text-foreground">Notifications</span>
              {unread > 0 && (
                <button
                  onClick={markAllRead}
                  className="text-xs text-primary hover:text-primary/80 font-semibold"
                >
                  Mark all read
                </button>
              )}
            </div>
            <div className="max-h-80 overflow-y-auto">
              {loading ? (
                <div className="px-4 py-8 text-center text-xs text-muted-foreground">Loading notifications…</div>
              ) : notifs.length === 0 ? (
                <div className="px-4 py-8 text-center text-xs text-muted-foreground">
                  No notifications yet
                </div>
              ) : (
                notifs.map(n => (
                  <button
                    key={n.id}
                    onClick={() => markRead(n.id)}
                    className={`w-full flex items-start gap-3 px-4 py-3 text-left hover:bg-hover transition-colors border-b border-border/50 last:border-0 ${
                      !n.read ? "bg-primary/5" : ""
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${NotifIconBg({ type: n.type })}`}>
                      <NotifIcon type={n.type} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                        {n.title}
                        {!n.read && <div className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />}
                      </div>
                      <div className="text-xs text-muted-foreground mt-0.5 truncate">{n.desc}</div>
                      <div className="text-[10px] text-muted-foreground mt-1">{n.t}</div>
                    </div>
                  </button>
                ))
              )}
            </div>
            <div className="px-4 py-2.5 border-t border-border">
              <button className="w-full text-xs text-primary hover:text-primary/80 font-semibold text-center">
                View all notifications
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center text-xs font-bold text-primary-foreground">
        M
      </div>

      <button
        onClick={onLogout}
        aria-label="Log out"
        className="text-muted-foreground hover:text-foreground transition-colors"
      >
        <LogOut size={16} strokeWidth={1.5} />
      </button>
    </div>
  );
}
