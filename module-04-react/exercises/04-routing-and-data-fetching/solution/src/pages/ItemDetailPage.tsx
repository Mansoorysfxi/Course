import { Link, useParams } from "react-router";
import { useItems } from "../hooks/useItems";

export function ItemDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { items, loading, error, refetch } = useItems();

  if (loading) {
    return <p className="muted">Loading item...</p>;
  }

  if (error) {
    return (
      <div className="error">
        <p>{error}</p>
        <button className="btn" onClick={refetch}>
          Try again
        </button>
      </div>
    );
  }

  const item = items.find((i) => i.id === id);

  if (!item) {
    return (
      <div>
        <p>Item not found.</p>
        <Link to="/">Back to catalog</Link>
      </div>
    );
  }

  return (
    <div className="card">
      <h2>{item.name}</h2>
      <p>{item.price} gold</p>
      <p className="muted">{item.description}</p>
      <Link to="/">Back to catalog</Link>
    </div>
  );
}
