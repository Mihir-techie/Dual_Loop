import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { login } from "../services/api";

export default function Login() {
  const { setToken, isAuthenticated, loading, token } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      const data = await login({ email, password });
      setToken(data.access_token);
      nav("/");
    } catch {
      setErr("Invalid email or password.");
    }
  };

  if (!loading && isAuthenticated) return <Navigate to="/" replace />;
  if (loading && token) {
    return (
      <div className="auth-page">
        <div className="muted">Restoring session…</div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card glass">
        <div className="auth-brand">
          <div className="brand-orbs" aria-hidden />
          <h1>Welcome back</h1>
          <p className="muted">Sign in to your cognitive support workspace.</p>
        </div>
        <form onSubmit={onSubmit} className="auth-form">
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </label>
          <label className="field">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </label>
          {err && <div className="form-error">{err}</div>}
          <button type="submit" className="btn primary wide">
            Sign in
          </button>
        </form>
        <p className="muted small center">
          New here? <Link to="/signup">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
