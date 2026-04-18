import { useState } from 'react';
import { Play, Square, Zap, Bot, Crosshair, Brain, Cpu } from 'lucide-react';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

const BOT_MODES = [
  { id: 'elite', label: 'Elite Trader', icon: Zap, desc: 'CrewAI multi-agent stock pairs' },
  { id: 'crypto', label: 'Crypto Bot', icon: Bot, desc: 'RL crypto pair trading' },
  { id: 'sniper', label: 'Sniper', icon: Crosshair, desc: '$100/day quick profit' },
  { id: 'autopilot', label: 'Autopilot', icon: Cpu, desc: 'Full autonomous scanning' },
  { id: 'rl', label: 'RL Agent', icon: Brain, desc: 'Reinforcement Learning + CrewAI' },
];

export default function BotPanel({ market, onMarketChange }) {
  const [selectedMode, setSelectedMode] = useState('elite');
  const [starting, setStarting] = useState(false);
  const { data: status, refetch } = usePolling(() => api.getBotStatus(), 3000);

  const isRunning = status?.running;
  const activeMode = status?.mode;

  async function handleStart() {
    setStarting(true);
    try {
      await api.startBot(selectedMode);
      setTimeout(refetch, 500);
    } catch (err) {
      alert('Failed to start bot: ' + err.message);
    }
    setStarting(false);
  }

  async function handleStop() {
    try {
      await api.stopBot();
      setTimeout(refetch, 500);
    } catch (err) {
      alert('Failed to stop: ' + err.message);
    }
  }

  return (
    <div className="bot-panel">
      <div className="card-header">
        <span className="card-title">Bot Control</span>
        {isRunning && (
          <span style={{
            fontSize: '11px', fontWeight: 600,
            color: 'var(--accent-bull)', display: 'flex', alignItems: 'center', gap: '6px'
          }}>
            <span className="status-dot running" />
            {activeMode?.toUpperCase()} RUNNING
          </span>
        )}
      </div>

      {/* Market Tabs */}
      <div className="market-tabs">
        <button
          className={`market-tab ${market === 'stocks' ? 'active' : ''}`}
          onClick={() => onMarketChange('stocks')}
        >
          📈 Stocks
        </button>
        <button
          className={`market-tab ${market === 'crypto' ? 'active' : ''}`}
          onClick={() => onMarketChange('crypto')}
        >
          🪙 Crypto
        </button>
      </div>

      {/* Mode Selector */}
      <div className="mode-selector">
        {BOT_MODES.map(m => (
          <button
            key={m.id}
            className={`mode-btn ${selectedMode === m.id ? 'active' : ''}`}
            onClick={() => setSelectedMode(m.id)}
            disabled={isRunning}
            title={m.desc}
          >
            <m.icon size={13} style={{ marginRight: 4 }} />
            {m.label}
          </button>
        ))}
      </div>

      {/* Controls */}
      <div className="control-btns">
        {!isRunning ? (
          <button
            className="btn btn-success"
            onClick={handleStart}
            disabled={starting}
            style={{ flex: 1, justifyContent: 'center' }}
            id="btn-start-bot"
          >
            <Play size={16} />
            {starting ? 'Starting...' : `Start ${BOT_MODES.find(m => m.id === selectedMode)?.label}`}
          </button>
        ) : (
          <button
            className="btn btn-danger"
            onClick={handleStop}
            style={{ flex: 1, justifyContent: 'center' }}
            id="btn-stop-bot"
          >
            <Square size={16} />
            Stop Bot
          </button>
        )}
      </div>

      {/* Live PnL */}
      {isRunning && status?.live_pnl !== undefined && (
        <div style={{
          marginTop: '12px', padding: '10px 14px',
          background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center'
        }}>
          <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 600 }}>LIVE P&L</span>
          <span style={{
            fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '16px',
            color: status.live_pnl >= 0 ? 'var(--accent-bull)' : 'var(--accent-bear)'
          }}>
            {status.live_pnl >= 0 ? '+' : ''}${status.live_pnl.toFixed(2)}
          </span>
        </div>
      )}
    </div>
  );
}
