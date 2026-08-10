import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, LogIn, AlertCircle } from "lucide-react";
import { useAuth } from "../../../shared/hooks/useAuth";

export const LoginPage = () => {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    
    if (!email || !password) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setErrorMsg(err.message || "Failed to log in. Please check credentials.");
    }
  };

  return (
    <div>
      {/* Back to Home */}
      <Link
        to="/"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "13px",
          color: "rgba(165, 180, 252, 0.8)",
          textDecoration: "none",
          marginBottom: "20px",
          padding: "6px 12px",
          borderRadius: "9999px",
          border: "1px solid rgba(99, 102, 241, 0.25)",
          backgroundColor: "rgba(99, 102, 241, 0.07)",
          transition: "all 150ms ease",
          fontWeight: 500,
        }}
        onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = "rgba(99,102,241,0.15)"; e.currentTarget.style.color = "#A5B4FC"; }}
        onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = "rgba(99,102,241,0.07)"; e.currentTarget.style.color = "rgba(165,180,252,0.8)"; }}
      >
        ← Back to Home
      </Link>

      {/* Page Title Header */}
      <h3
        style={{
          fontSize: "24px",
          fontWeight: 700,
          marginBottom: "var(--space-1)",
          color: "#FFFFFF",
        }}
      >
        Welcome Back
      </h3>
      <p
        style={{
          fontSize: "14px",
          color: "var(--gray-text-muted)",
          marginBottom: "var(--space-5)",
        }}
      >
        Sign in to manage dynamic pricing and demand forecasts.
      </p>

      {/* Global Alert Notification */}
      {errorMsg && (
        <div
          className="badge badge-danger"
          style={{
            width: "100%",
            padding: "var(--space-3)",
            borderRadius: "var(--radius-default)",
            marginBottom: "var(--space-4)",
            textTransform: "none",
            letterSpacing: "normal",
            fontSize: "13px",
            justifyContent: "flex-start",
            fontWeight: 500,
          }}
        >
          <AlertCircle size={16} style={{ flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Login Form */}
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
        <div className="form-group">
          <label className="form-label" style={{ color: "#E2E8F0" }}>Email Address</label>
          <div style={{ position: "relative" }}>
            <span
              style={{
                position: "absolute",
                left: "14px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--gray-text-muted)",
                display: "flex",
                alignItems: "center",
              }}
            >
              <Mail size={18} />
            </span>
            <input
              type="email"
              className="form-input"
              placeholder="retailer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                paddingLeft: "42px",
                backgroundColor: "rgba(15, 23, 42, 0.6)",
                borderColor: "rgba(99, 102, 241, 0.2)",
                color: "#FFFFFF",
              }}
              required
              disabled={loading}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" style={{ color: "#E2E8F0" }}>Password</label>
          <div style={{ position: "relative" }}>
            <span
              style={{
                position: "absolute",
                left: "14px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--gray-text-muted)",
                display: "flex",
                alignItems: "center",
              }}
            >
              <Lock size={18} />
            </span>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                paddingLeft: "42px",
                backgroundColor: "rgba(15, 23, 42, 0.6)",
                borderColor: "rgba(99, 102, 241, 0.2)",
                color: "#FFFFFF",
              }}
              required
              disabled={loading}
            />
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          style={{ width: "100%", marginTop: "var(--space-2)" }}
          disabled={loading}
        >
          <LogIn size={18} />
          {loading ? "Signing in..." : "Sign In"}
        </button>

        {/* Demo Credential Cards */}
        <div style={{ marginTop: "var(--space-2)" }}>
          {/* Divider */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              marginBottom: "var(--space-3)",
            }}
          >
            <div style={{ flex: 1, height: "1px", backgroundColor: "rgba(99,102,241,0.2)" }} />
            <span
              style={{
                fontSize: "11px",
                color: "rgba(165,180,252,0.55)",
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                whiteSpace: "nowrap",
              }}
            >
              Quick Demo Access
            </span>
            <div style={{ flex: 1, height: "1px", backgroundColor: "rgba(99,102,241,0.2)" }} />
          </div>

          {/* Cards Row */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            {/* Retailer Card */}
            <button
              type="button"
              onClick={() => {
                setEmail("karthikhrvidyanidhi676@gmail.com");
                setPassword("11111111");
              }}
              style={{
                background: "rgba(34, 197, 94, 0.06)",
                border: "1px solid rgba(34, 197, 94, 0.25)",
                borderRadius: "10px",
                padding: "12px 14px",
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.2s ease",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(34,197,94,0.12)";
                e.currentTarget.style.borderColor = "rgba(34,197,94,0.45)";
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(34,197,94,0.06)";
                e.currentTarget.style.borderColor = "rgba(34,197,94,0.25)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "7px" }}>
                <span style={{ fontSize: "15px" }}>🏪</span>
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "rgba(74, 222, 128, 0.9)",
                  }}
                >
                  Retailer
                </span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <span
                  style={{
                    fontSize: "11px",
                    color: "rgba(226,232,240,0.65)",
                    fontFamily: "var(--font-mono, monospace)",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    maxWidth: "100%",
                  }}
                >
                  karthikhrvidyanidhi676
                  <br />@gmail.com
                </span>
                <span
                  style={{
                    fontSize: "11px",
                    color: "rgba(226,232,240,0.5)",
                    fontFamily: "var(--font-mono, monospace)",
                  }}
                >
                  Pass: 11111111
                </span>
              </div>
              <div
                style={{
                  fontSize: "10px",
                  color: "rgba(74,222,128,0.7)",
                  fontWeight: 600,
                  marginTop: "2px",
                }}
              >
                ↗ Click to auto-fill
              </div>
            </button>

            {/* Admin Card */}
            <button
              type="button"
              onClick={() => {
                setEmail("karthikhr676@gmail.com");
                setPassword("Karthik@123");
              }}
              style={{
                background: "rgba(139, 92, 246, 0.06)",
                border: "1px solid rgba(139, 92, 246, 0.25)",
                borderRadius: "10px",
                padding: "12px 14px",
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.2s ease",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(139,92,246,0.12)";
                e.currentTarget.style.borderColor = "rgba(139,92,246,0.45)";
                e.currentTarget.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "rgba(139,92,246,0.06)";
                e.currentTarget.style.borderColor = "rgba(139,92,246,0.25)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "7px" }}>
                <span style={{ fontSize: "15px" }}>🛡️</span>
                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: "rgba(196, 181, 253, 0.9)",
                  }}
                >
                  Administrator
                </span>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                <span
                  style={{
                    fontSize: "11px",
                    color: "rgba(226,232,240,0.65)",
                    fontFamily: "var(--font-mono, monospace)",
                  }}
                >
                  karthikhr676
                  <br />@gmail.com
                </span>
                <span
                  style={{
                    fontSize: "11px",
                    color: "rgba(226,232,240,0.5)",
                    fontFamily: "var(--font-mono, monospace)",
                  }}
                >
                  Pass: Karthik@123
                </span>
              </div>
              <div
                style={{
                  fontSize: "10px",
                  color: "rgba(196,181,253,0.7)",
                  fontWeight: 600,
                  marginTop: "2px",
                }}
              >
                ↗ Click to auto-fill
              </div>
            </button>
          </div>
        </div>

        {/* Forgot Password */}
        <div style={{ textAlign: "center" }}>
          <Link
            to="/forgot-password"
            style={{
              fontSize: "13px",
              color: "var(--gray-text-muted)",
              textDecoration: "none",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#A5B4FC")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "var(--gray-text-muted)")}
          >
            Forgot your password?
          </Link>
        </div>
      </form>

      {/* Navigation Redirect Pathway */}
      <div style={{ textAlign: "center", marginTop: "var(--space-5)" }}>
        <span style={{ fontSize: "14px", color: "var(--gray-text-muted)" }}>
          Don't have an account?{" "}
          <Link
            to="/register"
            style={{
              color: "var(--accent)",
              fontWeight: 600,
              textDecoration: "none",
            }}
          >
            Register Here
          </Link>
        </span>
      </div>
    </div>
  );
};

export default LoginPage;
