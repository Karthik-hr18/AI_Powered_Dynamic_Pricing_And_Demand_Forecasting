import React, { useState, useEffect } from "react";
import {
  User,
  Settings,
  Bell,
  X,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  Building,
  Mail,
  Shield,
  Calendar,
  Sliders,
  Sparkles,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useNotifications } from "../hooks/useNotifications";
import { useToast } from "../hooks/useToast";

export const AccountSettingsModal = ({ isOpen, onClose, initialTab = "profile" }) => {
  const { user, isEmailVerified } = useAuth();
  const { preferences, updatePreferences } = useNotifications();
  const toast = useToast();

  const [activeTab, setActiveTab] = useState(initialTab);
  const [copiedId, setCopiedId] = useState(false);

  // Store preferences state persisted in localStorage
  const [defaultHorizon, setDefaultHorizon] = useState(() => {
    return localStorage.getItem("profitsync_pref_horizon") || "7d";
  });
  const [minGainThreshold, setMinGainThreshold] = useState(() => {
    return localStorage.getItem("profitsync_pref_min_gain") || "500";
  });

  // Sync initial tab when modal opens
  useEffect(() => {
    if (isOpen && initialTab) {
      setActiveTab(initialTab);
    }
  }, [isOpen, initialTab]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleCopyId = () => {
    const idToCopy = user?.id || user?._id || "";
    if (idToCopy) {
      navigator.clipboard.writeText(String(idToCopy));
      setCopiedId(true);
      toast.success("Copied to Clipboard", "Retailer ID copied successfully.");
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  const handleSaveStorePreferences = (e) => {
    e.preventDefault();
    localStorage.setItem("profitsync_pref_horizon", defaultHorizon);
    localStorage.setItem("profitsync_pref_min_gain", minGainThreshold);
    toast.success("Preferences Saved", "Store defaults have been updated.");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    } catch {
      return String(dateStr);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container"
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: "600px",
          width: "100%",
          padding: 0,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          maxHeight: "90vh",
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: "20px 24px",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            backgroundColor: "#FFFFFF",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "10px",
                backgroundColor: "rgba(79, 70, 229, 0.1)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--accent)",
              }}
            >
              <Settings size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0, color: "var(--gray-text-primary)" }}>
                Account & Store Settings
              </h3>
              <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0 }}>
                Manage your retailer profile, analytics defaults, and alerts
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="modal-close-btn"
            style={{ position: "static" }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div
          style={{
            display: "flex",
            borderBottom: "1px solid var(--gray-border)",
            backgroundColor: "var(--gray-bg)",
            padding: "0 24px",
            gap: "16px",
          }}
        >
          {[
            { id: "profile", label: "Store Profile", icon: <User size={15} /> },
            { id: "store", label: "Store Preferences", icon: <Sliders size={15} /> },
            { id: "notifications", label: "Alert Preferences", icon: <Bell size={15} /> },
          ].map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "12px 0",
                  fontSize: "13px",
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? "var(--accent)" : "var(--gray-text-muted)",
                  borderBottom: isActive ? "2px solid var(--accent)" : "2px solid transparent",
                  background: "none",
                  borderTop: "none",
                  borderLeft: "none",
                  borderRight: "none",
                  cursor: "pointer",
                  transition: "all 150ms ease",
                }}
              >
                {tab.icon}
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content Body */}
        <div style={{ padding: "24px", overflowY: "auto", flex: 1 }}>
          {/* TAB 1: PROFILE */}
          {activeTab === "profile" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              {/* Top Banner Card */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "16px",
                  padding: "16px",
                  backgroundColor: "var(--gray-bg)",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid var(--gray-border)",
                }}
              >
                <div
                  style={{
                    width: "48px",
                    height: "48px",
                    borderRadius: "50%",
                    backgroundColor: "var(--accent)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#FFFFFF",
                    fontSize: "20px",
                    fontWeight: 700,
                    flexShrink: 0,
                  }}
                >
                  {user?.business_name ? user.business_name[0].toUpperCase() : "R"}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h4 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 2px 0", color: "var(--gray-text-primary)" }}>
                    {user?.business_name || "Retail Store"}
                  </h4>
                  <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: 0 }}>
                    {user?.email}
                  </p>
                </div>
                <span
                  className={`badge ${isEmailVerified ? "badge-success" : "badge-warning"}`}
                  style={{ fontSize: "11px", padding: "4px 8px" }}
                >
                  {isEmailVerified ? (
                    <>
                      <CheckCircle2 size={12} /> Verified
                    </>
                  ) : (
                    <>
                      <AlertCircle size={12} /> Unverified
                    </>
                  )}
                </span>
              </div>

              {/* Detail fields */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <Building size={13} style={{ color: "var(--gray-text-muted)" }} />
                    Business Name
                  </label>
                  <input
                    type="text"
                    disabled
                    value={user?.business_name || "N/A"}
                    className="form-input"
                    style={{ backgroundColor: "#F8FAFC", cursor: "default" }}
                  />
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <Mail size={13} style={{ color: "var(--gray-text-muted)" }} />
                    Account Email
                  </label>
                  <input
                    type="text"
                    disabled
                    value={user?.email || "N/A"}
                    className="form-input"
                    style={{ backgroundColor: "#F8FAFC", cursor: "default" }}
                  />
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <Shield size={13} style={{ color: "var(--gray-text-muted)" }} />
                    Account Role
                  </label>
                  <input
                    type="text"
                    disabled
                    value={user?.role || "RETAILER"}
                    className="form-input"
                    style={{ backgroundColor: "#F8FAFC", cursor: "default" }}
                  />
                </div>

                <div className="form-group" style={{ margin: 0 }}>
                  <label className="form-label" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                    <Calendar size={13} style={{ color: "var(--gray-text-muted)" }} />
                    Member Since
                  </label>
                  <input
                    type="text"
                    disabled
                    value={formatDate(user?.created_at)}
                    className="form-input"
                    style={{ backgroundColor: "#F8FAFC", cursor: "default" }}
                  />
                </div>
              </div>

              {/* Retailer Identifier */}
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Retailer System ID</label>
                <div style={{ display: "flex", gap: "8px" }}>
                  <input
                    type="text"
                    disabled
                    value={user?.id || user?._id || "Not assigned"}
                    className="form-input"
                    style={{
                      fontFamily: "var(--font-mono)",
                      fontSize: "13px",
                      backgroundColor: "#F8FAFC",
                      cursor: "default",
                      flex: 1,
                    }}
                  />
                  <button
                    type="button"
                    onClick={handleCopyId}
                    className="btn btn-secondary"
                    style={{ padding: "0 14px", display: "inline-flex", alignItems: "center", gap: "6px" }}
                  >
                    {copiedId ? <Check size={14} style={{ color: "var(--success)" }} /> : <Copy size={14} />}
                    {copiedId ? "Copied" : "Copy"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: STORE PREFERENCES */}
          {activeTab === "store" && (
            <form onSubmit={handleSaveStorePreferences} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Default Forecast Horizon</label>
                <select
                  value={defaultHorizon}
                  onChange={(e) => setDefaultHorizon(e.target.value)}
                  className="form-input"
                  style={{ backgroundColor: "#FFFFFF" }}
                >
                  <option value="7d">7-Day Horizon (Weekly Tactical Forecast)</option>
                  <option value="30d">30-Day Horizon (Monthly Inventory Planning)</option>
                </select>
                <span style={{ fontSize: "12px", color: "var(--gray-text-muted)", marginTop: "4px", display: "block" }}>
                  Sets the initial forecast horizon displayed across product detail telemetry drawers.
                </span>
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Currency Standard</label>
                <input
                  type="text"
                  disabled
                  value="INR (₹) — Indian Rupee"
                  className="form-input"
                  style={{ backgroundColor: "#F8FAFC", cursor: "default" }}
                />
                <span style={{ fontSize: "12px", color: "var(--gray-text-muted)", marginTop: "4px", display: "block" }}>
                  All pricing, margins, and revenue calculations are formatted in Indian Rupees.
                </span>
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">Highlight Opportunities Above Minimum Gain</label>
                <select
                  value={minGainThreshold}
                  onChange={(e) => setMinGainThreshold(e.target.value)}
                  className="form-input"
                  style={{ backgroundColor: "#FFFFFF" }}
                >
                  <option value="100">₹100 Expected Gain</option>
                  <option value="500">₹500 Expected Gain (Default)</option>
                  <option value="1000">₹1,000 Expected Gain</option>
                  <option value="2500">₹2,500 Expected Gain</option>
                </select>
                <span style={{ fontSize: "12px", color: "var(--gray-text-muted)", marginTop: "4px", display: "block" }}>
                  Filters the top pricing recommendations shown in dashboard summaries.
                </span>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "8px" }}>
                <button type="submit" className="btn btn-primary">
                  Save Preferences
                </button>
              </div>
            </form>
          )}

          {/* TAB 3: NOTIFICATION PREFERENCES */}
          {activeTab === "notifications" && (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: "0 0 4px 0" }}>
                Choose which automated alerts are generated and displayed in your notification center:
              </p>

              {[
                {
                  key: "stockoutAlerts",
                  title: "Critical Stockout & Overstock Risks",
                  desc: "Generate alerts when inventory days of cover fall below 7 days or exceed 45 days.",
                  badge: "CRITICAL",
                  badgeClass: "badge-danger",
                },
                {
                  key: "pricingAlerts",
                  title: "High-Gain Pricing Opportunities",
                  desc: "Receive notices when AI dynamic pricing detects revenue expansion opportunities.",
                  badge: "PRICING",
                  badgeClass: "badge-warning",
                },
                {
                  key: "uploadAlerts",
                  title: "Dataset Ingestion & Processing Logs",
                  desc: "Get notified when uploaded CSV files complete validation and ML feature extraction.",
                  badge: "UPLOADS",
                  badgeClass: "badge-success",
                },
                {
                  key: "goalAlerts",
                  title: "Monthly Revenue Milestones",
                  desc: "Track store performance progress against monthly revenue targets.",
                  badge: "MILESTONES",
                  badgeClass: "badge-info",
                },
              ].map((item) => {
                const isEnabled = preferences[item.key] ?? true;
                return (
                  <div
                    key={item.key}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "16px",
                      backgroundColor: isEnabled ? "#FFFFFF" : "#F8FAFC",
                      border: "1px solid var(--gray-border)",
                      borderRadius: "var(--radius-default)",
                      gap: "16px",
                      transition: "background-color 150ms ease",
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                        <h5 style={{ fontSize: "14px", fontWeight: 700, margin: 0, color: "var(--gray-text-primary)" }}>
                          {item.title}
                        </h5>
                        <span className={`badge ${item.badgeClass}`} style={{ fontSize: "9px", padding: "1px 6px" }}>
                          {item.badge}
                        </span>
                      </div>
                      <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0, lineHeight: 1.4 }}>
                        {item.desc}
                      </p>
                    </div>

                    <label
                      style={{
                        position: "relative",
                        display: "inline-block",
                        width: "44px",
                        height: "24px",
                        cursor: "pointer",
                        flexShrink: 0,
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={isEnabled}
                        onChange={(e) => {
                          updatePreferences({ [item.key]: e.target.checked });
                          toast.info(
                            "Preference Updated",
                            `${item.title} ${e.target.checked ? "enabled" : "disabled"}.`
                          );
                        }}
                        style={{ opacity: 0, width: 0, height: 0 }}
                      />
                      <span
                        style={{
                          position: "absolute",
                          inset: 0,
                          backgroundColor: isEnabled ? "var(--accent)" : "#CBD5E1",
                          borderRadius: "9999px",
                          transition: "background-color 200ms ease",
                        }}
                      >
                        <span
                          style={{
                            position: "absolute",
                            top: "2px",
                            left: isEnabled ? "22px" : "2px",
                            width: "20px",
                            height: "20px",
                            backgroundColor: "#FFFFFF",
                            borderRadius: "50%",
                            transition: "left 200ms ease",
                            boxShadow: "0 1px 3px rgba(0,0,0,0.2)",
                          }}
                        />
                      </span>
                    </label>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
