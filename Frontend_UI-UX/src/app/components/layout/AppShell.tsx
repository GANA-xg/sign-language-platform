import { useState } from "react";
import { Outlet, useLocation, useNavigate } from "react-router";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { useAuth } from "../../context/AuthContext";
import { SCREEN_PATH, PATH_SCREEN } from "@/app/utils/nav";
import type { Screen } from "@/app/utils/types";

export function AppShell() {
  const { role, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const activeScreen: Screen = PATH_SCREEN[location.pathname] ?? "learner-dashboard";
  const go = (s: Screen) => {
    navigate(SCREEN_PATH[s]);
    setSidebarOpen(false);
  };

  const fullHeight = ["practice", "assessment", "lesson"].includes(activeScreen);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar
        role={role}
        active={activeScreen}
        setScreen={go}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopBar
          role={role}
          screen={activeScreen}
          onLogout={handleLogout}
          onMenuToggle={() => setSidebarOpen((o) => !o)}
        />
        <main className={`flex-1 ${fullHeight ? "overflow-hidden" : "overflow-auto"}`}>
          <Outlet context={{ go }} />
        </main>
      </div>
    </div>
  );
}