import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import "./index.css";
import App from "./App.tsx";

// Complete -- react-router is already installed, and <BrowserRouter> is
// already wrapping <App /> here, exactly as lessons/00-setup.md and
// lessons/08-react-router.md describe. Your work is entirely inside
// App.tsx and src/pages/.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
