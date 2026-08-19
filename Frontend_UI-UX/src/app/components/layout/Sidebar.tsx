import { useState, useEffect } from "react";
import { Bell, Settings } from "lucide-react";
import type { Role, Screen } from "../../utils/types";
import { NAV } from "../../utils/nav";
import { useAuth } from "../../context/AuthContext";
import { getNotifications } from "../../services/businessApi";
export function Sidebar({
  role, active, setScreen, open, onClose,
}: {
  role: Role; active: Screen; setScreen: (s: Screen) => void;
  open: boolean; onClose: () => void;
}) {
    const { userId } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!userId) return;
    getNotifications(userId)
      .then((data) => setUnreadCount(data.unread_count ?? 0))
      .catch(() => setUnreadCount(0));
  }, [userId, active]); // re-fetch when navigating, so it updates after marking read

  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}
      <div
        className={`
          w-60 flex-shrink-0 bg-sidebar border-r border-sidebar-border flex flex-col h-full
          fixed inset-y-0 left-0 z-50 transition-transform duration-200 ease-in-out
          md:relative md:z-auto md:translate-x-0
          ${open ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        <div className="p-5 border-b border-sidebar-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-primary rounded-xl flex items-center justify-center text-sm text-primary-foreground">✋</div>
            <div>
              <div className="font-bold text-sidebar-foreground text-sm leading-none">SignPath AI</div>
              <div className="text-[11px] text-muted-foreground mt-1">v2.4.0</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 overflow-y-auto space-y-0.5">
          {NAV[role].map(({ screen, label, icon: Icon }) => (
            <button
              key={screen}
              onClick={() => setScreen(screen)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                active === screen
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-sidebar-accent"
              }`}
            >
              <Icon size={16} strokeWidth={1.5} />
              {label}
            </button>
          ))}
        </nav>

        <div className="p-3 border-t border-sidebar-border space-y-0.5">
          {([
            { screen: "notifications" as Screen, label: "Notifications", icon: Bell, badge: unreadCount },
            { screen: "settings" as Screen,      label: "Settings",      icon: Settings },
          ]).map(({ screen, label, icon: Icon, badge }) => (
            <button
              key={screen}
              onClick={() => setScreen(screen)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                active === screen
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-sidebar-accent"
              }`}
            >
              <Icon size={16} strokeWidth={1.5} />
              {label}
              {badge > 0 && (
                <span className="ml-auto w-5 h-5 bg-primary text-primary-foreground text-[10px] font-bold rounded-full flex items-center justify-center">
                  {badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </>
  );
}
