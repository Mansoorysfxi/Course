/**
 * See lessons/07-frontend-testing-with-vitest-and-rtl.md's "mocking a
 * hook" section for exactly what `vi.mock` below does and why it's the
 * right tool here: ProtectedRoute.tsx's entire job is deciding what to
 * render based on whatever `useAuth()` returns (see that file) -- this
 * test suite controls that return value directly, on a case-by-case
 * basis, instead of wiring up a real `<AuthProvider>` (which would mean
 * a real signup/login round trip just to test three lines of
 * conditional rendering).
 */
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { ProtectedRoute } from "./ProtectedRoute";
import { useAuth } from "../context/AuthContext";

// Replaces the entire "../context/AuthContext" module, for every test in
// this file, with a fake whose `useAuth` export is a Vitest mock function
// -- see lessons/03-parametrize-and-mocking.md for `vi.mock`'s general
// shape (this is the frontend/Vitest equivalent of Python's
// `unittest.mock.patch`, applied to an entire ES module import instead of
// one attribute). Each test below then calls
// `vi.mocked(useAuth).mockReturnValue(...)` to decide what THIS test's
// fake `useAuth()` returns.
vi.mock("../context/AuthContext", () => ({
  useAuth: vi.fn(),
}));

function renderProtectedRoute() {
  return render(
    <MemoryRouter initialEntries={["/quests/new"]}>
      <Routes>
        <Route path="/login" element={<p>Login page</p>} />
        <Route
          path="/quests/new"
          element={
            <ProtectedRoute>
              <p>Secret quest form</p>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  it("shows a loading indicator while the auth check is still in flight", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      loading: true,
      error: null,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    renderProtectedRoute();

    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.queryByText("Secret quest form")).not.toBeInTheDocument();
    expect(screen.queryByText("Login page")).not.toBeInTheDocument();
  });

  it("redirects to /login when there is no logged-in user", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      loading: false,
      error: null,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    renderProtectedRoute();

    // The protected content never rendered, and the route we ended up on
    // (via react-router's own <Navigate>) is /login's page instead.
    expect(screen.queryByText("Secret quest form")).not.toBeInTheDocument();
    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("renders the protected content when a user is logged in", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: "user-1", email: "hero@example.com", createdAt: "2026-01-01T00:00:00.000Z" },
      loading: false,
      error: null,
      login: vi.fn(),
      signup: vi.fn(),
      logout: vi.fn(),
    });

    renderProtectedRoute();

    expect(screen.getByText("Secret quest form")).toBeInTheDocument();
    expect(screen.queryByText("Login page")).not.toBeInTheDocument();
  });
});
