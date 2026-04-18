import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';
import { usePolling } from '../../hooks/usePolling';
import api from '../../api/client';

export default function AgentTerminal() {
  const scrollRef = useRef(null);
  const { data } = usePolling(() => api.getBotLogs(60), 2000);

  const logs = data?.logs || [];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs.length]);

  return (
    <div className="terminal">
      <div className="terminal-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="dots">
            <span className="dot red" />
            <span className="dot yellow" />
            <span className="dot green" />
          </div>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>
            <Terminal size={13} style={{ marginRight: 4 }} />
            AI Agent Terminal
          </span>
        </div>
        <span style={{ fontSize: '10px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
          {logs.length} entries
        </span>
      </div>
      <div className="terminal-body" ref={scrollRef}>
        {logs.length === 0 ? (
          <div style={{ color: 'var(--text-tertiary)', fontStyle: 'italic' }}>
            Waiting for bot activity...
          </div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className={`log-entry ${log.level}`} style={{ animationDelay: `${i * 0.02}s` }}>
              <span className="log-ts">[{log.ts}]</span>
              <span className="log-msg">{log.msg}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
