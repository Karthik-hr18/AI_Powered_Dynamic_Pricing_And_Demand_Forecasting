import React from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught application error boundary caught:", error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          role="alert"
          style={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            backgroundColor: "#0F172A",
            color: "#F8FAFC",
            padding: "24px",
            textAlign: "center",
            fontFamily: "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
          }}
        >
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "14px",
              backgroundColor: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "20px",
            }}
          >
            <AlertTriangle size={28} style={{ color: "#EF4444" }} />
          </div>

          <h2
            style={{
              fontSize: "22px",
              fontWeight: 700,
              margin: "0 0 8px 0",
              color: "#FFFFFF",
              letterSpacing: "-0.02em",
            }}
          >
            Something went wrong
          </h2>

          <p
            style={{
              fontSize: "14px",
              color: "rgba(226, 232, 240, 0.7)",
              maxWidth: "420px",
              margin: "0 0 24px 0",
              lineHeight: 1.5,
            }}
          >
            We couldn't display this page correctly. Your data is safe and has not been affected.
          </p>

          <button
            onClick={this.handleReload}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "8px",
              padding: "10px 20px",
              backgroundColor: "#6366F1",
              color: "#FFFFFF",
              border: "none",
              borderRadius: "8px",
              fontSize: "13px",
              fontWeight: 600,
              cursor: "pointer",
              boxShadow: "0 4px 12px rgba(99, 102, 241, 0.35)",
              transition: "background-color 150ms ease",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#4F46E5")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#6366F1")}
          >
            <RefreshCw size={15} />
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
