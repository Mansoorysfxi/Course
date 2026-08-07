import { useAnnouncements } from "../hooks/useAnnouncements";

export function AnnouncementBoard() {
  const { announcements, loading, error, refetch } = useAnnouncements();

  if (loading) {
    return <p className="muted">Loading announcements...</p>;
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
      {announcements.map((announcement) => (
        <li key={announcement.id} className="card">
          {announcement.message}
        </li>
      ))}
    </ul>
  );
}
