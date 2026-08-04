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
      title: "AI Analysis Engine Completed",
      message: "Ingested sales_august_2026.csv (14,820 rows) and refreshed candidate pricing grids.",
      timestamp: "1 hour ago",
      link: "/uploads",
    },
    {
      id: "notif-4",
      type: "INFO",
      title: "Monthly Sales Goal Reached 64%",
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
        return <AlertTriangle size={16} style={{ color: "#F59E0B" }} />;
      case "COMPLETED":
        return <CheckCircle size={16} style={{ color: "#22C55E" }} />;
      default:
        return <Info size={16} style={{ color: "#3B82F6" }} />;
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
          backgroundColor: "#1E293B",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-lg)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5)",
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
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#FFFFFF" }}>Notifications</h4>
            <span className="badge badge-purple" style={{ fontSize: "10px" }}>{notifications.length} New</span>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--gray-text-muted)", cursor: "pointer" }}>
            <X size={16} />
          </button>
        </div>

        {/* Tab Filters */}
        <div style={{ display: "flex", borderBottom: "1px solid var(--gray-border)", backgroundColor: "rgba(15, 23, 42, 0.5)" }}>
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
                navigate(item.link);
                onClose();
              }}
              style={{
                padding: "var(--space-3) var(--space-4)",
                borderBottom: "1px solid rgba(255, 255, 255, 0.05)",
                cursor: "pointer",
                transition: "background-color 0.15s",
              }}
              className="command-item-hover"
            >
              <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
                {getIcon(item.type)}
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "2px" }}>
                    <span style={{ fontSize: "12px", fontWeight: 700, color: "#FFFFFF" }}>{item.title}</span>
                    <span style={{ fontSize: "10px", color: "var(--gray-text-muted)" }}>{item.timestamp}</span>
                  </div>
                  <p style={{ fontSize: "11px", color: "var(--gray-text-muted)", lineHeight: "1.4" }}>{item.message}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};
