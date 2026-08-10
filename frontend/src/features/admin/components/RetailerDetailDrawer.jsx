import React, { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  X,
  Building,
  Mail,
  Calendar,
  Clock,
  Database,
  ShoppingBag,
  TrendingUp,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  FileText,
  UserCheck,
  UserX,
  Copy,
  ExternalLink,
  Circle,
} from "lucide-react";
import { apiClient } from "../../../shared/apiClient";
import { formatInteger, formatRupee } from "../../../shared/utils/formatters";
import { useToast } from "../../../shared/hooks/useToast";

export const RetailerDetailDrawer = ({
  isOpen,
  onClose,
  retailerId,
  onToggleStatus,
}) => {
  const toast = useToast();

  // Escape key handler
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  // Fetch deep profile for this retailer
  const { data: detailData, isLoading, error } = useQuery({
    queryKey: ["adminRetailerDetail", retailerId],
    queryFn: async () => {
      if (!retailerId) return null;
      const res = await apiClient.get(`admin/retailers/${retailerId}/details`);
      return res.data;
    },
    enabled: isOpen && !!retailerId,
  });

  if (!isOpen) return null;

  const retailer = detailData?.retailer;
  const uploads = detailData?.recent_uploads || [];
  const activity = detailData?.recent_activity || [];

  const copyRetailerId = () => {
    if (retailer?.id) {
      navigator.clipboard.writeText(String(retailer.id));
      toast.success("Copied to Clipboard", "Retailer ID copied successfully.");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        right: 0,
        bottom: 0,
        width: "100%",
        maxWidth: "560px",
        zIndex: 9990,
        display: "flex",
        flexDirection: "column",
        backgroundColor: "var(--gray-surface, #F8FAFC)",
        boxShadow: "-4px 0 24px rgba(0, 0, 0, 0.12), -1px 0 0 var(--gray-border, #E2E8F0)",
        animation: "slideInRight 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
        overflow: "hidden",
      }}
    >
        {/* Drawer Header */}
        <div
          style={{
            padding: "var(--space-5)",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            backgroundColor: "var(--gray-surface)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "10px",
                backgroundColor: "rgba(79, 70, 229, 0.1)",
                color: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 800,
                fontSize: "16px",
              }}
            >
              {retailer?.business_name ? retailer.business_name.charAt(0).toUpperCase() : "R"}
            </div>
            <div>
              <h2 style={{ fontSize: "17px", fontWeight: 800, margin: 0, color: "var(--gray-text-primary)" }}>
                {retailer?.business_name || "Retailer Profile"}
              </h2>
              <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                {retailer?.email}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--gray-text-muted)",
              padding: "6px",
              borderRadius: "var(--radius-default)",
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Drawer Body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "var(--space-5)" }}>
          {isLoading ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
              <div className="skeleton-card" style={{ height: "80px" }} />
              <div className="skeleton-card" style={{ height: "140px" }} />
              <div className="skeleton-card" style={{ height: "200px" }} />
            </div>
          ) : error || !retailer ? (
            <div className="badge badge-danger" style={{ width: "100%", padding: "var(--space-4)" }}>
              Failed to load retailer profile details.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
              {/* Account Status & Identity Bar */}
              <div
                style={{
                  padding: "var(--space-4)",
                  backgroundColor: "var(--gray-surface)",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid var(--gray-border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <div>
                  <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: 700, color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "4px" }}>
                    Account Status
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                    <span
                      className={`badge ${retailer.is_active ? "badge-success" : "badge-danger"}`}
                      style={{ fontSize: "12px", fontWeight: 700, display: "inline-flex", alignItems: "center", gap: "5px" }}
                    >
                      <Circle size={7} fill="currentColor" />
                      {retailer.is_active ? "Active Account" : "Disabled Account"}
                    </span>
                    {retailer.is_email_verified && (
                      <span className="badge badge-info" style={{ fontSize: "11px" }}>
                        Verified
                      </span>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => onToggleStatus(retailer)}
                  className={`btn ${retailer.is_active ? "btn-danger" : "btn-primary"}`}
                  style={{ height: "34px", fontSize: "12px" }}
                >
                  {retailer.is_active ? <UserX size={14} /> : <UserCheck size={14} />}
                  {retailer.is_active ? "Disable Account" : "Reactivate"}
                </button>
              </div>

              {/* Usage Metrics 3-Card Grid */}
              <div>
                <h4 style={{ fontSize: "13px", fontWeight: 700, textTransform: "uppercase", color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "var(--space-3)" }}>
                  Data Footprint
                </h4>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-3)" }}>
                  <div className="card" style={{ padding: "var(--space-3)", textAlign: "center" }}>
                    <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                      Datasets
                    </div>
                    <div style={{ fontSize: "20px", fontWeight: 800, color: "var(--accent)" }}>
                      {formatInteger(retailer.dataset_count)}
                    </div>
                  </div>
                  <div className="card" style={{ padding: "var(--space-3)", textAlign: "center" }}>
                    <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                      Sales Records
                    </div>
                    <div style={{ fontSize: "20px", fontWeight: 800, color: "var(--success)" }}>
                      {formatInteger(retailer.sales_record_count)}
                    </div>
                  </div>
                  <div className="card" style={{ padding: "var(--space-3)", textAlign: "center" }}>
                    <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                      SKU Catalog
                    </div>
                    <div style={{ fontSize: "20px", fontWeight: 800, color: "var(--purple)" }}>
                      {formatInteger(retailer.product_count)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Retailer Details Metadata List */}
              <div>
                <h4 style={{ fontSize: "13px", fontWeight: 700, textTransform: "uppercase", color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "var(--space-3)" }}>
                  Account Metadata
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)", fontSize: "13px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--gray-border)" }}>
                    <span style={{ color: "var(--gray-text-muted)" }}>Retailer ID:</span>
                    <button
                      onClick={copyRetailerId}
                      style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "6px", fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--accent)" }}
                    >
                      <span>{String(retailer.id).substring(0, 16)}...</span>
                      <Copy size={13} />
                    </button>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--gray-border)" }}>
                    <span style={{ color: "var(--gray-text-muted)" }}>Registration Date:</span>
                    <strong style={{ color: "var(--gray-text-primary)" }}>{formatDate(retailer.created_at)}</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--gray-border)" }}>
                    <span style={{ color: "var(--gray-text-muted)" }}>Last Active Timestamp:</span>
                    <strong style={{ color: "var(--gray-text-primary)" }}>{formatDate(retailer.last_active_at)}</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
                    <span style={{ color: "var(--gray-text-muted)" }}>Latest Upload File:</span>
                    <strong style={{ color: "var(--gray-text-primary)" }}>{retailer.last_upload_filename || "None"}</strong>
                  </div>
                </div>
              </div>

              {/* Uploads History */}
              <div>
                <h4 style={{ fontSize: "13px", fontWeight: 700, textTransform: "uppercase", color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "var(--space-3)" }}>
                  Recent Dataset Ingestions
                </h4>
                {uploads.length === 0 ? (
                  <div style={{ padding: "var(--space-4)", textAlign: "center", color: "var(--gray-text-muted)", fontSize: "13px", backgroundColor: "var(--gray-surface)", borderRadius: "var(--radius-default)" }}>
                    No dataset uploads recorded for this retailer.
                  </div>
                ) : (
                  <div className="table-responsive">
                    <table className="table" style={{ fontSize: "12px" }}>
                      <thead>
                        <tr>
                          <th>Filename</th>
                          <th>Rows</th>
                          <th>Status</th>
                          <th style={{ textAlign: "right" }}>Uploaded</th>
                        </tr>
                      </thead>
                      <tbody>
                        {uploads.map((u) => (
                          <tr key={u.upload_id}>
                            <td style={{ fontWeight: 600 }}>{u.filename}</td>
                            <td>{formatInteger(u.rows_ingested || 0)}</td>
                            <td>
                              <span
                                className={`badge ${
                                  u.status.includes("COMPLETED")
                                    ? "badge-success"
                                    : u.status.includes("FAILED") || u.status.includes("REJECTED")
                                    ? "badge-danger"
                                    : "badge-warning"
                                }`}
                                style={{ fontSize: "10px" }}
                              >
                                {u.status}
                              </span>
                            </td>
                            <td style={{ textAlign: "right", color: "var(--gray-text-muted)" }}>
                              {new Date(u.created_at).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Recent Retailer Activity Stream */}
              {activity.length > 0 && (
                <div>
                  <h4 style={{ fontSize: "13px", fontWeight: 700, textTransform: "uppercase", color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "var(--space-3)" }}>
                    Recent Activity Events
                  </h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                    {activity.map((ev) => (
                      <div
                        key={ev.id}
                        style={{
                          padding: "var(--space-3)",
                          backgroundColor: "var(--gray-surface)",
                          borderRadius: "var(--radius-default)",
                          border: "1px solid var(--gray-border)",
                          fontSize: "12px",
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                          <span style={{ fontWeight: 700, color: "var(--accent)" }}>{ev.action}</span>
                          <span style={{ color: "var(--gray-text-muted)" }}>{formatDate(ev.timestamp)}</span>
                        </div>
                        <div style={{ color: "var(--gray-text-primary)" }}>{ev.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
    </div>
  );
};
