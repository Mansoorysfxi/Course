import { Link } from "react-router";

/** The catch-all route (`path="*"` in App.tsx) -- see lessons/08-react-router.md. */
export function NotFoundPage() {
  return (
    <div className="py-16 text-center">
      <h1 className="text-2xl font-bold text-slate-900">404 — Page Not Found</h1>
      <p className="mt-2 text-slate-500">There's no quest, or page, here.</p>
      <Link to="/" className="mt-4 inline-block text-indigo-600 hover:underline">
        Back to the Quest Board
      </Link>
    </div>
  );
}
