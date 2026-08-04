import React, { useState } from "react";
import { Bell, AlertTriangle, Info, CheckCircle, X, ExternalLink } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const NotificationCenter = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("ALL");

  if (!isOpen) return null;

  const notifications = [
    {
      id: "notif-1",
      type: "CRITICAL",
      title: "Stockout Risk: Organic Whole Milk 1L",
      message: "Current inventory (120 units) covers only 4.2 days based on demand velocity.",
      timestamp: "10 mins ago",
      link: "/products?search=milk",
    },
    {
      id: "notif-2",
      type: "WARNING",
      title: "Price Spike Anomaly Detected",
      message: "Artisan Sourdough Bread experienced +140% sales volume spike on Sunday.",
      timestamp: "35 mins ago",
      link: "/dashboard",
    },
    {
      id: "notif-3",
      type: "COMPLETED",
      title: "Data Upload Processed",
      message: "Ingested sales_august_2026.csv (14,820 rows) and updated pricing models.",
      timestamp: "1 hour ago",
      link: "/uploads",
    },
    {
      id: "notif-4",
      type: "INFO",
      title: "Monthly Revenue Target 64%",
      message: "Store is currently on track to reach the $50,000 monthly target.",
      timestamp: "2 hours ago",
      link: "/dashboard",
    },
  ];

  const filteredNotifs =
    activeTab === "ALL"
      ? notifications
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

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} style={{ zIndex: 100 }} />
      <div
        style={{
          position: "fixed",
          top: "60px",
          right: "20px",
          width: "360px",
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
          zIndex: 101,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "var(--space-3) var(--space-4)",
            borderBottom: "1px solid var(--gray-border)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Bell size={16} style={{ color: "var(--accent)" }} />
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "var(--gray-text-primary)" }}>Notifications</h4>
            <span style={{ fontSize: "10px", fontWeight: 700, backgroundColor: "#EEF2FF", color: "var(--accent)", padding: "2px 6px", borderRadius: "9999px" }}>
              {notifications.length} New
            </span>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--gray-text-muted)", cursor: "pointer" }}>
            <X size={16} />
          </button>
        </div>

        {/* Tab Filters */}
        <div style={{ display: "flex", borderBottom: "1px solid var(--gray-border)", backgroundColor: "#F8FAFC" }}>
          {["ALL", "CRITICAL", "WARNING", "COMPLETED"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                flex: 1,
                padding: "8px 0",
                fontSize: "10px",
                fontWeight: 700,
                color: activeTab === tab ? "var(--accent)" : "var(--gray-text-muted)",
                borderBottom: activeTab === tab ? "2px solid var(--accent)" : "none",
                background: "none",
                borderTop: "none",
                borderLeft: "none",
                borderRight: "none",
                cursor: "pointer",
              }}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Notification List */}
        <div style={{ maxHeight: "320px", overflowY: "auto" }}>
          {filteredNotifs.map((item) => (
            <div
              key={item.id}
              onClick={() => {
                onClose();
                navigate(item.link);
              }}
              style={{
                padding: "var(--space-3) var(--space-4)",
                borderBottom: "1px solid var(--gray-border)",
                cursor: "pointer",
                transition: "background-color 0.15s",
                display: "flex",
                gap: "var(--space-3)",
                alignItems: "flex-start",
              }}
              className="notif-item-hover"
            >
              <div style={{ marginTop: "2px" }}>{getIcon(item.type)}</div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h5 style={{ fontSize: "13px", fontWeight: 700, color: "var(--gray-text-primary)" }}>{item.title}</h5>
                  <span style={{ fontSize: "10px", color: "var(--gray-text-muted)" }}>{item.timestamp}</span>
                </div>
                <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: "3px 0 0 0" }}>{item.message}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .notif-item-hover:hover {
          background-color: #F8FAFC !important;
        }
      `}</style>
    </>
  );
};
