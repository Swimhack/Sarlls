import { useEffect, useState } from 'react';
import { fetchActivity } from '../api';

export function ActivityPage() {
  const [events, setEvents] = useState<Array<Record<string, string>>>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchActivity()
      .then(setEvents)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading activity...</div>;

  const filtered =
    filter === 'all'
      ? events
      : events.filter((e) => e.outcome === filter);

  const outcomes = [...new Set(events.map((e) => e.outcome))];

  return (
    <div>
      <h1 className="page-title">Activity History</h1>

      <div className="tab-bar">
        <button
          className="tab-btn"
          aria-selected={filter === 'all' ? 'true' : undefined}
          onClick={() => setFilter('all')}
        >
          All ({events.length})
        </button>
        {outcomes.map((o) => (
          <button
            key={o}
            className="tab-btn"
            aria-selected={filter === o ? 'true' : undefined}
            onClick={() => setFilter(o ?? 'all')}
          >
            {o} ({events.filter((e) => e.outcome === o).length})
          </button>
        ))}
      </div>

      <div className="card">
        {filtered.length === 0 ? (
          <p style={{ color: 'var(--muted)', fontSize: 13 }}>No activity yet.</p>
        ) : (
          filtered.map((event, i) => (
            <div key={i} className="activity-item">
              <span className="activity-time">
                {new Date(event.createdAt!).toLocaleString()}
              </span>
              <span style={{ flex: 1 }}>{event.summary}</span>
              <span
                className={`status-label ${event.outcome}`}
                style={{ fontSize: 11 }}
              >
                {event.outcome}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
