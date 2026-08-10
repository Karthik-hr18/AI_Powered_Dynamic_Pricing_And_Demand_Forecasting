import React, { createContext, useContext, useState, useCallback } from "react";
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from "lucide-react";

const ToastContext = createContext(null);

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    ({
      type = "info", // "success" | "error" | "warning" | "info"
      title,
      message,
      action = null, // { label: string, onClick: Function }
      duration = 5000,
    }) => {
      const id = "toast-" + Date.now() + "-" + Math.random().toString(36).substr(2, 4);
      const newToast = { id, type, title, message, action, duration };

      setToasts((prev) => [...prev.slice(-4), newToast]); // Keep maximum 5 concurrent toasts

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }

      return id;
    },
    [removeToast]
  );

  // Helper shortcuts
  const success = useCallback(
    (title, message, options = {}) => showToast({ type: "success", title, message, ...options }),
    [showToast]
  );
  const error = useCallback(
    (title, message, options = {}) => showToast({ type: "error", title, message, ...options }),
    [showToast]
  );
  const warning = useCallback(
    (title, message, options = {}) => showToast({ type: "warning", title, message, ...options }),
    [showToast]
  );
  const info = useCallback(
    (title, message, options = {}) => showToast({ type: "info", title, message, ...options }),
    [showToast]
  );

  return (
    <ToastContext.Provider value={{ showToast, removeToast, success, error, warning, info }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};

// Internal Toast Container Component
const ToastContainer = ({ toasts, onDismiss }) => {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div
      aria-live="polite"
      aria-label="Notifications"
      style={{
        position: "fixed",
        bottom: "24px",
        right: "24px",
        zIndex: 9999,
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        maxWidth: "420px",
        width: "calc(100vw - 48px)",
        pointerEvents: "none",
      }}
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={() => onDismiss(toast.id)} />
      ))}
    </div>
  );
};

const TOAST_THEMES = {
  success: {
    borderColor: "rgba(16, 185, 129, 0.3)",
    iconColor: "#10B981",
    Icon: CheckCircle2,
    badgeBg: "rgba(16, 185, 129, 0.1)",
    defaultTitle: "Success",
  },
  error: {
    borderColor: "rgba(239, 68, 68, 0.35)",
    iconColor: "#EF4444",
    Icon: AlertCircle,
    badgeBg: "rgba(239, 68, 68, 0.1)",
    defaultTitle: "Error",
  },
  warning: {
    borderColor: "rgba(245, 158, 11, 0.35)",
    iconColor: "#F59E0B",
    Icon: AlertTriangle,
    badgeBg: "rgba(245, 158, 11, 0.1)",
    defaultTitle: "Warning",
  },
  info: {
    borderColor: "rgba(99, 102, 241, 0.3)",
    iconColor: "#6366F1",
    Icon: Info,
    badgeBg: "rgba(99, 102, 241, 0.1)",
    defaultTitle: "Notice",
  },
};

const ToastItem = ({ toast, onDismiss }) => {
  const theme = TOAST_THEMES[toast.type] || TOAST_THEMES.info;
  const { Icon } = theme;

  return (
    <div
      role="alert"
      style={{
        pointerEvents: "auto",
        backgroundColor: "#1E293B",
        color: "#F8FAFC",
        border: `1px solid ${theme.borderColor}`,
        borderRadius: "10px",
        padding: "14px 16px",
        boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3)",
        display: "flex",
        alignItems: "flex-start",
        gap: "12px",
        animation: "slideInRight 200ms ease-out",
        transition: "all 150ms ease",
      }}
    >
      <div
        style={{
          width: "28px",
          height: "28px",
          borderRadius: "8px",
          backgroundColor: theme.badgeBg,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          marginTop: "1px",
        }}
      >
        <Icon size={18} style={{ color: theme.iconColor }} />
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        {toast.title && (
          <h5
            style={{
              margin: 0,
              fontSize: "13px",
              fontWeight: 600,
              color: "#FFFFFF",
              letterSpacing: "-0.01em",
            }}
          >
            {toast.title}
          </h5>
        )}
        {toast.message && (
          <p
            style={{
              margin: toast.title ? "4px 0 0 0" : 0,
              fontSize: "12px",
              color: "rgba(226, 232, 240, 0.85)",
              lineHeight: 1.45,
            }}
          >
            {toast.message}
          </p>
        )}
        {toast.action && (
          <button
            onClick={() => {
              toast.action.onClick();
              onDismiss();
            }}
            style={{
              marginTop: "8px",
              padding: "4px 10px",
              fontSize: "11px",
              fontWeight: 600,
              color: "#FFFFFF",
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              border: "1px solid rgba(255, 255, 255, 0.2)",
              borderRadius: "6px",
              cursor: "pointer",
              transition: "all 120ms ease",
            }}
          >
            {toast.action.label}
          </button>
        )}
      </div>

      <button
        onClick={onDismiss}
        aria-label="Dismiss notification"
        style={{
          background: "none",
          border: "none",
          color: "rgba(148, 163, 184, 0.7)",
          cursor: "pointer",
          padding: "2px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "4px",
          flexShrink: 0,
          marginTop: "2px",
          transition: "color 120ms ease",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.color = "#FFFFFF")}
        onMouseLeave={(e) => (e.currentTarget.style.color = "rgba(148, 163, 184, 0.7)")}
      >
        <X size={15} />
      </button>
    </div>
  );
};
