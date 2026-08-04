import React from "react";
import { User, Settings, Bell, Key, CreditCard, LogOut, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export const UserProfileMenu = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleLogout = async () => {
    try {
      await logout();
      onClose();
      navigate("/login");
    } catch (e) {
      console.error("Logout failed", e);
    }
  };

  const menuItems = [
    { label: "Business Profile", icon: <User size={15} />, action: () => alert("Business Profile Settings") },
    { label: "Account Settings", icon: <Settings size={15} />, action: () => alert("Account Settings") },
    { label: "Notification Preferences", icon: <Bell size={15} />, action: () => alert("Notification Preferences") },
    { label: "API Keys & Developer Tools", icon: <Key size={15} />, action: () => alert("API Keys (Enterprise Feature)") },
    { label: "Billing & Subscriptions", icon: <CreditCard size={15} />, action: () => alert("Billing & Plan Details") },
  ];

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} style={{ zIndex: 100 }} />
      <div
        style={{
          position: "fixed",
          bottom: "70px",
          left: "20px",
          width: "240px",
          backgroundColor: "#1E293B",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-lg)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5)",
          zIndex: 101,
          overflow: "hidden",
          padding: "var(--space-2)",
        }}
      >
        <div style={{ padding: "var(--space-3)", borderBottom: "1px solid var(--gray-border)", marginBottom: "var(--space-2)" }}>
          <span style={{ fontSize: "13px", fontWeight: 700, color: "#FFFFFF", display: "block" }}>
            {user?.business_name || user?.email || "Demo Retailer"}
          </span>
          <span className="badge badge-purple" style={{ fontSize: "10px", marginTop: "4px" }}>
            {user?.role || "RETAILER"} Tier
          </span>
        </div>

        {menuItems.map((item, idx) => (
          <div
            key={idx}
            onClick={() => {
              item.action();
              onClose();
            }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "8px 12px",
              fontSize: "12px",
              fontWeight: 600,
              color: "var(--gray-text-primary)",
              borderRadius: "var(--radius-sm)",
              cursor: "pointer",
            }}
            className="command-item-hover"
          >
            <div style={{ color: "var(--accent)" }}>{item.icon}</div>
            {item.label}
          </div>
        ))}

        <div style={{ borderTop: "1px solid var(--gray-border)", marginTop: "var(--space-2)", paddingTop: "var(--space-2)" }}>
          <div
            onClick={handleLogout}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "8px 12px",
              fontSize: "12px",
              fontWeight: 700,
              color: "#EF4444",
              borderRadius: "var(--radius-sm)",
              cursor: "pointer",
            }}
            className="command-item-hover"
          >
            <LogOut size={15} />
            Sign Out
          </div>
        </div>
      </div>
    </>
  );
};
