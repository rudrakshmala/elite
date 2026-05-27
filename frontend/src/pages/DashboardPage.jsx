import { useState } from 'react';
import { ErrorBoundary } from '../components/Common/ErrorBoundary';
import TradingChart from '../components/Charts/TradingChart';
import PortfolioSummary from '../components/Portfolio/PortfolioSummary';
import PositionsTable from '../components/Portfolio/PositionsTable';
import BotPanel from '../components/BotControl/BotPanel';
import AgentTerminal from '../components/BotControl/AgentTerminal';
import MarketScanner from '../components/BotControl/MarketScanner';

export default function DashboardPage() {
  const [market, setMarket] = useState('stocks');

  return (
    <div className="page-content">
      {/* Stat Cards */}
      <ErrorBoundary fallbackTitle="Portfolio data unavailable">
        <PortfolioSummary />
      </ErrorBoundary>

      {/* Chart */}
      <ErrorBoundary fallbackTitle="Chart failed to load">
        <TradingChart />
      </ErrorBoundary>

      {/* Bottom Grid: Bot Control + Scanner */}
      <div className="grid-2">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <ErrorBoundary fallbackTitle="Bot panel error">
            <BotPanel market={market} onMarketChange={setMarket} />
          </ErrorBoundary>
          <ErrorBoundary fallbackTitle="Positions table error">
            <PositionsTable />
          </ErrorBoundary>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <ErrorBoundary fallbackTitle="Scanner error">
            <MarketScanner market={market} />
          </ErrorBoundary>
          <ErrorBoundary fallbackTitle="Terminal error">
            <AgentTerminal />
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
}
