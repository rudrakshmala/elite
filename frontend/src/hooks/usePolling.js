import { useState, useEffect, useRef } from 'react';

export function usePolling(fetchFn, intervalMs = 5000, deps = []) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    let timer;

    async function poll() {
      try {
        const result = await fetchFn();
        if (mountedRef.current) {
          setData(result);
          setError(null);
          setLoading(false);
        }
      } catch (err) {
        if (mountedRef.current) {
          setError(err.message);
          setLoading(false);
        }
      }
      if (mountedRef.current) {
        timer = setTimeout(poll, intervalMs);
      }
    }

    poll();

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
    };
  }, deps);

  return { data, error, loading, refetch: () => fetchFn().then(setData) };
}
