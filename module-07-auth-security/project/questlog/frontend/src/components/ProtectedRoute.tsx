import type { ReactNode } from "react";
import { Navigate } from "react-router";
import { useAuth } from "../context/AuthContext";
import { LoadingSpinner } from "./LoadingSpinner";

/**
 * Wraps a page element and only ever renders it for a logged-in user --
 * see App.tsx for exactly which routes are wrapped in this. This is the
 * **frontend** half of "protecting" a route; it exists purely for user
 * experience (redirecting to /login instead of showing a broken page
 * that immediately fails every request). It is not a security boundary
 * by itself -- see lessons/07-protecting-routes-with-dependencies.md's
 * "the frontend check is not the real lock" box: the *actual* protection
 * is the backend's `CurrentUser` dependency (backend/app/dependencies.py),
 * which rejects an unauthenticated request no matter what the frontend
 * did or didn't check first. A learner who opens their browser's dev
 * tools and calls `fetch()` directly, bypassing this component entirely,
 * still cannot read another user's quests -- try it, per Exercise 04.
 */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    // Still checking whether a stored token is valid (AuthContext's own
    // effect) -- render nothing conclusive yet, rather than redirecting
    // to /login for a split second and then immediately back.
    return <LoadingSpinner />;
  }

  if (!user) {
    // `replace` means this navigation doesn't add a new browser-history
    // entry -- pressing the back button from /login won't bounce you
    // right back to the page that redirected you here.
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
