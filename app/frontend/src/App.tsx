import { useEffect, useState } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

function App() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const tokenFromUrl = params.get('token');
    const usernameFromUrl = params.get('username');

    if (tokenFromUrl && usernameFromUrl) {
      localStorage.setItem('secureakey_token', tokenFromUrl);
      localStorage.setItem('secureakey_username', usernameFromUrl);
      setToken(tokenFromUrl);
      setUser(usernameFromUrl);

      window.history.replaceState({}, document.title, '/');
    } else {
      
      const storedToken = localStorage.getItem('secureakey_token');
      const storedUser = localStorage.getItem('secureakey_username');
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(storedUser);
      }
    }

    setLoading(false); 
  }, []);

  const handleLogin = () => {
    window.location.href = 'https://secureakey-backend.onrender.com/auth/login';
  };

  const handleLogout = () => {
    localStorage.removeItem('secureakey_token');
    localStorage.removeItem('secureakey_username');
    setToken(null);
    setUser(null);
  };

  if (loading) return null;

  if (!token || !user) {
    return <Login onLogin={handleLogin} />;
  }

  return <Dashboard user={user} token={token} onLogout={handleLogout} />;
}

export default App;
