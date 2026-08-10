import React, { useState } from "react";
import { Bell, AlertTriangle, Info, CheckCircle, X, CheckCheck, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useNotifications } from "../hooks/useNotifications";

export const NotificationCenter = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { notifications, unreadCount, markAsRead, markAllAsRead, refreshNotifications, isLoading } = useNotifications();
  const [activeTab, setActiveTab] = useState("ALL");

  if (!isOpen) return null;

  const filteredNotifs =
    activeTab === "ALL"
      ? notifications
      : activeTab === "UNREAD"
      ? notifications.filter((n) => !n.isRead)
      : notifications.filter((n) => n.type === activeTab);

  const getIcon = (type) => {
    switch (type) {
      case "CRITICAL":
        return <AlertTriangle size={16} style={{ color: "#EF4444" }} />;
      case "WARNING":
        return <AlertTriangle size={16} style={{ color: "#D97706" }} />;
      case "COMPLETED":
        return <CheckCircle size={16} style={{ color: "#10B981" }} />;
      default:
        return <Info size={16} style={{ color: "#4F46E5" }} />;
    }
  };

  const handleItemClick = (item) => {
    markAsRead(item.id);
    onClose();
    if (item.link) {
      navigate(item.link);
    }
  };

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} style={{ zIndex: 100 }} />
      <div
        style={{
          position: "fixed",
          top: "60px",
          right: "20px",
          width: "380px",
          maxWidth: "calc(100vw - 40px)",
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
          zIndex: 101,
          overflow: "hidden",
          animation: "fadeIn 150ms ease-out",
        }}
      >
        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "12px 16px",
            borderBottom: "1px solid var(--gray-border)",
            backgroundColor: "#FFFFFF",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Bell size={16} style={{ color: "var(--accent)" }} />
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "var(--gray-text-primary)", margin: 0 }}>
              Live Alerts & Updates
            </h4>
            {unreadCount > 0 && (
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  backgroundColor: "#FEF2F2",
                  color: "#EF4444",
                  border: "1px solid #FECACA",
                  padding: "2px 6px",
                  borderRadius: "9999px",
                }}
              >
                {unreadCount} New
              </span>
            )}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                title="Mark all as read"
                style={{
                  background: "none",
                  border: "none",
                  fontSize: "11px",
                  color: "var(--accent)",
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "4px 6px",
                  borderRadius: "4px",
                }}
              >
                <CheckCheck size={13} />
                Mark read
              </button>
            )}
            <button
              onClick={onClose}
              style={{
                background: "none",
                border: "none",
                color: "var(--gray-text-muted)",
                cursor: "pointer",
                padding: "4px",
                borderRadius: "4px",
                display: "flex",
                alignItems: "center",
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Tab Filters */}
        <div
          style={{
            display: "flex",
            borderBottom: "1px solid var(--gray-border)",
            backgroundColor: "#F8FAFC",
          }}
        >
          {[
            { id: "ALL", label: "All" },
            { id: "UNREAD", label: `Unread (${unreadCount})` },
            { id: "CRITICAL", label: "Risks" },
            { id: "WARNING", label: "Pricing" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1,
                padding: "8px 0",
                fontSize: "11px",
                fontWeight: 600,
                color: activeTab === tab.id ? "var(--accent)" : "var(--gray-text-muted)",
                borderBottom: activeTab === tab.id ? "2px solid var(--accent)" : "2px solid transparent",
                backgroundColor: activeTab === tab.id ? "#FFFFFF" : "transparent",
                borderTop: "none",
                borderLeft: "none",
                borderRight: "none",
                cursor: "pointer",
                transition: "all 120ms ease",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Notification List */}
        <div style={{ maxHeight: "360px", overflowY: "auto" }}>
          {filteredNotifs.length === 0 ? (
            <div style={{ padding: "36px 16px", textAlign: "center" }}>
              <CheckCircle size={32} style={{ color: "#10B981", margin: "0 auto 8px auto", opacity: 0.8 }} />
              <h5 style={{ fontSize: "13px", fontWeight: 700, margin: "0 0 4px 0", color: "var(--gray-text-primary)" }}>
                You're All Caught Up!
              </h5>
              <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0 }}>
                {activeTab === "UNREAD"
                  ? "No unread alerts. All notifications have been reviewed."
                  : "No active alerts or critical risks detected in your dataset."}
              </p>
            </div>
          ) : (
            filteredNotifs.map((item, idx) => (
              <div
                key={item.id || `notif-${idx}`}
                onClick={() => handleItemClick(item)}
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--gray-border)",
                  cursor: "pointer",
                  transition: "background-color 0.15s ease",
                  display: "flex",
                  gap: "12px",
                  alignItems: "flex-start",
                  backgroundColor: item.isRead ? "#FFFFFF" : "rgba(238, 242, 255, 0.4)",
                  position: "relative",
                }}
                className="notif-item-hover"
              >
                {!item.isRead && (
                  <div
                    style={{
                      position: "absolute",
                      left: "4px",
                      top: "50%",
                      transform: "translateY(-50%)",
                      width: "4px",
                      height: "24px",
                      borderRadius: "2px",
                      backgroundColor: "var(--accent)",
                    }}
                  />
                )}
                <div style={{ marginTop: "2px", flexShrink: 0 }}>{getIcon(item.type)}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "6px" }}>
                    <h5
                      style={{
                        fontSize: "13px",
                        fontWeight: item.isRead ? 600 : 700,
                        color: "var(--gray-text-primary)",
                        margin: 0,
                        lineHeight: 1.3,
                      }}
                    >
                      {item.title}
                    </h5>
                    <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", whiteSpace: "nowrap" }}>
                      {item.timestamp}
                    </span>
                  </div>
                  <p
                    style={{
                      fontSize: "12px",
                      color: item.isRead ? "var(--gray-text-muted)" : "#334155",
                      margin: "4px 0 0 0",
                      lineHeight: 1.4,
                    }}
                  >
                    {item.message}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer info */}
        <div
          style={{
            padding: "8px 16px",
            backgroundColor: "#F8FAFC",
            borderTop: "1px solid var(--gray-border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
            Updated from latest sales upload
          </span>
          <button
            onClick={() => refreshNotifications()}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px",
              fontSize: "11px",
              color: "var(--accent)",
              fontWeight: 600,
            }}
          >
            <RefreshCw size={11} className={isLoading ? "spin-clockwise" : ""} />
            Sync
          </button>
        </div>
      </div>

      <style>{`
        .notif-item-hover:hover {
          background-color: #F1F5F9 !important;
        }
      `}</style>
    </>
  );
};

