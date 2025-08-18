import { useEffect, useState } from "react";
import "./App.css";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

function App() {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const currentPath = window.location.pathname;
    const params = new URLSearchParams(window.location.search);

    if (currentPath === "/callback") {
      handleOAuthCallback(params);
    } else {
      checkExistingAuth();
    }

    setLoading(false);
  }, []);

  const handleOAuthCallback = async (params: any) => {
    const code = params.get("code");

    if (code) {
      try {
        const response = await fetch(
          `https://secureakey-backend.onrender.com/auth/callback?code=${code}`
        );
        const data = await response.json();

        localStorage.setItem("secureakey_token", data.access_token);
        localStorage.setItem("secureakey_username", data.user.github_username);

        setToken(data.access_token);
        setUser(data.user.github_username);

        // Redirect to main app
        window.location.href = "/";
      } catch (error) {
        console.error("OAuth callback failed:", error);
        setLoading(false);
      }
    } else {
      console.error("No code in callback");
      setLoading(false);
    }
  };

  const checkExistingAuth = () => {
    const storedToken = localStorage.getItem("secureakey_token");
    const storedUser = localStorage.getItem("secureakey_username");

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(storedUser);
    }

    setLoading(false);
  };

  const handleLogin = () => {
    window.location.href = "https://secureakey-backend.onrender.com/auth/login";
  };

  const handleLogout = () => {
    localStorage.removeItem("secureakey_token");
    localStorage.removeItem("secureakey_username");
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
