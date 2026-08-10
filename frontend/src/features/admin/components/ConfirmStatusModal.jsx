import React, { useEffect } from "react";
import { AlertTriangle, CheckCircle2, X } from "lucide-react";

export const ConfirmStatusModal = ({
  isOpen,
  onClose,
  onConfirm,
  retailerName,
  currentStatus,
  isLoading,
}) => {
  // Escape key handler
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen && !isLoading) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, isLoading, onClose]);

  if (!isOpen) return null;

  const isDeactivating = currentStatus === true;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(15, 23, 42, 0.65)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: "var(--space-4)",
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget && !isLoading) onClose();
      }}
    >
      <div
        className="card"
        style={{
          width: "100%",
          maxWidth: "480px",
          backgroundColor: "#FFFFFF",
          borderRadius: "var(--radius-lg)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
          overflow: "hidden",
          border: "1px solid var(--gray-border)",
          animation: "modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            padding: "var(--space-5)",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "10px",
                backgroundColor: isDeactivating ? "#FEF2F2" : "#F0FDF4",
                color: isDeactivating ? "var(--error)" : "var(--success)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              {isDeactivating ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
            </div>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>
                {isDeactivating ? "Disable Retailer Account" : "Reactivate Retailer Account"}
              </h3>
              <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                {retailerName || "Retail Store"}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isLoading}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--gray-text-muted)",
              padding: "4px",
              display: "flex",
              alignItems: "center",
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: "var(--space-5)" }}>
          <p style={{ fontSize: "14px", lineHeight: "1.6", color: "var(--gray-text-primary)", margin: 0 }}>
            {isDeactivating ? (
              <>
                Are you sure you want to disable <strong>{retailerName}</strong>? This will immediately revoke their platform session and prevent the retailer from logging in or uploading datasets.
              </>
            ) : (
              <>
                Are you sure you want to reactivate <strong>{retailerName}</strong>? The retailer will regain full access to their dashboard, products, and forecasting pipelines.
              </>
            )}
          </p>

          <div
            style={{
              marginTop: "var(--space-4)",
              padding: "var(--space-3) var(--space-4)",
              backgroundColor: "var(--gray-surface)",
              borderRadius: "var(--radius-default)",
              border: "1px solid var(--gray-border)",
              fontSize: "12px",
              color: "var(--gray-text-muted)",
            }}
          >
            ⚡ <strong>Audit Trail:</strong> This administrative change will be logged in the immutable Platform Activity Log with your admin timestamp.
          </div>
        </div>

        {/* Modal Actions */}
        <div
          style={{
            padding: "var(--space-4) var(--space-5)",
            backgroundColor: "var(--gray-bg)",
            borderTop: "1px solid var(--gray-border)",
            display: "flex",
            justifyContent: "flex-end",
            gap: "var(--space-3)",
          }}
        >
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="btn btn-secondary"
            style={{ height: "38px", fontSize: "13px" }}
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isLoading}
            className={isDeactivating ? "btn btn-danger" : "btn btn-primary"}
            style={{ height: "38px", fontSize: "13px" }}
          >
            {isLoading ? "Updating..." : isDeactivating ? "Disable Account" : "Reactivate Account"}
          </button>
        </div>
      </div>
    </div>
  );
};
