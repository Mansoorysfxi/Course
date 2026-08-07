/**
 * The shared, low-level HTTP layer both src/api/authApi.ts and
 * src/api/questsApi.ts build on. Extracted from Module 06's
 * questsApi.ts (which had this `request()` function private to itself)
 * because Module 07 needs the exact same fetch/error-handling machinery
 * from a second file too, and duplicating it would violate the same
 * "one seam" discipline the backend's app/repository.py docstring
 * describes -- see lessons/06-building-signup-login.md's "why a shared
 * http.ts" box.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// The browser's own persistent key-value store (survives page reloads
// and closing the tab, unlike React state) -- this is where this
// frontend keeps its JWT between page loads. See
// lessons/06-building-signup-login.md's "where does the frontend put the
// token" section for the trade-offs against the alternative (a cookie),
// and why this course picks localStorage specifically.
const TOKEN_STORAGE_KEY = "questlog_token";

export function getStoredToken(): string | null {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setStoredToken(token: string): void {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearStoredToken(): void {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

/** Thrown specifically for a 401 response, so calling code (see
 * src/context/QuestsContext.tsx) can tell "you're not logged in (or your
 * session expired)" apart from every other kind of failure, and react to
 * it differently (by sending the user back to /login) instead of just
 * showing a generic error banner. */
export class UnauthorizedError extends Error {}

/** Turns a non-OK fetch Response into a thrown Error with a useful
 * message, pulled from the backend's own `{"detail": ...}` shape when
 * possible (Module 05's error shape) -- unchanged from Module 06's
 * questsApi.ts. */
async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") {
      return body.detail;
    }
    if (Array.isArray(body?.detail)) {
      // FastAPI's automatic 422 validation-error shape -- detail is a
      // list of {type, loc, msg, input} objects.
      return body.detail.map((item: { msg?: string }) => item.msg).join("; ");
    }
  } catch {
    // Body wasn't JSON at all -- fall through to the generic message below.
  }
  return `Request failed with status ${response.status}.`;
}

/** The one function every JSON request in this app funnels through.
 * Automatically attaches `Authorization: Bearer <token>` whenever a
 * token is stored -- this is the **entire** mechanism by which this
 * frontend proves who it is to the backend on every request after
 * login; there is no other code anywhere in this app that adds that
 * header. See lessons/06-building-signup-login.md's "the frontend's half
 * of the contract" section. */
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getStoredToken();

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init?.headers,
      },
    });
  } catch {
    // The fetch() call itself failed -- almost always the backend isn't
    // running, or CORS blocked it (see lessons/10-cors-in-depth.md).
    throw new Error(
      "Could not reach the QuestLog API. Is the FastAPI backend running on " +
        `${API_BASE_URL}? See backend/README.md.`,
    );
  }

  if (response.status === 401) {
    // Whatever token we sent (or didn't) wasn't accepted -- clear it so
    // this frontend never keeps retrying with a token the backend has
    // already rejected, then let the caller decide what "not
    // authenticated" should do on screen.
    clearStoredToken();
    throw new UnauthorizedError(await parseErrorMessage(response));
  }

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  if (response.status === 204) {
    // DELETE returns 204 No Content -- no body to parse at all.
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/** Used for exactly one endpoint in this app: `POST /api/auth/login` (see
 * src/api/authApi.ts). That route's body must be
 * `application/x-www-form-urlencoded`, not JSON -- FastAPI's
 * `OAuth2PasswordRequestForm` (backend/app/routers/auth.py) only knows
 * how to read form fields, per the OAuth2 spec's own convention -- so
 * this is a deliberately separate function from `request()` above rather
 * than one function branching on content type. */
export async function requestForm<T>(path: string, form: URLSearchParams): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
  } catch {
    throw new Error(
      "Could not reach the QuestLog API. Is the FastAPI backend running on " +
        `${API_BASE_URL}? See backend/README.md.`,
    );
  }

  if (!response.ok) {
    throw new Error(await parseErrorMessage(response));
  }

  return response.json() as Promise<T>;
}
