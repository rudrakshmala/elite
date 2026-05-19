export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('elite_token');
  const isAuthenticated = localStorage.getItem('authenticated') === 'true';

  if (!token || !isAuthenticated) {
    window.location.href = '/login';
    return null;
  }

  return children;
}
