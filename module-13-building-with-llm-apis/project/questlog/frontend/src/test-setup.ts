/**
 * Runs once before every test file (see vite.config.ts's `test.setupFiles`).
 * Two jobs, both explained in
 * lessons/07-frontend-testing-with-vitest-and-rtl.md:
 *
 * 1. `@testing-library/jest-dom/vitest` extends Vitest's own `expect`
 *    with extra, DOM-specific matchers this course's tests use --
 *    `toBeInTheDocument()`, `toHaveTextContent()`, `toBeDisabled()`, and
 *    so on. Without this import, those matchers don't exist and calling
 *    one throws a plain "not a function" error instead of a readable
 *    assertion failure.
 * 2. `cleanup()` unmounts and removes from the (jsdom) page whatever
 *    React Testing Library rendered in the *previous* test. Jest runs
 *    this automatically because it defines `afterEach` as a global by
 *    default; this project deliberately does not enable Vitest's
 *    `globals: true` (see vite.config.ts), so this file wires the exact
 *    same cleanup up by hand, explicitly, once, here -- every test file
 *    benefits without needing to repeat this itself.
 */
import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

afterEach(() => {
  cleanup();
});
