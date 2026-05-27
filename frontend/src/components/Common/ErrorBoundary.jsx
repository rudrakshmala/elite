import { Component } from 'react';
import { AlertTriangle } from 'lucide-react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('Component Error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="card" style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', padding: '30px', gap: '10px',
          color: 'var(--text-tertiary)', textAlign: 'center'
        }}>
          <AlertTriangle size={28} style={{ color: 'var(--accent-gold)' }} />
          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
            {this.props.fallbackTitle || 'Component Error'}
          </div>
          <div style={{ fontSize: '11px' }}>
            {this.state.error?.message || 'Something went wrong'}
          </div>
          <button
            className="btn btn-ghost"
            style={{ marginTop: '8px', fontSize: '11px', padding: '6px 14px' }}
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Retry
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
