import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// `defineConfig` now comes from `vitest/config`, not plain `vite`, so this
// one config object can carry both Vite's own options (`plugins`, used by
// `vite dev` / `vite build`, unchanged from Module 04) AND the `test`
// block Vitest reads (new in Module 08) -- `vitest/config` re-exports
// Vite's own `defineConfig` with the `test` key's type added, so nothing
// about `npm run dev` or `npm run build` changes at all. See
// lessons/07-frontend-testing-with-vitest-and-rtl.md.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  test: {
    // A real DOM implementation in plain Node.js -- see
    // lessons/07-frontend-testing-with-vitest-and-rtl.md's "what jsdom
    // actually is" section. Without this, `document`/`window` don't exist
    // at all in the process Vitest runs tests in, and every React
    // Testing Library call would crash immediately.
    environment: "jsdom",
    // Runs once before every test *file* -- see src/test-setup.ts. Deliberately
    // NOT using Vitest's `globals: true` option (which would make `describe`,
    // `it`, `expect` available with no import at all) -- this course's Rule 2
    // ("explain everything, no magic") means every test file below imports
    // these explicitly from "vitest" instead.
    setupFiles: ["./src/test-setup.ts"],
    css: false,
  },
});
