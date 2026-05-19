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

  // Check if API keys are configured on mount
  useEffect(() => {
    api.getConfig()
      .then(cfg => {
        if (!cfg.configured) {
          setShowKeySetup(true);
        }
      })
      .catch(() => {
        // Default: show settings if API check fails
        setShowKeySetup(true);
      });
  }, []);

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
          <Route path="*" element={<DashboardPage />} />
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