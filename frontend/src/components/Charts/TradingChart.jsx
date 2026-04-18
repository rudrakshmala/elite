import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import api from '../../api/client';

const TIMEFRAMES = [
  { label: '1m', period: '1d', interval: '1m' },
  { label: '5m', period: '5d', interval: '5m' },
  { label: '1H', period: '5d', interval: '1h' },
  { label: '1D', period: '6mo', interval: '1d' },
  { label: '1W', period: '2y', interval: '1wk' },
];

const SYMBOLS = [
  'AAPL', 'MSFT', 'GOOGL', 'META', 'TSLA', 'NVDA', 'AMD', 'JPM', 'BAC',
  'KO', 'PEP', 'XOM', 'CVX', 'F', 'GM', 'V', 'MA', 'LMT', 'RTX',
  'BTC-USD', 'ETH-USD', 'SOL-USD', 'DOGE-USD',
];

export default function TradingChart() {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const volumeRef = useRef(null);
  const [symbol, setSymbol] = useState('AAPL');
  const [tfIdx, setTfIdx] = useState(2);
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);

  // Create chart instance
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0f1118' },
        textColor: '#8a8f9c',
        fontFamily: "'Inter', sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#1e2433' },
        horzLines: { color: '#1e2433' },
      },
      crosshair: {
        mode: 0,
        vertLine: { color: '#2962ff', width: 1, style: 2 },
        horzLine: { color: '#2962ff', width: 1, style: 2 },
      },
      rightPriceScale: {
        borderColor: '#2a3345',
        scaleMargins: { top: 0.1, bottom: 0.2 },
      },
      timeScale: {
        borderColor: '#2a3345',
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: true,
      handleScale: true,
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });

    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    chartRef.current = chart;
    seriesRef.current = candleSeries;
    volumeRef.current = volumeSeries;

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Fetch data when symbol or timeframe changes
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const tf = TIMEFRAMES[tfIdx];
        const [chartData, quoteData] = await Promise.all([
          api.getChartData(symbol, tf.period, tf.interval),
          api.getQuote(symbol),
        ]);
        setQuote(quoteData);

        if (seriesRef.current && chartData?.candles?.length) {
          const candles = chartData.candles
            .filter(c => c.time > 0)
            .sort((a, b) => a.time - b.time);

          seriesRef.current.setData(candles);
          volumeRef.current?.setData(
            candles.map(c => ({
              time: c.time,
              value: c.volume,
              color: c.close >= c.open ? 'rgba(38,166,154,0.3)' : 'rgba(239,83,80,0.3)',
            }))
          );

          chartRef.current?.timeScale().fitContent();
        }
      } catch (err) {
        console.error('Chart data error:', err);
      }
      setLoading(false);
    }
    fetchData();
  }, [symbol, tfIdx]);

  return (
    <div className="chart-container">
      <div className="chart-toolbar">
        <div className="chart-symbol-select">
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)} id="symbol-select">
            {SYMBOLS.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          {quote && (
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '14px' }}>
              ${quote.price?.toFixed(2)}
              <span
                style={{
                  marginLeft: '8px',
                  fontSize: '12px',
                  color: quote.change >= 0 ? 'var(--accent-bull)' : 'var(--accent-bear)',
                }}
              >
                {quote.change >= 0 ? '+' : ''}{quote.change?.toFixed(2)} ({quote.change_pct?.toFixed(2)}%)
              </span>
            </span>
          )}
          {loading && <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />}
        </div>

        <div className="timeframe-btns">
          {TIMEFRAMES.map((tf, i) => (
            <button
              key={tf.label}
              className={`tf-btn ${i === tfIdx ? 'active' : ''}`}
              onClick={() => setTfIdx(i)}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>
      <div className="chart-body" ref={chartContainerRef} />
    </div>
  );
}
