
import { createRoot } from "react-dom/client";
import App from "./app/App.tsx";
import { ThemeProvider } from "./app/ThemeProvider.tsx";
import "./styles/index.css";
import { startKeepAlive } from "./app/services/aiApi.js";
startKeepAlive();

createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <App />
  </ThemeProvider>
);
