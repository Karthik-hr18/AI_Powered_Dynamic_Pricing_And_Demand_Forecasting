import React, { useEffect } from "react";
import {
  X,
  ShieldCheck,
  AlertTriangle,
  Activity,
  CheckCircle2,
  TrendingUp,
  Package,
  Sparkles,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { formatCurrency } from "../../../shared/utils/formatters";

export const BusinessHealthModal = ({
  isOpen,
  onClose,
  businessHealth,
  criticalRisks = [],
  topOpportunities = [],
  inventoryHealth,
  kpis,
}) => {
  const navigate = useNavigate();

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

  if (!isOpen) return null;

  const score = businessHealth?.score ?? 85;
  const rating = businessHealth?.rating ?? "Good";
  const isNeedsAttention = rating.toLowerCase().includes("attention") || score < 70;
  const isGood = !isNeedsAttention && (rating.toLowerCase().includes("good") || score < 88);
  const isExcellent = score >= 88;

  const themeColor = isNeedsAttention ? "#EF4444" : isGood ? "#D97706" : "#10B981";
  const themeBg = isNeedsAttention ? "#FEF2F2" : isGood ? "#FFFBEB" : "#ECFDF5";
  const themeBorder = isNeedsAttention ? "#FECACA" : isGood ? "#FDE68A" : "#A7F3D0";

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container"
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: "580px",
          width: "100%",
          padding: 0,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          maxHeight: "90vh",
        }}
      >
        {/* Header */}
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
                backgroundColor: themeBg,
                border: `1px solid ${themeBorder}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: themeColor,
              }}
            >
              {isNeedsAttention ? (
                <AlertTriangle size={20} />
              ) : isGood ? (
                <Activity size={20} />
              ) : (
                <CheckCircle2 size={20} />
              )}
            </div>
            <div>
              <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0, color: "var(--gray-text-primary)" }}>
                Business Health Diagnostics
              </h3>
              <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0 }}>
                Composite score breakdown and recovery action plan
              </p>
            </div>
          </div>
          <button onClick={onClose} className="modal-close-btn" style={{ position: "static" }}>
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: "24px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Top Score Banner */}
          <div
            style={{
              padding: "16px 20px",
              backgroundColor: themeBg,
              border: `1px solid ${themeBorder}`,
              borderRadius: "var(--radius-card)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div>
              <span style={{ fontSize: "11px", fontWeight: 700, color: themeColor, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Overall Store Rating
              </span>
              <h2 style={{ fontSize: "24px", fontWeight: 800, margin: "2px 0 0 0", color: "var(--gray-text-primary)" }}>
                {score} <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--gray-text-muted)" }}>/ 100</span>
              </h2>
              <span style={{ fontSize: "13px", fontWeight: 700, color: themeColor }}>
                {rating}
              </span>
            </div>

            {/* Score Progress Bar visual */}
            <div style={{ flex: 1, maxWidth: "200px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>
                <span>Target: 90+</span>
                <span>{score}%</span>
              </div>
              <div style={{ width: "100%", height: "8px", backgroundColor: "#E2E8F0", borderRadius: "9999px", overflow: "hidden" }}>
                <div
                  style={{
                    width: `${score}%`,
                    height: "100%",
                    backgroundColor: themeColor,
                    borderRadius: "9999px",
                    transition: "width 500ms ease",
                  }}
                />
              </div>
            </div>
          </div>

          {/* Actionable Steps to Restore / Boost Score */}
          <div>
            <h4 style={{ fontSize: "14px", fontWeight: 700, color: "var(--gray-text-primary)", margin: "0 0 12px 0" }}>
              Recommended Actions to Maximize Score
            </h4>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {/* Step 1: Stockout Risks */}
              <div
                style={{
                  padding: "12px 16px",
                  border: "1px solid var(--gray-border)",
                  borderRadius: "8px",
                  backgroundColor: "#FFFFFF",
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  gap: "12px",
                }}
              >
                <div style={{ display: "flex", gap: "10px" }}>
                  <Package size={16} style={{ color: criticalRisks.length > 0 ? "#EF4444" : "#10B981", marginTop: "2px" }} />
                  <div>
                    <strong style={{ fontSize: "13px", color: "var(--gray-text-primary)", display: "block" }}>
                      {criticalRisks.length > 0
                        ? `Restock ${criticalRisks.length} Critical Inventory SKUs`
                        : "Inventory Stock Levels are Healthy"}
                    </strong>
                    <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: "2px 0 0 0" }}>
                      {criticalRisks.length > 0
                        ? "Items with days of cover under 7 days risk immediate stockouts."
                        : "All tracked SKUs have sufficient buffer against forecast demand."}
                    </p>
                  </div>
                </div>
                {criticalRisks.length > 0 && (
                  <button
                    onClick={() => {
                      onClose();
                      navigate("/products?status=RISK");
                    }}
                    className="btn btn-secondary"
                    style={{ fontSize: "11px", padding: "4px 10px", flexShrink: 0, display: "inline-flex", alignItems: "center", gap: "4px" }}
                  >
                    View Risks <ArrowRight size={12} />
                  </button>
                )}
              </div>

              {/* Step 2: Pricing Opportunities */}
              <div
                style={{
                  padding: "12px 16px",
                  border: "1px solid var(--gray-border)",
                  borderRadius: "8px",
                  backgroundColor: "#FFFFFF",
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  gap: "12px",
                }}
              >
                <div style={{ display: "flex", gap: "10px" }}>
                  <Sparkles size={16} style={{ color: "var(--accent)", marginTop: "2px" }} />
                  <div>
                    <strong style={{ fontSize: "13px", color: "var(--gray-text-primary)", display: "block" }}>
                      {topOpportunities.length > 0
                        ? `Adopt ${topOpportunities.length} Dynamic Pricing Shifts`
                        : "Prices are Optimized"}
                    </strong>
                    <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: "2px 0 0 0" }}>
                      {topOpportunities.length > 0
                        ? `Capture up to +${formatCurrency(kpis?.potential_revenue_gain || 0)} in projected gross margin gain.`
                        : "Current price points are aligned with demand elasticity."}
                    </p>
                  </div>
                </div>
                {topOpportunities.length > 0 && (
                  <button
                    onClick={() => {
                      onClose();
                      navigate("/products");
                    }}
                    className="btn btn-primary"
                    style={{ fontSize: "11px", padding: "4px 10px", flexShrink: 0, display: "inline-flex", alignItems: "center", gap: "4px" }}
                  >
                    Apply Pricing <ArrowRight size={12} />
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Inventory Distribution Overview */}
          {inventoryHealth && (
            <div style={{ backgroundColor: "var(--gray-bg)", padding: "14px 16px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--gray-text-primary)", display: "block", marginBottom: "8px" }}>
                Catalog Stock Health Breakdown
              </span>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", textAlign: "center" }}>
                <div style={{ backgroundColor: "#FFFFFF", padding: "8px", borderRadius: "6px", border: "1px solid var(--gray-border)" }}>
                  <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>Healthy</span>
                  <strong style={{ fontSize: "15px", color: "#10B981" }}>{inventoryHealth.healthy_pct}%</strong>
                </div>
                <div style={{ backgroundColor: "#FFFFFF", padding: "8px", borderRadius: "6px", border: "1px solid var(--gray-border)" }}>
                  <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>At Risk</span>
                  <strong style={{ fontSize: "15px", color: "#D97706" }}>{inventoryHealth.risk_pct}%</strong>
                </div>
                <div style={{ backgroundColor: "#FFFFFF", padding: "8px", borderRadius: "6px", border: "1px solid var(--gray-border)" }}>
                  <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>Critical</span>
                  <strong style={{ fontSize: "15px", color: "#EF4444" }}>{inventoryHealth.critical_pct}%</strong>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "12px 24px",
            borderTop: "1px solid var(--gray-border)",
            backgroundColor: "#F8FAFC",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <button onClick={onClose} className="btn btn-secondary">
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};
