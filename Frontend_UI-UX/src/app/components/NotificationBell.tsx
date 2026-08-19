// NotificationBell.tsx
// Bell icon + dropdown for in-app notifications
// Used in AppShell TopBar — appears on every screen

import { useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";
import {
  getNotifications,
  markNotificationsRead,
} from "../../services/businessApi";
import { useAuth } from "../context/AuthContext";

interface Notification {
  notification_id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

interface NotificationResponse {
  user_id: string;
  notifications: Notification[];
  unread_count: number;
  total: number;
}

export default function NotificationBell() {
  const { userId } = useAuth();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  useEffect(() => {
    fetchNotifications();
  }, [userId]);

  async function fetchNotifications() {
    if (!userId) return;
    setLoading(true);
    setError(null);
    try {
      const data: NotificationResponse = await getNotifications(userId);
      setNotifications(data.notifications ?? []);
    } catch {
      setError("Could not load notifications.");
    } finally {
      setLoading(false);
    }
  }

  // ── Close dropdown when clicking outside ──────────────────────────────────
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [open]);

  async function handleMarkRead(_id: string) {
    try {
      if (!userId) return;
      await markNotificationsRead(userId);
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true }))
      );
    } catch {
      // silent fail
    }
  }

  async function handleMarkAllRead() {
    try {
      if (!userId) return;
      await markNotificationsRead(userId);
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      // silent fail
    }
  }

  return (
    <div className="notification-bell-wrapper" ref={dropdownRef}>
      {/* ── Bell Button ── */}
      <button
        className="notification-bell-btn"
        onClick={() => setOpen((prev) => !prev)}
        aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}`}
        aria-haspopup="true"
        aria-expanded={open}
      >
        <Bell size={22} strokeWidth={1.8} />
        {unreadCount > 0 && (
          <span className="notification-badge" aria-hidden="true">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {/* ── Dropdown Panel ── */}
      {open && (
        <div
          className="notification-dropdown"
          role="dialog"
          aria-label="Notifications panel"
        >
          {/* Header */}
          <div className="notification-header">
            <span className="notification-title">Notifications</span>
            {unreadCount > 0 && (
              <button
                className="mark-all-read-btn"
                onClick={handleMarkAllRead}
                aria-label="Mark all notifications as read"
              >
                Mark all read
              </button>
            )}
          </div>

          {/* Body */}
          <div className="notification-body">
            {loading && (
              <div className="notification-state">Loading...</div>
            )}

            {error && !loading && (
              <div className="notification-state notification-error">
                {error}
                <button
                  onClick={fetchNotifications}
                  className="retry-btn"
                  aria-label="Retry loading notifications"
                >
                  Try again
                </button>
              </div>
            )}

            {!loading && !error && notifications.length === 0 && (
              <div className="notification-state notification-empty">
                <Bell size={32} strokeWidth={1.2} style={{ opacity: 0.3 }} />
                <p>No notifications yet.</p>
                <p className="notification-empty-sub">
                  We'll let you know when something happens!
                </p>
              </div>
            )}

            {!loading &&
              !error &&
              notifications.map((notif) => (
                <div
                  key={notif.notification_id}
                  className={`notification-item${notif.is_read ? "" : " notification-item--unread"}`}
                  onClick={() => !notif.is_read && handleMarkRead(notif.notification_id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      !notif.is_read && handleMarkRead(notif.notification_id);
                    }
                  }}
                  aria-label={`${notif.is_read ? "Read" : "Unread"} notification: ${notif.message}`}
                >
                  {!notif.is_read && (
                    <span className="unread-dot" aria-hidden="true" />
                  )}
                  <div className="notification-item-content">
                    {notif.title && <p className="notification-message font-semibold">{notif.title}</p>}
                    <p className="notification-message">{notif.message}</p>
                    <span className="notification-time">{notif.created_at ? new Date(notif.created_at).toLocaleDateString() : ""}</span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}