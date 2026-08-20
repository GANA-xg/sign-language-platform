
import { createRoot } from "react-dom/client";
import App from "./app/App.tsx";
import { ThemeProvider } from "./app/ThemeProvider.tsx";
import "./styles/index.css";
import { startKeepAlive } from "./app/services/aiApi.js";
startKeepAlive();

// Keep backend services warm
const backendUrl = import.meta.env.VITE_API_URL ?? "https://ai-signlanguage-backend-api-signlanguage-gagi.onrender.com";
const bizUrl = import.meta.env.VITE_BUSINESS_API_URL ?? "https://ai-signlanguage-business-logic.onrender.com";
setInterval(() => { fetch(`${backendUrl}/docs`).catch(()=>{}); fetch(`${bizUrl}/docs`).catch(()=>{}); }, 10 * 60 * 1000);

createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <App />
  </ThemeProvider>
);
