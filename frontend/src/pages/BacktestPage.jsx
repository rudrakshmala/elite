import { useState } from 'react';
import { FlaskConical, TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import api from '../api/client';

export default function BacktestPage() {
  const [symbolA, setSymbolA] = useState('MSFT');
  const [symbolB, setSymbolB] = useState('AAPL');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  async function runBacktest() {
    setLoading(true);
    setResults(null);
    try {
      const data = await api.runBacktest(symbolA, symbolB);
      setResults(data);
    } catch (err) {
      alert('Backtest failed: ' + err.message);
    }
    setLoading(false);
  }

  useEffect(() => {
    if (!results?.equity_curve?.length || !chartRef.current) return;

    if (chartInstanceRef.current) {
      chartInstanceRef.current.remove();
    }

    const chart = createChart(chartRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#161b25' },
        textColor: '#8a8f9c',
        fontFamily: "'Inter', sans-serif",
        fontSize: 10,
      },
      grid: { vertLines: { color: '#1e2433' }, horzLines: { color: '#1e2433' } },
      rightPriceScale: { borderColor: '#2a3345' },
      timeScale: { borderColor: '#2a3345' },
      width: chartRef.current.clientWidth,
      height: 300,
    });

    chartInstanceRef.current = chart;

    const series = chart.addAreaSeries({
      topColor: results.final_balance >= 10000
        ? 'rgba(38, 166, 154, 0.35)' : 'rgba(239, 83, 80, 0.35)',
      bottomColor: results.final_balance >= 10000
        ? 'rgba(38, 166, 154, 0.02)' : 'rgba(239, 83, 80, 0.02)',
      lineColor: results.final_balance >= 10000 ? '#26a69a' : '#ef5350',
      lineWidth: 2,
    });

    const data = results.equity_curve.map((p, i) => ({ time: p.date, value: p.equity }));
    series.setData(data);
    chart.timeScale().fitContent();

    return () => chart.remove();
  }, [results]);

  const pairs = [
    ['MSFT', 'AAPL'], ['KO', 'PEP'], ['XOM', 'CVX'], ['JPM', 'BAC'],
    ['F', 'GM'], ['V', 'MA'], ['LMT', 'RTX'], ['GOOGL', 'META'],
    ['BTC-USD', 'ETH-USD'],
  ];

  return (
    <div className="page-content">
      <div className="card">
        <div className="card-header">
          <span className="card-title">
            <FlaskConical size={14} style={{ marginRight: 6 }} />
            Backtester
          </span>
        </div>

        <div className="backtest-form" style={{ marginTop: '8px' }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label style={{ fontSize: '10px' }}>Pair</label>
            <select
              value={`${symbolA}|${symbolB}`}
              onChange={(e) => {
                const [a, b] = e.target.value.split('|');
                setSymbolA(a);
                setSymbolB(b);
              }}
            >
              {pairs.map(([a, b]) => (
                <option key={`${a}|${b}`} value={`${a}|${b}`}>{a} / {b}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={runBacktest} disabled={loading}>
            {loading ? (
              <><span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} /> Running...</>
            ) : (
              <><FlaskConical size={14} /> Run Backtest</>
            )}
          </button>
        </div>
      </div>

      {results && (
        <>
          {/* Results Summary */}
          <div className="stat-cards">
            <div className="stat-card">
              <div className="stat-icon blue"><BarChart3 size={18} /></div>
              <div className="stat-label">Final Balance</div>
              <div className={`stat-value ${results.final_balance >= 10000 ? 'positive' : 'negative'}`}>
                ${results.final_balance?.toLocaleString()}
              </div>
            </div>
            <div className="stat-card">
              <div className={`stat-icon ${results.total_return_pct >= 0 ? 'green' : 'red'}`}>
                {results.total_return_pct >= 0 ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
              </div>
              <div className="stat-label">Total Return</div>
              <div className={`stat-value ${results.total_return_pct >= 0 ? 'positive' : 'negative'}`}>
                {results.total_return_pct >= 0 ? '+' : ''}{results.total_return_pct}%
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon purple"><FlaskConical size={18} /></div>
              <div className="stat-label">Total Trades</div>
              <div className="stat-value">{results.total_trades}</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon green"><TrendingUp size={18} /></div>
              <div className="stat-label">Win Rate</div>
              <div className="stat-value">{results.win_rate}%</div>
              <div className="stat-change" style={{ color: 'var(--text-secondary)' }}>
                {results.wins}W / {results.losses}L
              </div>
            </div>
          </div>

          {/* Equity Curve */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Backtest Equity Curve — {symbolA} / {symbolB}</span>
            </div>
            <div ref={chartRef} style={{ height: 300 }} />
          </div>

          {/* Recent Trades */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Recent Trades</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Result</th>
                    <th>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {results.trades?.map((t, i) => (
                    <tr key={i}>
                      <td>{t.date}</td>
                      <td>
                        <span className={`signal-badge ${t.result === 'WIN' ? 'buy' : 'sell'}`}>
                          {t.result}
                        </span>
                      </td>
                      <td className={t.pnl >= 0 ? 'positive' : 'negative'}>
                        {t.pnl >= 0 ? '+' : ''}${t.pnl?.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
