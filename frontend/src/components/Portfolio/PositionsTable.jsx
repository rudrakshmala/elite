import { Package } from 'lucide-react';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

export default function PositionsTable() {
  const { data, loading } = usePolling(() => api.getPositions().catch(() => ({ positions: [] })), 4000);

  const positions = data?.positions || [];

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Open Positions</span>
        {positions.length > 0 && (
          <button
            className="btn btn-danger"
            style={{ padding: '4px 10px', fontSize: '11px' }}
            onClick={() => {
              if (confirm('Close ALL positions? This cannot be undone.')) {
                api.closeAllPositions();
              }
            }}
            id="btn-close-all"
          >
            Close All
          </button>
        )}
      </div>

      {positions.length === 0 ? (
        <div className="empty-state" style={{ padding: '30px' }}>
          <Package size={32} />
          <p>No open positions</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Side</th>
                <th>Qty</th>
                <th>Avg Entry</th>
                <th>Current</th>
                <th>P&L</th>
                <th>P&L %</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{p.symbol}</td>
                  <td>
                    <span className={`signal-badge ${p.side === 'long' ? 'buy' : 'sell'}`}>
                      {p.side?.toUpperCase()}
                    </span>
                  </td>
                  <td>{p.qty}</td>
                  <td>${p.avg_entry_price?.toFixed(2)}</td>
                  <td>${p.current_price?.toFixed(2)}</td>
                  <td className={p.unrealized_pl >= 0 ? 'positive' : 'negative'}>
                    {p.unrealized_pl >= 0 ? '+' : ''}${p.unrealized_pl?.toFixed(2)}
                  </td>
                  <td className={p.unrealized_plpc >= 0 ? 'positive' : 'negative'}>
                    {(p.unrealized_plpc * 100)?.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
