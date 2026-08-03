import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Mail, ArrowLeft, SendHorizonal, AlertCircle, CheckCircle2 } from "lucide-react";
import { useAuth } from "../../../shared/hooks/useAuth";

export const ForgotPasswordPage = () => {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null); // null | "success" | "error"
  const [errorMsg, setErrorMsg] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    setSubmitting(true);
    setErrorMsg("");
    setStatus(null);
    try {
      await forgotPassword(email.trim());
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message || "Failed to send reset email.");
      setStatus("error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      {/* Back link */}
      <Link
        to="/login"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "13px",
          color: "var(--gray-text-muted)",
          textDecoration: "none",
          marginBottom: "var(--space-5)",
          transition: "color 0.2s",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "#A5B4FC")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "var(--gray-text-muted)")}
      >
        <ArrowLeft size={14} />
        Back to Sign In
      </Link>

      {/* Header */}
      <h3
        style={{
          fontSize: "24px",
          fontWeight: 700,
          marginBottom: "var(--space-1)",
          color: "#FFFFFF",
        }}
      >
        Reset Your Password
      </h3>
      <p
        style={{
          fontSize: "14px",
          color: "var(--gray-text-muted)",
          marginBottom: "var(--space-5)",
          lineHeight: 1.6,
        }}
      >
        Enter the email address registered to your account and we'll send you a secure link to
        reset your password.
      </p>

      {/* Success state */}
      {status === "success" && (
        <div
          style={{
            background: "rgba(16,185,129,0.1)",
            border: "1px solid rgba(16,185,129,0.35)",
            borderRadius: "var(--radius-default)",
            padding: "var(--space-4)",
            display: "flex",
            gap: "var(--space-3)",
            alignItems: "flex-start",
            marginBottom: "var(--space-5)",
          }}
        >
          <CheckCircle2 size={18} style={{ color: "#34D399", flexShrink: 0, marginTop: "2px" }} />
          <div>
            <p style={{ color: "#34D399", fontWeight: 600, fontSize: "14px", marginBottom: "4px" }}>
              Reset link sent!
            </p>
            <p style={{ color: "#6EE7B7", fontSize: "13px", lineHeight: 1.5 }}>
              If <strong>{email}</strong> is registered, you'll receive a password reset link
              shortly. Check your spam folder if you don't see it.
            </p>
          </div>
        </div>
      )}

      {/* Error state */}
      {status === "error" && (
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

      {/* Form — hide after success */}
      {status !== "success" && (
        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}
        >
          <div className="form-group">
            <label className="form-label" style={{ color: "#E2E8F0" }}>
              Email Address
            </label>
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
                disabled={submitting}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-lg"
            style={{ width: "100%", marginTop: "var(--space-2)", justifyContent: "center" }}
            disabled={submitting}
          >
            <SendHorizonal size={17} />
            {submitting ? "Sending…" : "Send Reset Link"}
          </button>
        </form>
      )}

      {/* Resend link shown after success */}
      {status === "success" && (
        <button
          onClick={() => { setStatus(null); setEmail(""); }}
          style={{
            background: "transparent",
            border: "none",
            color: "var(--accent)",
            fontSize: "14px",
            fontWeight: 600,
            cursor: "pointer",
            padding: 0,
            marginTop: "var(--space-3)",
          }}
        >
          Use a different email
        </button>
      )}

      {/* Footer */}
      <div style={{ textAlign: "center", marginTop: "var(--space-6)" }}>
        <span style={{ fontSize: "14px", color: "var(--gray-text-muted)" }}>
          Remember your password?{" "}
          <Link
            to="/login"
            style={{ color: "var(--accent)", fontWeight: 600, textDecoration: "none" }}
          >
            Sign In
          </Link>
        </span>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
