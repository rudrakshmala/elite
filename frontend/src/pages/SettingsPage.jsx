import { useState, useEffect } from 'react';
import { KeyRound, Shield, Sliders, Info } from 'lucide-react';
import api from '../api/client';

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('');
  const [secretKey, setSecretKey] = useState('');
  const [paper, setPaper] = useState(true);
  const [config, setConfig] = useState(null);
  const [validation, setValidation] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getConfig().then(setConfig).catch(() => {});
  }, []);

  async function handleSave() {
    setSaving(true);
    setValidation(null);
    try {
      await api.setConfig({ api_key: apiKey, secret_key: secretKey, paper });
      const res = await api.validateConfig();
      if (res.valid) {
        setValidation({ success: true, msg: `Connected! Portfolio: $${res.portfolio_value?.toLocaleString()}` });
        api.getConfig().then(setConfig);
        setApiKey('');
        setSecretKey('');
      } else {
        setValidation({ success: false, msg: res.error || 'Invalid keys' });
      }
    } catch (err) {
      setValidation({ success: false, msg: err.message });
    }
    setSaving(false);
  }

  return (
    <div className="page-content" style={{ maxWidth: '700px' }}>
      {/* Connection Status */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><Shield size={13} style={{ marginRight: 6 }} /> Connection Status</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0' }}>
          <span className={`status-dot ${config?.configured ? 'online' : 'offline'}`} style={{ width: 12, height: 12 }} />
          <div>
            <div style={{ fontWeight: 600 }}>{config?.configured ? 'Connected to Alpaca' : 'Not Connected'}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {config?.configured ? `Key: ${config.api_key_masked} | ${config.paper ? 'Paper' : 'LIVE'}` : 'Enter your API keys below'}
            </div>
          </div>
        </div>
      </div>

      {/* API Key Configuration */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><KeyRound size={13} style={{ marginRight: 6 }} /> Alpaca API Keys</span>
        </div>

        <div style={{ padding: '8px 0' }}>
          <div style={{
            padding: '10px 14px', borderRadius: 'var(--radius-md)', marginBottom: '16px',
            background: 'var(--accent-blue-dim)', fontSize: '12px', color: 'var(--accent-blue)',
            display: 'flex', alignItems: 'center', gap: '8px'
          }}>
            <Info size={14} />
            Keys are stored in server memory only — never written to disk or logs.
          </div>

          <div className="form-group">
            <label>API Key ID</label>
            <input
              type="text"
              placeholder="PK..."
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              autoComplete="off"
            />
          </div>

          <div className="form-group">
            <label>Secret Key</label>
            <input
              type="password"
              placeholder="Your secret key..."
              value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              autoComplete="off"
            />
          </div>

          <div className="toggle-row">
            <div>
              <label style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)' }}>Paper Trading Mode</label>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Use fake money for testing</div>
            </div>
            <div className="toggle-switch">
              <input type="checkbox" checked={paper} onChange={(e) => setPaper(e.target.checked)} />
              <span className="toggle-slider" onClick={() => setPaper(!paper)} />
            </div>
          </div>

          {!paper && (
            <div className="validation-result error" style={{ margin: '8px 0' }}>
              ⚠️ LIVE MODE — You will be trading with real money!
            </div>
          )}

          {validation && (
            <div className={`validation-result ${validation.success ? 'success' : 'error'}`}>
              {validation.success ? '✅' : '❌'} {validation.msg}
            </div>
          )}

          <button
            className="btn btn-primary"
            onClick={handleSave}
            disabled={!apiKey || !secretKey || saving}
            style={{ marginTop: '12px', width: '100%', justifyContent: 'center' }}
          >
            {saving ? 'Validating...' : 'Save & Validate Keys'}
          </button>
        </div>
      </div>

      {/* Risk Config Info */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><Sliders size={13} style={{ marginRight: 6 }} /> Risk Configuration</span>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
          <table className="data-table">
            <tbody>
              <tr>
                <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-primary)' }}>Hard Stop Loss</td>
                <td className="negative">-$100.00</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-primary)' }}>Soft Stop Loss</td>
                <td className="negative">-$75.00</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-primary)' }}>Daily Profit Target</td>
                <td className="positive">+$1,000.00</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-primary)' }}>Max Sector Exposure</td>
                <td>25%</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-primary)' }}>Fee Per Side</td>
                <td>0.1%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
