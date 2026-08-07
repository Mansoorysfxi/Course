import { request, requestForm } from "./http";
import type { AuthToken, AuthUser } from "../types/auth";

/** `POST /api/auth/signup` -- plain JSON, like every other non-login
 * request in this app. Returns the newly created account (never a
 * token) -- see src/context/AuthContext.tsx's `signup`, which logs the
 * new account in immediately afterward as a separate, second call to
 * `login` below, exactly the two real HTTP requests a signup-then-login
 * flow actually takes. */
export function signup(email: string, password: string): Promise<AuthUser> {
  return request<AuthUser>("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

/** `POST /api/auth/login` -- form-encoded, not JSON, because the backend
 * route this calls uses FastAPI's `OAuth2PasswordRequestForm` (see
 * backend/app/routers/auth.py and lessons/05-oauth2-conceptual.md for
 * why). The form's two field names, `username` and `password`, are fixed
 * by that class -- `username` is where this app's *email* goes, since
 * QuestLog has no separate username concept at all. */
export function login(email: string, password: string): Promise<AuthToken> {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  return requestForm<AuthToken>("/api/auth/login", form);
}

/** `GET /api/auth/me` -- a protected route; only succeeds if a valid
 * token is currently stored (see src/api/http.ts's `request()`). Used by
 * AuthContext once on app load to answer "is there already a logged-in
 * user from a previous visit," since a JWT in localStorage survives a
 * page reload even though React's own state does not. */
export function fetchCurrentUser(): Promise<AuthUser> {
  return request<AuthUser>("/api/auth/me");
}
