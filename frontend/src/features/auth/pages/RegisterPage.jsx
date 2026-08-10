import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Lock, UserPlus, AlertCircle, Building, ArrowLeft, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../../../shared/hooks/useAuth";

export const RegisterPage = () => {
  const { register, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState("RETAILER");
  const [businessName, setBusinessName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");

    if (!email || !password) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    if (role === "RETAILER" && !businessName.trim()) {
      setErrorMsg("Business name is required for retailers.");
      return;
    }

    try {
      await register(email, password, role, businessName.trim());
      navigate("/dashboard");
    } catch (err) {
      setErrorMsg(err.message || "Failed to register. Please try again.");
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
        <ArrowLeft size={13} />
        Back to Home
      </Link>

      {/* Page Title Header */}
      <h3 style={{ fontSize: "24px", fontWeight: 700, marginBottom: "var(--space-1)", color: "#FFFFFF" }}>
        Create Account
      </h3>
      <p style={{ fontSize: "14px", color: "var(--gray-text-muted)", marginBottom: "var(--space-5)" }}>
        Sign up to start optimizing margins and predicting sales.
      </p>

      {/* Error Banner */}
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

      {/* Register Form */}
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
        {/* Email Address */}
        <div className="form-group">
          <label className="form-label" style={{ color: "#E2E8F0" }}>Email Address</label>
          <div style={{ position: "relative" }}>
            <span style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--gray-text-muted)", display: "flex", alignItems: "center" }}>
              <Mail size={18} />
            </span>
            <input
              type="email"
              className="form-input"
              placeholder="retailer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ paddingLeft: "42px", backgroundColor: "rgba(15, 23, 42, 0.6)", borderColor: "rgba(99, 102, 241, 0.2)", color: "#FFFFFF" }}
              required
              disabled={loading}
            />
          </div>
        </div>

        {/* Password with show/hide toggle */}
        <div className="form-group">
          <label className="form-label" style={{ color: "#E2E8F0" }}>Password</label>
          <div style={{ position: "relative" }}>
            <span style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--gray-text-muted)", display: "flex", alignItems: "center" }}>
              <Lock size={18} />
            </span>
            <input
              type={showPassword ? "text" : "password"}
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ paddingLeft: "42px", paddingRight: "44px", backgroundColor: "rgba(15, 23, 42, 0.6)", borderColor: "rgba(99, 102, 241, 0.2)", color: "#FFFFFF" }}
              required
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              tabIndex={-1}
              style={{
                position: "absolute",
                right: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                color: "var(--gray-text-muted)",
                display: "flex",
                alignItems: "center",
                padding: "2px",
                transition: "color 0.15s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.color = "#A5B4FC")}
              onMouseLeave={(e) => (e.currentTarget.style.color = "var(--gray-text-muted)")}
            >
              {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
        </div>

        {/* Account type is always RETAILER — Admin account is pre-seeded */}

        {/* Conditional Business Name for Retailers */}
        {role === "RETAILER" && (
          <div className="form-group">
            <label className="form-label" style={{ color: "#E2E8F0" }}>Business Name</label>
            <div style={{ position: "relative" }}>
              <span style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--gray-text-muted)", display: "flex", alignItems: "center" }}>
                <Building size={18} />
              </span>
              <input
                type="text"
                className="form-input"
                placeholder="Apex Retailers Ltd."
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                style={{ paddingLeft: "42px", backgroundColor: "rgba(15, 23, 42, 0.6)", borderColor: "rgba(99, 102, 241, 0.2)", color: "#FFFFFF" }}
                required
                disabled={loading}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          style={{ width: "100%", marginTop: "var(--space-2)" }}
          disabled={loading}
        >
          <UserPlus size={18} />
          {loading ? "Creating account..." : "Sign Up"}
        </button>
      </form>

      {/* Sign In Redirect */}
      <div style={{ textAlign: "center", marginTop: "var(--space-5)" }}>
        <span style={{ fontSize: "14px", color: "var(--gray-text-muted)" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "var(--accent)", fontWeight: 600, textDecoration: "none" }}>
            Sign In Here
          </Link>
        </span>
      </div>
    </div>
  );
};

export default RegisterPage;
