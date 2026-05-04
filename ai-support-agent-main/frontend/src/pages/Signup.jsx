import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { signup } from "../services/api";

export default function Signup() {
  const { setToken, isAuthenticated, loading, token } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [memoryConsent, setMemoryConsent] = useState(true);
  const [err, setErr] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      const data = await signup({
        email,
        password,
        display_name: displayName,
        memory_consent: memoryConsent,
      });
      setToken(data.access_token);
      nav("/");
    } catch (ex) {
      const detail = ex?.response?.data?.detail;
      const msg =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? detail.map((x) => x.msg || JSON.stringify(x)).join(", ")
            : "Could not create account.";
      setErr(msg);
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
          <h1>Create your account</h1>
          <p className="muted">
            Memory is the product: opt in to long-term semantic memory (Qdrant RAG) for evolving answers.
          </p>
        </div>
        <form onSubmit={onSubmit} className="auth-form">
          <label className="field">
            <span>Display name</span>
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              required
              minLength={1}
              autoComplete="nickname"
            />
          </label>
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
              minLength={6}
              autoComplete="new-password"
            />
          </label>
          <label className="consent-row">
            <input
              type="checkbox"
              checked={memoryConsent}
              onChange={(e) => setMemoryConsent(e.target.checked)}
            />
            <span>
              I consent to <strong>long-term personalized memory</strong> for support (SQLite transcript +
              Qdrant vectors). I can still use the app with session-only support if I turn this off.
            </span>
          </label>
          {err && <div className="form-error">{err}</div>}
          <button type="submit" className="btn primary wide">
            Create account
          </button>
        </form>
        <p className="muted small center">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
