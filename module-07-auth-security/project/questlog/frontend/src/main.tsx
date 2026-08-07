import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import "./index.css";
import App from "./App.tsx";
import { AuthProvider } from "./context/AuthContext.tsx";
import { QuestsProvider } from "./context/QuestsContext.tsx";

// `<AuthProvider>` wraps `<QuestsProvider>`, in that order, deliberately
// -- new in Module 07. `QuestsProvider` calls `useAuth()` internally
// (src/context/QuestsContext.tsx) to decide whether there's even a
// logged-in user to fetch quests for, which only works if an
// `<AuthProvider>` is already somewhere above it in the tree. See
// Module 04, lessons/06-context.md for why a Provider only makes its
// value available to components rendered *inside* it, never to
// components above or beside it.
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <QuestsProvider>
          <App />
        </QuestsProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
