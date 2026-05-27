import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

export default function MarketScanner({ market }) {
  const { data, loading } = usePolling(() => api.scanMarket(market), 30000, [market]);

  const results = data?.results || [];

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">
          <Search size={13} style={{ marginRight: 6 }} />
          Pair Scanner — {market === 'crypto' ? '🪙 Crypto' : '📈 Stocks'}
        </span>
        {loading && <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />}
      </div>

      <div>
        {results.length === 0 ? (
          <div className="empty-state" style={{ padding: '20px' }}>
            <p>Click scan or wait for auto-refresh...</p>
          </div>
        ) : (
          results.map((r, i) => (
            <div className="scanner-row" key={i}>
              <div>
                <div className="scanner-pair">{r.pair}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  Z: {r.z !== null ? r.z.toFixed(3) : 'N/A'}
                </div>
              </div>
              <span className={`signal-badge ${r.signal === 'BUY' ? 'buy' : r.signal === 'SELL' ? 'sell' : 'hold'}`}>
                {r.signal}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
