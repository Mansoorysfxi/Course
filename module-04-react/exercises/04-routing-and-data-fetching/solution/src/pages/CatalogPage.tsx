import { Link } from "react-router";
import { useItems } from "../hooks/useItems";

export function CatalogPage() {
  const { items, loading, error, refetch } = useItems();

  if (loading) {
    return <p className="muted">Loading the catalog...</p>;
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

  return (
    <ul style={{ listStyle: "none", padding: 0 }}>
      {items.map((item) => (
        <li key={item.id} className="card">
          <Link to={`/items/${item.id}`}>
            {item.name} — {item.price} gold
          </Link>
        </li>
      ))}
    </ul>
  );
}
