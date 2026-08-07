import { Link, NavLink, Outlet, useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";

const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? "bg-indigo-600 text-white" : "text-slate-600 hover:bg-slate-100"
  }`;

/** The shared page shell -- header/nav plus wherever the current route's
 * page renders. `<Outlet />` is React Router's placeholder for "whichever
 * child route matched" -- see lessons/08-react-router.md (Module 04).
 * New in Module 07: the signed-in user's email and a "Log out" button,
 * read from `useAuth()` (src/context/AuthContext.tsx). */
export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-lg font-bold text-slate-900">
            🗒️ QuestLog
          </Link>
          <nav className="flex items-center gap-1">
            <NavLink to="/" className={navLinkClasses} end>
              Quest Board
            </NavLink>
            <NavLink to="/quests/new" className={navLinkClasses}>
              New Quest
            </NavLink>
            {user && (
              <div className="ml-4 flex items-center gap-3 border-l border-slate-200 pl-4">
                <span className="text-sm text-slate-500">{user.email}</span>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-md px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
                >
                  Log out
                </button>
              </div>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
