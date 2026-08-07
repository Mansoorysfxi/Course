import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import * as authApi from "../api/authApi";
import { clearStoredToken, setStoredToken, getStoredToken } from "../api/http";
import type { AuthUser } from "../types/auth";

interface AuthContextValue {
  user: AuthUser | null;
  /** True only during the one-time "is there already a valid token from
   * a previous visit" check this provider does on mount -- see the
   * effect below. Every page that requires auth (src/components/
   * ProtectedRoute.tsx) waits for this to become false before deciding
   * whether to redirect to /login, so a page reload never flashes the
   * login screen for a fraction of a second before this check finishes. */
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Owns exactly one piece of truth this whole app cares about: "who, if
 * anyone, is currently logged in." Every other component reaches this
 * through the `useAuth()` hook below, never by importing `AuthContext`
 * directly -- the same pattern src/context/QuestsContext.tsx (Module 05)
 * already established. See lessons/06-building-signup-login.md's "the
 * frontend's half of the contract" section for the full walkthrough of
 * every function below.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Runs exactly once, when the app first loads. A JWT in
    // localStorage (see src/api/http.ts) survives a page reload even
    // though this component's own `user` state does not -- React state
    // always starts fresh on every load, the same "state is just a
    // variable that resets unless something re-derives it" lesson
    // Module 04 taught, just now colliding with the fact that the token
    // itself lives somewhere React doesn't manage at all. This effect is
    // that "something": if a token exists, ask the backend whose it is
    // (`GET /api/auth/me`) and restore `user` from the answer; if there
    // is no token, or the backend rejects it (expired, tampered with,
    // the account no longer exists), treat this exactly like a fresh,
    // logged-out visit.
    let cancelled = false;

    async function restoreSession() {
      if (!getStoredToken()) {
        setLoading(false);
        return;
      }
      try {
        const currentUser = await authApi.fetchCurrentUser();
        if (!cancelled) {
          setUser(currentUser);
        }
      } catch {
        // http.ts's request() already cleared the stored token itself
        // if this failed with a 401 -- nothing further to clean up here.
        if (!cancelled) {
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    restoreSession();

    return () => {
      cancelled = true;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const token = await authApi.login(email, password);
      setStoredToken(token.access_token);
      const currentUser = await authApi.fetchCurrentUser();
      setUser(currentUser);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not log in.");
      throw err;
    }
  }, []);

  const signup = useCallback(
    async (email: string, password: string) => {
      setError(null);
      try {
        await authApi.signup(email, password);
        // Signing up does not, by itself, log you in -- POST /api/auth/signup
        // returns the new account, not a token (backend/app/routers/auth.py).
        // This app's UX choice is to immediately follow signup with a real
        // login call, so a new user never has to re-type their password on
        // a second screen -- but that is two genuinely separate HTTP
        // requests, not one, and the second one can still fail (e.g. if it
        // somehow doesn't match) independently of the first succeeding.
        await login(email, password);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not sign up.");
        throw err;
      }
    },
    [login],
  );

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const value: AuthContextValue = { user, loading, error, login, signup, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth() must be called from inside an <AuthProvider>.");
  }
  return context;
}
