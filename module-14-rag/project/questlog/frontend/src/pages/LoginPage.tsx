import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";

/**
 * The login form. A controlled form exactly like src/components/
 * QuestForm.tsx (Module 04's pattern) -- two fields, both live in local
 * state, fed back into their `value` props. See
 * lessons/06-building-signup-login.md's "the frontend's half of the
 * contract" section for what `login()` (from useAuth(), see
 * src/context/AuthContext.tsx) actually does under the hood.
 */
export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setFormError(null);
    try {
      await login(email, password);
      // If ProtectedRoute redirected here from some other page (see
      // App.tsx / ProtectedRoute.tsx), react-router's `Navigate` attaches
      // the page you were headed to as `location.state.from` -- send you
      // back there instead of always landing on the Quest Board.
      const from = (location.state as { from?: string } | null)?.from ?? "/";
      navigate(from, { replace: true });
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Could not log in.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-1 text-center text-2xl font-bold text-slate-900">🗒️ QuestLog</h1>
        <p className="mb-6 text-center text-sm text-slate-500">Log in to see your quests.</p>

        {formError && (
          <p className="mb-4 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-800">
            {formError}
          </p>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60"
          >
            {submitting ? "Logging in..." : "Log in"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          No account yet?{" "}
          <Link to="/signup" className="text-indigo-600 hover:underline">
            Sign up
          </Link>
        </p>

        <p className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-center text-xs text-slate-400">
          Demo account: <code>player@questlog.local</code> / <code>dragon-slayer-1</code>
        </p>
      </div>
    </div>
  );
}
