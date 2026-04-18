import { useState, useEffect } from 'react';
import { ScrollText } from 'lucide-react';
import api from '../../api/client';

export default function OrderHistory() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await api.getOrders(filter, 100);
        setOrders(data.orders || []);
      } catch (err) {
        console.error(err);
      }
      setLoading(false);
    }
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [filter]);

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Order History</span>
        <div className="timeframe-btns">
          {['all', 'open', 'closed'].map(f => (
            <button
              key={f}
              className={`tf-btn ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loader"><div className="spinner" /></div>
      ) : orders.length === 0 ? (
        <div className="empty-state" style={{ padding: '30px' }}>
          <ScrollText size={32} />
          <p>No orders found</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto', maxHeight: '500px', overflowY: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Side</th>
                <th>Qty</th>
                <th>Type</th>
                <th>Status</th>
                <th>Filled Price</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{o.symbol}</td>
                  <td>
                    <span className={`signal-badge ${o.side === 'buy' ? 'buy' : 'sell'}`}>
                      {o.side?.toUpperCase()}
                    </span>
                  </td>
                  <td>{o.filled_qty || o.qty}</td>
                  <td style={{ textTransform: 'uppercase', fontSize: '11px' }}>{o.type}</td>
                  <td>
                    <span style={{
                      fontSize: '11px', fontWeight: 600,
                      color: o.status === 'filled' ? 'var(--accent-bull)' :
                        o.status === 'canceled' ? 'var(--accent-bear)' : 'var(--accent-gold)'
                    }}>
                      {o.status?.toUpperCase()}
                    </span>
                  </td>
                  <td>{o.filled_avg_price ? `$${parseFloat(o.filled_avg_price).toFixed(2)}` : '—'}</td>
                  <td style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    {o.submitted_at ? new Date(o.submitted_at).toLocaleString() : '—'}
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
