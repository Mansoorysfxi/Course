/// <reference types="vite/client" />

// Declared explicitly so `import.meta.env.VITE_API_BASE_URL` (used in
// src/api/questsApi.ts) is a real, checked `string | undefined` rather
// than falling back to `any` -- see that file's own comment, and
// lessons/08-building-the-questlog-api.md, for what this variable is for.
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  // NEW in Module 11 -- read by src/monitoring.ts. See
  // lessons/06-monitoring-logging-and-error-tracking.md.
  readonly VITE_SENTRY_DSN?: string;
  readonly VITE_ENVIRONMENT?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
