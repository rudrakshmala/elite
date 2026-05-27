import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Briefcase, ScrollText, FlaskConical, Settings, Bot } from 'lucide-react';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/portfolio', icon: Briefcase, label: 'Portfolio' },
  { to: '/orders', icon: ScrollText, label: 'Orders' },
  { to: '/backtest', icon: FlaskConical, label: 'Backtest' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  const { data: status } = usePolling(() => api.getBotStatus(), 3000);

  const botRunning = status?.running;
  const botMode = status?.mode;

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">E</div>
        <div className="logo-text">
          <span>Elite-Bot</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Navigation</div>
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end={to === '/'}
          >
            <Icon className="nav-icon" size={18} />
            {label}
          </NavLink>
        ))}

        <div className="sidebar-section-label">Quick Info</div>
        <div className="nav-item" style={{ cursor: 'default', opacity: 0.8 }}>
          <Bot size={18} className="nav-icon" />
          <span style={{ fontSize: '12px' }}>
            {botRunning ? `${botMode?.toUpperCase()} Running` : 'Bot Idle'}
          </span>
        </div>
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className={`status-dot ${botRunning ? 'running' : 'online'}`} />
          <span>
            {botRunning
              ? `🟢 ${botMode?.charAt(0).toUpperCase() + botMode?.slice(1)} Active`
              : '⚪ System Ready'}
          </span>
        </div>
      </div>
    </aside>
  );
}
