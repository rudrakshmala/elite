import { Settings, KeyRound, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

export default function Header({ onOpenSettings, onLogout }) {
  const { data: account } = usePolling(() => api.getAccount().catch(() => null), 5000);
  const { data: config } = usePolling(() => api.getConfig(), 10000);
  const navigate = useNavigate();

  const equity = account?.equity || 0;
  const lastEquity = account?.last_equity || equity;
  const dayChange = equity - lastEquity;
  const dayChangePct = lastEquity > 0 ? ((dayChange / lastEquity) * 100) : 0;

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="header-title">AI Trading Terminal</h1>
      </div>

      <div className="header-right">
        {config?.configured ? (
          <>
            <div className="header-stat">
              <span className="label">Equity</span>
              <span className="value">${equity.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="header-stat">
              <span className="label">Day P&L</span>
              <span className={`value ${dayChange >= 0 ? 'positive' : 'negative'}`}>
                {dayChange >= 0 ? '+' : ''}${dayChange.toFixed(2)} ({dayChangePct.toFixed(2)}%)
              </span>
            </div>
            {config?.paper && <span className="paper-badge">📄 Paper</span>}
          </>
        ) : (
          <button className="btn btn-primary" onClick={onOpenSettings} style={{ fontSize: '12px', padding: '6px 14px' }}>
            <KeyRound size={14} />
            Connect Alpaca
          </button>
        )}

        <button className="settings-btn" onClick={onOpenSettings} title="Settings">
          <Settings size={16} />
        </button>

        <button className="logout-btn" onClick={handleLogout} title="Logout" style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-secondary)',
          transition: 'color 0.2s'
        }}>
          <LogOut size={16} />
        </button>
      </div>
    </header>
  );
}
