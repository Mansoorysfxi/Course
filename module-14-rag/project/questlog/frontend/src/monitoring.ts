// NEW in Module 11 -- see
// lessons/06-monitoring-logging-and-error-tracking.md for the full
// explanation of what Sentry is, what it's for, and why frontend and
// backend each get their own, separate initialization even though
// they report to the same Sentry project.
//
// This file is imported for its *side effect* (calling
// `Sentry.init(...)`) -- see src/main.tsx's very first import. Kept in
// its own file, rather than inlined at the top of main.tsx, purely so
// this one, self-contained "is monitoring turned on, and with what
// settings" decision lives in exactly one place, the same way
// app/config.py centralizes the backend's equivalent decision.
import * as Sentry from "@sentry/react";

// `import.meta.env.VITE_SENTRY_DSN` -- exactly the same mechanism this
// project already uses for `VITE_API_BASE_URL` (see
// src/api/questsApi.ts and vite-env.d.ts): a `VITE_`-prefixed
// environment variable, read and baked into the compiled JavaScript at
// **build time** by Vite (never at runtime -- there is no server-side
// process here to read a "real" environment variable from once this
// code is just static files served by Nginx). Every lesson/exercise in
// this course that never sets `VITE_SENTRY_DSN` builds a frontend with
// Sentry completely inert -- `Sentry.init` is simply never called below,
// exactly mirroring the backend's `if settings.sentry_dsn:` guard in
// app/main.py.
const dsn = import.meta.env.VITE_SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    environment: import.meta.env.VITE_ENVIRONMENT ?? "development",
    // Sends 10% of page loads/navigations as full performance traces --
    // the same conservative default as the backend's own
    // `traces_sample_rate=0.1` (app/main.py), and for the same reason:
    // real signal at a fraction of the event volume (and therefore a
    // fraction of the free-tier quota) full tracing would cost.
    tracesSampleRate: 0.1,
  });
}

export {};
