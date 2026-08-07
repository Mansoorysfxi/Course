import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <div>
      <h2>404 — Page Not Found</h2>
      <Link to="/">Back to catalog</Link>
    </div>
  );
}
