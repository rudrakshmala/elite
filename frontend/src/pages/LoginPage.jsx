import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

export default function LoginPage() {
  const navigate = useNavigate();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.detail || 'Invalid password');
        setLoading(false);
        return;
      }

      const data = await response.json();
      localStorage.setItem('elite_token', data.token);
      localStorage.setItem('authenticated', 'true');
      
      setPassword('');
      navigate('/');
    } catch (err) {
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        {/* Logo */}
        <div className="login-logo">
          <div className="logo-icon">🦅</div>
          <h1>Elite-Bot</h1>
          <p>AI Trading Terminal</p>
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter app password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoFocus
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button
            type="submit"
            disabled={loading || !password}
            className="login-btn"
          >
            {loading ? 'Authenticating...' : 'Login'}
          </button>
        </form>

        {/* Footer */}
        <div className="login-footer">
          <p>Secure access to your trading dashboard</p>
        </div>
      </div>
    </div>
  );
}
