import { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import ApiKeySetup from './components/Settings/ApiKeySetup';
import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import OrdersPage from './pages/OrdersPage';
import BacktestPage from './pages/BacktestPage';
import SettingsPage from './pages/SettingsPage';
import api from './api/client';

export default function App() {
  const [showKeySetup, setShowKeySetup] = useState(false);
  const [configChecked, setConfigChecked] = useState(false);

  useEffect(() => {
    // Check if keys are configured on first load
    api.getConfig()
      .then(async cfg => {
        if (!cfg.configured) {
          const localApiKey = localStorage.getItem('alpaca_api_key');
          const localSecretKey = localStorage.getItem('alpaca_secret_key');
          const localPaper = localStorage.getItem('alpaca_paper') !== 'false';
          const localGroqKey = localStorage.getItem('groq_api_key') || '';
          
          if (localApiKey && localSecretKey) {
            try {
              await api.setConfig({
                api_key: localApiKey,
                secret_key: localSecretKey,
                paper: localPaper,
                groq_key: localGroqKey
              });
              const val = await api.validateConfig();
              if (val.valid) {
                setConfigChecked(true);
                return;
              }
            } catch (e) {
              console.error("Auto-sync keys failed:", e);
            }
          }
          setShowKeySetup(true);
        }
        setConfigChecked(true);
      })
      .catch(() => setConfigChecked(true));
  }, []);

  if (!configChecked) {
    return (
      <div style={{
        height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'var(--bg-primary)', flexDirection: 'column', gap: '16px'
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
        <Header onOpenSettings={() => setShowKeySetup(true)} />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
          <Route path="/settings" element={<SettingsPage />} />
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
