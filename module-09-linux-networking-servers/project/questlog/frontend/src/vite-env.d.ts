/// <reference types="vite/client" />

// Declared explicitly so `import.meta.env.VITE_API_BASE_URL` (used in
// src/api/questsApi.ts) is a real, checked `string | undefined` rather
// than falling back to `any` -- see that file's own comment, and
// lessons/08-building-the-questlog-api.md, for what this variable is for.
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
