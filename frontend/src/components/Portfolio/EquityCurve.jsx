import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import api from '../../api/client';

export default function EquityCurve() {
  const containerRef = useRef(null);
  const [period, setPeriod] = useState('1M');

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#161b25' },
        textColor: '#8a8f9c',
        fontFamily: "'Inter', sans-serif",
        fontSize: 10,
      },
      grid: {
        vertLines: { color: '#1e2433' },
        horzLines: { color: '#1e2433' },
      },
      rightPriceScale: { borderColor: '#2a3345' },
      timeScale: { borderColor: '#2a3345' },
      handleScroll: true,
      handleScale: true,
      width: containerRef.current.clientWidth,
      height: 220,
    });

    const areaSeries = chart.addAreaSeries({
      topColor: 'rgba(41, 98, 255, 0.35)',
      bottomColor: 'rgba(41, 98, 255, 0.02)',
      lineColor: '#2962ff',
      lineWidth: 2,
    });

    async function loadData() {
      try {
        const data = await api.getPortfolioHistory(period, period === '1D' ? '5Min' : '1D');
        if (data?.timestamps?.length) {
          const points = data.timestamps.map((t, i) => ({
            time: t,
            value: data.equity[i],
          }));
          areaSeries.setData(points);
          chart.timeScale().fitContent();
        }
      } catch (err) {
        console.error('Equity curve error:', err);
      }
    }

    loadData();

    const handleResize = () => {
      chart.applyOptions({ width: containerRef.current.clientWidth });
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [period]);

  return (
    <div className="card">
      <div className="card-header">
        <span className="card-title">Equity Curve</span>
        <div className="timeframe-btns">
          {['1D', '1W', '1M', '3M', '1A'].map(p => (
            <button
              key={p}
              className={`tf-btn ${p === period ? 'active' : ''}`}
              onClick={() => setPeriod(p)}
            >
              {p}
            </button>
          ))}
        </div>
      </div>
      <div className="equity-chart-container" ref={containerRef} />
    </div>
  );
}
