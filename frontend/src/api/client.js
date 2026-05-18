const API_BASE = import.meta.env.VITE_API_URL || '';

const api = {
  getToken: () => localStorage.getItem('elite_token'),
  
  getHeaders: () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${api.getToken()}`
  }),

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...api.getHeaders(),
        ...options.headers
      }
    });

    if (response.status === 401) {
      localStorage.removeItem('elite_token');
      localStorage.removeItem('authenticated');
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  },

  // Auth
  login: (password) => api.request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ password })
  }),

  logout: () => {
    localStorage.removeItem('elite_token');
    localStorage.removeItem('authenticated');
  },

  // Config
  getConfig: () => api.request('/api/config'),
  setConfig: (payload) => api.request('/api/config', {
    method: 'POST',
    body: JSON.stringify(payload)
  }),
  validateConfig: () => api.request('/api/config/validate', { method: 'POST' }),

  // Account
  getAccount: () => api.request('/api/account'),
  getPortfolioHistory: (period = '1M', timeframe = '1D') =>
    api.request(`/api/account/portfolio-history?period=${period}&timeframe=${timeframe}`),

  // Positions
  getPositions: () => api.request('/api/positions'),
  closeAllPositions: () => api.request('/api/positions/close-all', { method: 'POST' }),

  // Orders
  getOrders: (status = 'all', limit = 50) =>
    api.request(`/api/orders?status=${status}&limit=${limit}`),

  // Market Data
  getChartData: (symbol, period = '5d', interval = '1h') =>
    api.request(`/api/market/chart/${symbol}?period=${period}&interval=${interval}`),
  getQuote: (symbol) => api.request(`/api/market/quote/${symbol}`),
  getMarketPairs: () => api.request('/api/market/pairs'),
  scanMarket: (market = 'stocks') => api.request(`/api/market/scan?market=${market}`),

  // Bot Control
  startBot: (mode) => api.request(`/api/bot/start/${mode}`, { method: 'POST' }),
  stopBot: () => api.request('/api/bot/stop', { method: 'POST' }),
  getBotStatus: () => api.request('/api/bot/status'),
  getBotLogs: (last = 50) => api.request(`/api/bot/logs?last=${last}`),

  // Backtest
  runBacktest: (symbol_a, symbol_b) => api.request('/api/backtest', {
    method: 'POST',
    body: JSON.stringify({ symbol_a, symbol_b })
  })
};

export default api;
