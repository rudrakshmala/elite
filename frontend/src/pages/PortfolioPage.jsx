import { ErrorBoundary } from '../components/Common/ErrorBoundary';
import PortfolioSummary from '../components/Portfolio/PortfolioSummary';
import PositionsTable from '../components/Portfolio/PositionsTable';
import EquityCurve from '../components/Portfolio/EquityCurve';

export default function PortfolioPage() {
  return (
    <div className="page-content">
      <ErrorBoundary fallbackTitle="Portfolio data unavailable">
        <PortfolioSummary />
      </ErrorBoundary>
      <ErrorBoundary fallbackTitle="Equity curve failed to load">
        <EquityCurve />
      </ErrorBoundary>
      <ErrorBoundary fallbackTitle="Positions table error">
        <PositionsTable />
      </ErrorBoundary>
    </div>
  );
}
