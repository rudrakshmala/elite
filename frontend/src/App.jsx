import { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import LoginPage from './pages/LoginPage';
import ApiKeySetup from './components/Settings/ApiKeySetup';
import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import OrdersPage from './pages/OrdersPage';
import BacktestPage from './pages/BacktestPage';
import SettingsPage from './pages/SettingsPage';
import api from './api/client';

export default function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [showKeySetup, setShowKeySetup] = useState(false);
  const [configChecked, setConfigChecked] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const location = useLocation();

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('elite_token');
    const isAuth = localStorage.getItem('authenticated');
    
    if (token && isAuth) {
      setAuthenticated(true);
    }
    
    setAuthChecked(true);
  }, []);

  // Check if API keys are configured (only if authenticated)
  useEffect(() => {
    if (!authenticated) {
      setConfigChecked(true);
      return;
    }

    api.getConfig()
      .then(cfg => {
        if (!cfg.configured) {
          setShowKeySetup(true);
        }
        setConfigChecked(true);
      })
      .catch(() => setConfigChecked(true));
  }, [authenticated]);

  const handleLogout = () => {
    localStorage.removeItem('elite_token');
    localStorage.removeItem('authenticated');
    setAuthenticated(false);
  };

  if (!authChecked) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
        <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Loading...</span>
      </div>
    );
  }

  // Redirect authenticated users away from login page
  if (authenticated && location.pathname === '/login') {
    return <Navigate to="/" replace />;
  }

  if (!authenticated) {
    return <LoginPage />;
  }

  if (!configChecked) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--bg-primary)',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
        <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Connecting to Elite-Bot...</span>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="main-area">
        <Header onOpenSettings={() => setShowKeySetup(true)} onLogout={handleLogout} />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>

      {showKeySetup && (
        <ApiKeySetup
          onClose={() => setShowKeySetup(false)}
          onSuccess={() => setShowKeySetup(false)}
        />
      )}
    </div>
  );
}
