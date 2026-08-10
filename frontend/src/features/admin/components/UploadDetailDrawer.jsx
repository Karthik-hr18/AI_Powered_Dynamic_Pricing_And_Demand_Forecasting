import React, { useEffect } from "react";
import {
  X,
  Database,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Building,
  FileSpreadsheet,
  Layers,
  Copy,
} from "lucide-react";
import { formatInteger } from "../../../shared/utils/formatters";
import { useToast } from "../../../shared/hooks/useToast";

export const UploadDetailDrawer = ({
  isOpen,
  onClose,
  upload,
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

  if (!isOpen || !upload) return null;

  const copyUploadId = () => {
    navigator.clipboard.writeText(upload.upload_id);
    toast.success("Copied to Clipboard", "Upload ID copied successfully.");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return "0 KB";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const isFailed = upload.status.includes("FAILED") || upload.status.includes("REJECTED");
  const isCompleted = upload.status.includes("COMPLETED");

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 9990,
        display: "flex",
        justifyContent: "flex-end",
      }}
    >
      {/* Backdrop */}
      <div
        className="slide-drawer-backdrop"
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(15, 23, 42, 0.5)",
          backdropFilter: "blur(2px)",
        }}
        onClick={onClose}
      />

      {/* Drawer Content */}
      <div
        className="slide-drawer"
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "540px",
          height: "100%",
          backgroundColor: "#FFFFFF",
          boxShadow: "-10px 0 25px -5px rgba(0, 0, 0, 0.15)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          animation: "slideInRight 0.25s cubic-bezier(0.16, 1, 0.3, 1)",
          zIndex: 9991,
        }}
      >
        {/* Header */}
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
                backgroundColor: isCompleted
                  ? "#F0FDF4"
                  : isFailed
                  ? "#FEF2F2"
                  : "#EFF6FF",
                color: isCompleted
                  ? "var(--success)"
                  : isFailed
                  ? "var(--error)"
                  : "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <FileSpreadsheet size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: "16px", fontWeight: 800, margin: 0, color: "var(--gray-text-primary)" }}>
                {upload.original_filename}
              </h2>
              <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                {upload.retailer_business_name} ({upload.retailer_email})
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
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "var(--space-5)" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
            {/* Status Header Bar */}
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
                <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: 700, color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                  Ingestion Status
                </div>
                <span
                  className={`badge ${
                    isCompleted
                      ? "badge-success"
                      : isFailed
                      ? "badge-danger"
                      : "badge-warning"
                  }`}
                  style={{ fontSize: "12px", fontWeight: 700 }}
                >
                  {upload.status}
                </span>
              </div>

              {upload.duration_seconds !== null && upload.duration_seconds !== undefined && (
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: "11px", textTransform: "uppercase", fontWeight: 700, color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                    Total Processing Time
                  </div>
                  <strong style={{ fontSize: "14px", color: "var(--gray-text-primary)" }}>
                    {upload.duration_seconds}s
                  </strong>
                </div>
              )}
            </div>

            {/* Error Forensic Box (If Failed) */}
            {isFailed && (
              <div
                style={{
                  padding: "var(--space-4)",
                  backgroundColor: "#FEF2F2",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid rgba(220, 38, 38, 0.2)",
                  color: "#991B1B",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 700, fontSize: "13px", marginBottom: "6px" }}>
                  <AlertTriangle size={16} />
                  Safe Operational Failure Reason
                </div>
                <p style={{ fontSize: "13px", lineHeight: "1.5", margin: 0, color: "#B91C1C" }}>
                  {upload.error_reason_safe || "CSV processing failed during dataset validation or formatting checks."}
                </p>
                {upload.failed_stage && (
                  <div style={{ marginTop: "8px", fontSize: "11px", color: "#7F1D1D" }}>
                    Failed at pipeline phase: <strong>{upload.failed_stage}</strong>
                  </div>
                )}
              </div>
            )}

            {/* Ingestion Metrics 3-Card Grid */}
            <div>
              <h4 style={{ fontSize: "13px", fontWeight: 700, textTransform: "uppercase", color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "var(--space-3)" }}>
                Ingestion Metrics
              </h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-3)" }}>
                <div className="card" style={{ padding: "var(--space-3)", textAlign: "center" }}>
                  <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                    File Size
                  </div>
                  <div style={{ fontSize: "16px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
                    {formatFileSize(upload.file_size_bytes)}
                  </div>
                </div>
                <div className="card" style={{ padding: "var(--space-3)", textAlign: "center" }}>
                  <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                    Rows Ingested
                  </div>
                  <div style={{ fontSize: "16px", fontWeight: 800, color: "var(--success)" }}>
                    {formatInteger(upload.rows_ingested || upload.row_count || 0)}
                  </div>
                </div>
                <div className="card" style={{ padding: "var(--space-3)", textAlign: "center" }}>
                  <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                    Rows Rejected
                  </div>
                  <div style={{ fontSize: "16px", fontWeight: 800, color: upload.rows_rejected > 0 ? "var(--error)" : "var(--gray-text-muted)" }}>
                    {formatInteger(upload.rows_rejected)}
                  </div>
                </div>
              </div>
            </div>

            {/* Pipeline Stage Information */}
            <div>
              <h4 style={{ fontSize: "13px", fontWeight: 700, textTransform: "uppercase", color: "var(--gray-text-muted)", letterSpacing: "0.05em", marginBottom: "var(--space-3)" }}>
                Operational Pipeline Details
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)", fontSize: "13px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--gray-border)" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Upload Job ID:</span>
                  <button
                    onClick={copyUploadId}
                    style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "6px", fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--accent)" }}
                  >
                    <span>{upload.upload_id}</span>
                    <Copy size={13} />
                  </button>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--gray-border)" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Current Pipeline Stage:</span>
                  <strong style={{ color: "var(--gray-text-primary)" }}>{upload.current_stage || "COMPLETED"}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--gray-border)" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Received Timestamp:</span>
                  <strong style={{ color: "var(--gray-text-primary)" }}>{formatDate(upload.created_at)}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Completed Timestamp:</span>
                  <strong style={{ color: "var(--gray-text-primary)" }}>{formatDate(upload.processing_completed_at)}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
