import { useState } from 'react';
import { KeyRound, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react';
import api from '../../api/client';

export default function ApiKeySetup({ onClose, onSuccess }) {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('alpaca_api_key') || '');
  const [secretKey, setSecretKey] = useState(() => localStorage.getItem('alpaca_secret_key') || '');
  const [paper, setPaper] = useState(() => {
    const val = localStorage.getItem('alpaca_paper');
    return val === null ? true : val === 'true';
  });
  const [groqKey, setGroqKey] = useState(() => localStorage.getItem('groq_api_key') || '');
  const [showSecret, setShowSecret] = useState(false);
  const [validating, setValidating] = useState(false);
  const [result, setResult] = useState(null);

  async function handleSave() {
    setValidating(true);
    setResult(null);
    try {
      await api.setConfig({ api_key: apiKey, secret_key: secretKey, paper, groq_key: groqKey });
      const res = await api.validateConfig();
      if (res.valid) {
        localStorage.setItem('alpaca_api_key', apiKey);
        localStorage.setItem('alpaca_secret_key', secretKey);
        localStorage.setItem('alpaca_paper', String(paper));
        localStorage.setItem('groq_api_key', groqKey);
        setResult({
          success: true,
          msg: `✅ Connected! Portfolio: $${res.portfolio_value?.toLocaleString()} | Buying Power: $${res.buying_power?.toLocaleString()}`
        });
        setTimeout(() => {
          onSuccess?.();
          onClose?.();
        }, 1500);
      } else {
        setResult({ success: false, msg: `❌ ${res.error || 'Invalid keys'}` });
      }
    } catch (err) {
      setResult({ success: false, msg: `❌ ${err.message}` });
    }
    setValidating(false);
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose?.()}>
      <div className="modal">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
          <div style={{
            width: '42px', height: '42px', borderRadius: '12px',
            background: 'var(--accent-blue-dim)', display: 'flex',
            alignItems: 'center', justifyContent: 'center', color: 'var(--accent-blue)'
          }}>
            <KeyRound size={22} />
          </div>
          <div>
            <h2>Connect to Alpaca & Groq</h2>
          </div>
        </div>
        <p>Enter your API keys to start trading. Keys are saved securely in your browser's local storage and synced to the backend.</p>

        <div className="form-group">
          <label>Alpaca API Key ID</label>
          <input
            id="input-api-key"
            type="text"
            placeholder="PK..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            autoComplete="off"
          />
        </div>

        <div className="form-group">
          <label>Alpaca Secret Key</label>
          <div style={{ position: 'relative' }}>
            <input
              id="input-secret-key"
              type={showSecret ? 'text' : 'password'}
              placeholder="Your secret key..."
              value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              autoComplete="off"
            />
            <button
              type="button"
              onClick={() => setShowSecret(!showSecret)}
              style={{
                position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)',
                background: 'none', border: 'none', color: 'var(--text-tertiary)', cursor: 'pointer'
              }}
            >
              {showSecret ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Groq API Key (For AI Agents Validation - Optional)</label>
          <input
            id="input-groq-key"
            type={showSecret ? 'text' : 'password'}
            placeholder="gsk_... (Leave blank to use server environment key)"
            value={groqKey}
            onChange={(e) => setGroqKey(e.target.value)}
            autoComplete="off"
          />
        </div>

        <div className="toggle-row">
          <label>📄 Paper Trading Mode (Safe)</label>
          <div className="toggle-switch">
            <input
              id="toggle-paper"
              type="checkbox"
              checked={paper}
              onChange={(e) => setPaper(e.target.checked)}
            />
            <span className="toggle-slider" onClick={() => setPaper(!paper)} />
          </div>
        </div>

        {!paper && (
          <div className="validation-result error" style={{ marginTop: '8px', marginBottom: '8px' }}>
            ⚠️ LIVE TRADING — Real money will be at risk!
          </div>
        )}

        {result && (
          <div className={`validation-result ${result.success ? 'success' : 'error'}`}>
            {result.msg}
          </div>
        )}

        <div className="modal-btns">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={!apiKey || !secretKey || validating}
            id="btn-connect"
          >
            {validating ? (
              <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
            ) : (
              <CheckCircle size={16} />
            )}
            {validating ? 'Validating...' : 'Connect & Validate'}
          </button>
        </div>
      </div>
    </div>
  );
}
