import React from "react";

export const AuthLayout = ({ children }) => {
  return (
    <div
      style={{
        backgroundColor: "var(--dark-bg)",
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "var(--space-4)",
        backgroundImage: "radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 45%)",
      }}
    >
      <div
        className="card auth-card-container"
        style={{
          width: "100%",
          maxWidth: "880px",
          padding: 0,
          backgroundColor: "var(--dark-surface)",
          borderColor: "var(--dark-border)",
          boxShadow: "var(--shadow-dark-ambient)",
          overflow: "hidden",
          display: "flex",
          minHeight: "520px",
          color: "#E2E8F0",
        }}
      >
        {/* Left Side: Brand Pitch Hero */}
        <div
          style={{
            flex: 1,
            background: "linear-gradient(135deg, var(--accent), var(--accent-hover))",
            padding: "var(--space-6)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            position: "relative",
            overflow: "hidden",
          }}
          className="auth-hero-panel"
        >
          {/* Subtle Ambient Decorative Circles */}
          <div
            style={{
              position: "absolute",
              top: "-50px",
              left: "-50px",
              width: "200px",
              height: "200px",
              borderRadius: "50%",
              background: "rgba(255, 255, 255, 0.1)",
              filter: "blur(20px)",
            }}
          />
          <div
            style={{
              position: "absolute",
              bottom: "-80px",
              right: "-80px",
              width: "300px",
              height: "300px",
              borderRadius: "50%",
              background: "rgba(99, 102, 241, 0.2)",
              filter: "blur(30px)",
            }}
          />

          <div style={{ position: "relative", zIndex: 1 }}>
            <h2
              style={{
                color: "#FFFFFF",
                fontSize: "32px",
                fontWeight: 800,
                marginBottom: "var(--space-3)",
                lineHeight: 1.2,
                letterSpacing: "-0.02em",
              }}
            >
              ProfitSync Retail OS
            </h2>
            <p
              style={{
                color: "#E0E7FF",
                fontSize: "15px",
                lineHeight: 1.6,
                fontWeight: 500,
              }}
            >
              Enterprise demand forecasting and revenue optimization built for Indian retail enterprises.
            </p>
          </div>
        </div>

        {/* Right Side: Render children login/register forms */}
        <div
          className="auth-form-panel"
          style={{
            flex: 1.2,
            padding: "var(--space-6) var(--space-7)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            backgroundColor: "rgba(15, 23, 42, 0.4)",
          }}
        >
          {children}
        </div>
      </div>

      <style>{`
        @media (max-width: 767px) {
          .auth-card-container {
            flex-direction: column !important;
            max-width: 440px !important;
            min-height: auto !important;
            border-radius: 16px !important;
          }
          .auth-hero-panel {
            padding: 24px 20px !important;
            text-align: center;
          }
          .auth-hero-panel h2 {
            font-size: 22px !important;
            margin-bottom: 6px !important;
          }
          .auth-hero-panel p {
            font-size: 13px !important;
          }
          .auth-form-panel {
            padding: 24px 20px !important;
          }
          .form-input {
            height: 44px !important;
            font-size: 15px !important;
          }
          .btn-primary {
            height: 46px !important;
            font-size: 15px !important;
          }
        }
      `}</style>
    </div>
  );
};

export default AuthLayout;
