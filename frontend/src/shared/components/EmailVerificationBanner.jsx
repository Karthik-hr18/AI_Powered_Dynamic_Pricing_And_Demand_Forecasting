import React, { useState } from "react";
import { MailCheck, RefreshCw, LogOut, ShieldCheck, X } from "lucide-react";
import { useAuth } from "../hooks/useAuth";

/**
 * EmailVerificationBanner
 * ─────────────────────────────────────────────────────────────
 * Full-screen overlay modal shown to unverified RETAILER accounts.
 * Blocks access until the user verifies their email via the link
 * sent by Firebase. Includes a resend button and a "check again"
 * polling action to detect when verification completes.
 */
export const EmailVerificationBanner = () => {
  const { firebaseUser, user, resendVerificationEmail, reloadFirebaseUser, logout } = useAuth();
  const [resendStatus, setResendStatus] = useState(null); // null | "sent" | "error"
  const [checking, setChecking] = useState(false);
  const [resendDisabled, setResendDisabled] = useState(false);

  const handleResend = async () => {
    setResendStatus(null);
    setResendDisabled(true);
    try {
      await resendVerificationEmail();
      setResendStatus("sent");
    } catch (e) {
      setResendStatus("error");
    }
    // Throttle resend: re-enable after 60 seconds
    setTimeout(() => setResendDisabled(false), 60000);
  };

  const handleCheckVerification = async () => {
    setChecking(true);
    await reloadFirebaseUser();
    setTimeout(() => setChecking(false), 1200);
  };

  const email = firebaseUser?.email || user?.email || "your email";
  const businessName = user?.business_name || "your business";

  return (
    <>
      {/* Backdrop */}
      <div
        style={{
          position: "fixed",
          inset: 0,
          backgroundColor: "rgba(5, 8, 20, 0.85)",
          backdropFilter: "blur(12px)",
          zIndex: 9000,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "var(--space-5)",
        }}
      >
        {/* Card */}
        <div
          style={{
            position: "relative",
            width: "100%",
            maxWidth: "480px",
            background: "linear-gradient(145deg, rgba(15,23,42,0.98) 0%, rgba(20,30,60,0.98) 100%)",
            border: "1px solid rgba(99,102,241,0.35)",
            borderRadius: "var(--radius-modal)",
            padding: "var(--space-7) var(--space-6)",
            boxShadow: "0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.1)",
            textAlign: "center",
            animation: "slideUpFade 0.35s cubic-bezier(0.4,0,0.2,1) both",
          }}
        >
          {/* Glow ring behind icon */}
          <div
            style={{
              width: "80px",
              height: "80px",
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(79,70,229,0.25) 0%, transparent 70%)",
              border: "2px solid rgba(79,70,229,0.4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto var(--space-5)",
              position: "relative",
            }}
          >
            <MailCheck size={36} style={{ color: "#818CF8" }} />
            {/* Animated pulse ring */}
            <div
              style={{
                position: "absolute",
                inset: "-6px",
                borderRadius: "50%",
                border: "2px solid rgba(99,102,241,0.3)",
                animation: "pulseRing 2s ease-out infinite",
              }}
            />
          </div>

          {/* Title */}
          <h2
            style={{
              fontSize: "22px",
              fontWeight: 700,
              color: "#F1F5F9",
              marginBottom: "var(--space-2)",
              letterSpacing: "-0.3px",
            }}
          >
            Verify Your Email to Continue
          </h2>

          {/* Subtitle */}
          <p
            style={{
              fontSize: "14px",
              color: "#94A3B8",
              marginBottom: "var(--space-5)",
              lineHeight: 1.65,
            }}
          >
            Welcome to the platform, <strong style={{ color: "#C7D2FE" }}>{businessName}</strong>!
            A verification link has been sent to{" "}
            <strong style={{ color: "#A5B4FC" }}>{email}</strong>.
            <br />
            Please check your inbox (and spam folder) to activate your account.
          </p>

          {/* Info pill */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "var(--space-2)",
              backgroundColor: "rgba(79,70,229,0.12)",
              border: "1px solid rgba(99,102,241,0.3)",
              borderRadius: "var(--radius-pill)",
              padding: "var(--space-2) var(--space-4)",
              marginBottom: "var(--space-6)",
            }}
          >
            <ShieldCheck size={14} style={{ color: "#818CF8" }} />
            <span style={{ fontSize: "12px", color: "#A5B4FC", fontWeight: 500 }}>
              Email verification protects your account
            </span>
          </div>

          {/* CTA buttons */}
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            {/* Check verification button */}
            <button
              onClick={handleCheckVerification}
              disabled={checking}
              className="btn btn-primary btn-lg"
              style={{ width: "100%", justifyContent: "center" }}
            >
              <RefreshCw
                size={17}
                style={{
                  transition: "transform 0.6s ease",
                  transform: checking ? "rotate(360deg)" : "none",
                }}
              />
              {checking ? "Checking…" : "I've Verified — Continue"}
            </button>

            {/* Resend button */}
            <button
              onClick={handleResend}
              disabled={resendDisabled}
              style={{
                background: "transparent",
                border: "1px solid rgba(99,102,241,0.3)",
                borderRadius: "var(--radius-default)",
                padding: "10px 20px",
                color: resendDisabled ? "#475569" : "#818CF8",
                fontSize: "14px",
                fontWeight: 500,
                cursor: resendDisabled ? "not-allowed" : "pointer",
                transition: "all 0.2s",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "var(--space-2)",
                width: "100%",
              }}
            >
              <MailCheck size={16} />
              {resendDisabled ? "Email sent — check your inbox" : "Resend Verification Email"}
            </button>
          </div>

          {/* Status feedback */}
          {resendStatus === "sent" && (
            <p
              style={{
                marginTop: "var(--space-3)",
                fontSize: "13px",
                color: "#34D399",
                fontWeight: 500,
              }}
            >
              ✓ Verification email sent! Check your inbox.
            </p>
          )}
          {resendStatus === "error" && (
            <p
              style={{
                marginTop: "var(--space-3)",
                fontSize: "13px",
                color: "#F87171",
                fontWeight: 500,
              }}
            >
              Failed to send email. Please try again later.
            </p>
          )}

          {/* Divider */}
          <div
            style={{
              height: "1px",
              background: "rgba(99,102,241,0.15)",
              margin: "var(--space-5) 0 var(--space-4)",
            }}
          />

          {/* Logout escape */}
          <button
            onClick={logout}
            style={{
              background: "transparent",
              border: "none",
              color: "#64748B",
              fontSize: "13px",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "6px",
              margin: "0 auto",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#94A3B8")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#64748B")}
          >
            <LogOut size={13} />
            Sign out and use a different account
          </button>
        </div>
      </div>

      {/* Keyframe animations injected inline */}
      <style>{`
        @keyframes slideUpFade {
          from { opacity: 0; transform: translateY(24px) scale(0.97); }
          to   { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes pulseRing {
          0%   { opacity: 0.8; transform: scale(1); }
          100% { opacity: 0;   transform: scale(1.5); }
        }
      `}</style>
    </>
  );
};

export default EmailVerificationBanner;
