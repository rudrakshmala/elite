import { useEffect, useState } from 'react';

export default function ProtectedRoute({ children }) {
  const [isReady, setIsReady] = useState(false);
  const token = localStorage.getItem('elite_token');
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';

  useEffect(() => {
    // Only redirect if NOT already on login page (prevents infinite loop)
    if (!token || !isAuthenticated) {
      if (window.location.pathname !== '/login') {
        window.location.replace('/login');  // Use replace() to prevent back-button loop
      }
    }
    setIsReady(true);
  }, [token, isAuthenticated]);

  if (!isReady || !token || !isAuthenticated) {
    return null;
  }

  return children;
}