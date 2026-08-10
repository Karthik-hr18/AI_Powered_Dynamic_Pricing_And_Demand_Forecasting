import React from "react";
import { User, Settings, Bell, Key, CreditCard, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";

export const UserProfileMenu = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

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
    { label: "Profile", icon: <User size={15} />, action: () => { onClose(); toast.info("Profile", "Business profile settings will be configurable in your next store update."); } },
    { label: "Settings", icon: <Settings size={15} />, action: () => { onClose(); toast.info("Settings", "Account settings will be configurable in your next store update."); } },
    { label: "Notifications", icon: <Bell size={15} />, action: () => { onClose(); toast.info("Notifications", "Notification preferences will be configurable in your next store update."); } },
    { label: "API Keys", icon: <Key size={15} />, action: () => { onClose(); toast.info("API Keys", "Developer API keys will be configurable in your next store update."); } },
    { label: "Billing", icon: <CreditCard size={15} />, action: () => { onClose(); toast.info("Billing", "Subscription and billing management will be available in your next store update."); } },
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
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
          zIndex: 101,
          overflow: "hidden",
          padding: "var(--space-2)",
        }}
      >
        <div style={{ padding: "var(--space-3)", borderBottom: "1px solid var(--gray-border)", marginBottom: "var(--space-2)" }}>
          <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--gray-text-primary)", display: "block" }}>
            {user?.business_name || user?.email || "Demo Retailer"}
          </span>
          <span style={{ fontSize: "10px", fontWeight: 600, backgroundColor: "#EEF2FF", color: "var(--accent)", padding: "2px 6px", borderRadius: "4px", display: "inline-block", marginTop: "4px" }}>
            {user?.role || "RETAILER"} Tier
          </span>
        </div>

        {menuItems.map((item, idx) => (
          <div
            key={idx}
            onClick={() => {
              onClose();
              item.action();
            }}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-3)",
              padding: "8px 10px",
              borderRadius: "var(--radius-default)",
              cursor: "pointer",
              fontSize: "13px",
              color: "var(--gray-text-primary)",
              fontWeight: 500,
            }}
            className="menu-item-hover"
          >
            <span style={{ color: "var(--gray-text-muted)" }}>{item.icon}</span>
            {item.label}
          </div>
        ))}

        <div style={{ borderTop: "1px solid var(--gray-border)", marginTop: "var(--space-2)", paddingTop: "var(--space-2)" }}>
          <div
            onClick={handleLogout}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-3)",
              padding: "8px 10px",
              borderRadius: "var(--radius-default)",
              cursor: "pointer",
              fontSize: "13px",
              color: "var(--error)",
              fontWeight: 600,
            }}
            className="menu-item-hover-danger"
          >
            <LogOut size={15} />
            Sign Out
          </div>
        </div>
      </div>

      <style>{`
        .menu-item-hover:hover {
          background-color: #F8FAFC !important;
        }
        .menu-item-hover-danger:hover {
          background-color: #FEF2F2 !important;
        }
      `}</style>
    </>
  );
};
