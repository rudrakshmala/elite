import { DollarSign, TrendingUp, Wallet, BarChart3, Activity } from 'lucide-react';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

export default function PortfolioSummary() {
  const { data: account, loading } = usePolling(() => api.getAccount().catch(() => null), 5000);
  const { data: positions } = usePolling(() => api.getPositions().catch(() => ({ total_pnl: 0, count: 0 })), 5000);

  if (loading || !account) {
    return (
      <div className="stat-cards">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="stat-card">
            <div className="skeleton" style={{ width: 80, height: 12, marginBottom: 8 }} />
            <div className="skeleton" style={{ width: 120, height: 28 }} />
          </div>
        ))}
      </div>
    );
  }

  const dayChange = account.equity - account.last_equity;
  const dayChangePct = account.last_equity > 0 ? (dayChange / account.last_equity * 100) : 0;

  const stats = [
    {
      label: 'Portfolio Value',
      value: `$${account.portfolio_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
      change: `${dayChange >= 0 ? '+' : ''}$${dayChange.toFixed(2)} (${dayChangePct.toFixed(2)}%)`,
      positive: dayChange >= 0,
      icon: DollarSign,
      color: 'blue',
    },
    {
      label: 'Buying Power',
      value: `$${account.buying_power?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
      icon: Wallet,
      color: 'green',
    },
    {
      label: 'Cash',
      value: `$${account.cash?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
      icon: BarChart3,
      color: 'purple',
    },
    {
      label: 'Open P&L',
      value: `${positions?.total_pnl >= 0 ? '+' : ''}$${positions?.total_pnl?.toFixed(2) || '0.00'}`,
      positive: (positions?.total_pnl || 0) >= 0,
      icon: TrendingUp,
      color: (positions?.total_pnl || 0) >= 0 ? 'green' : 'red',
    },
    {
      label: 'Positions',
      value: positions?.count || '0',
      icon: Activity,
      color: 'gold',
    },
  ];

  return (
    <div className="stat-cards">
      {stats.map((s, i) => (
        <div className="stat-card" key={i}>
          <div className={`stat-icon ${s.color}`}>
            <s.icon size={18} />
          </div>
          <div className="stat-label">{s.label}</div>
          <div className={`stat-value ${s.positive === true ? 'positive' : s.positive === false ? 'negative' : ''}`}>
            {s.value}
          </div>
          {s.change && (
            <div className={`stat-change ${s.positive ? 'positive' : 'negative'}`}>{s.change}</div>
          )}
        </div>
      ))}
    </div>
  );
}
