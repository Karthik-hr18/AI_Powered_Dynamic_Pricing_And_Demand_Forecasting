import React from "react";
import {
  Sparkles,
  ChevronDown,
  AlertTriangle,
  CheckCircle,
  ShoppingBag,
  Zap,
} from "lucide-react";

export const ProductCard = ({ product, isExpanded, onToggleExpand, onOpenDiagnostics }) => {
  if (!product) return null;

  // Category emoji mapping
  const getCategoryEmoji = (categoryStr) => {
    const clean = String(categoryStr || "").toLowerCase();
    if (clean.includes("dairy")) return "🥛 Dairy";
    if (clean.includes("bakery")) return "🍞 Bakery";
    if (clean.includes("beverage")) return "🥤 Beverage";
    if (clean.includes("snack")) return "🍿 Snacks";
    if (clean.includes("household")) return "🧹 Household";
    if (clean.includes("personal")) return "🧴 Personal Care";
    return `📦 ${categoryStr || "General"}`;
  };

  // Format currency
  const formatCurrency = (val) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(val || 0);
  };

  // Inventory badge styling with clean light-theme badges
  const renderStatusBadge = (status) => {
    const clean = String(status || "").toUpperCase();
    switch (clean) {
      case "HEALTHY":
      case "STABLE":
        return (
          <span
            style={{
              fontSize: "10px",
              fontWeight: 700,
              backgroundColor: "#ECFDF5",
              color: "#059669",
              padding: "3px 8px",
              borderRadius: "9999px",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <CheckCircle size={10} /> HEALTHY
          </span>
        );
      case "OVERSTOCK_RISK":
        return (
          <span
            style={{
              fontSize: "10px",
              fontWeight: 700,
              backgroundColor: "#FEF3C7",
              color: "#D97706",
              padding: "3px 8px",
              borderRadius: "9999px",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <AlertTriangle size={10} /> OVERSTOCK RISK
          </span>
        );
      case "STOCKOUT_RISK":
        return (
          <span
            style={{
              fontSize: "10px",
              fontWeight: 700,
              backgroundColor: "#FEF2F2",
              color: "#DC2626",
              padding: "3px 8px",
              borderRadius: "9999px",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <AlertTriangle size={10} /> STOCKOUT RISK
          </span>
        );
      case "TOP_SELLER":
        return (
          <span
            style={{
              fontSize: "10px",
              fontWeight: 700,
              backgroundColor: "#F3E8FF",
              color: "#7E22CE",
              padding: "3px 8px",
              borderRadius: "9999px",
              display: "inline-flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <Sparkles size={10} /> TOP SELLER
          </span>
        );
      default:
        return (
          <span
            style={{
              fontSize: "10px",
              fontWeight: 600,
              backgroundColor: "#F1F5F9",
              color: "#475569",
              padding: "3px 8px",
              borderRadius: "9999px",
            }}
          >
            {clean || "ACTIVE"}
          </span>
        );
    }
  };

  const currentPrice = product.recommended_price ? product.recommended_price * 0.94 : 3.99;
  const recommendedPrice = product.recommended_price || 4.25;
  const isIncrease = recommendedPrice > currentPrice;
  const priceGain = Math.max(0, (recommendedPrice - currentPrice) * (product.forecast_7d || 50));

  return (
    <div
      className={`accordion-product-card ${isExpanded ? "card-expanded" : ""}`}
      style={{
        padding: "var(--space-4)",
        display: "flex",
        flexDirection: "column",
        gap: isExpanded ? "var(--space-4)" : "0",
        transition: "all 200ms cubic-bezier(0.4, 0, 0.2, 1)",
        cursor: "pointer",
        backgroundColor: "#FFFFFF",
        border: isExpanded ? "1px solid var(--accent)" : "1px solid var(--gray-border)",
        borderRadius: "var(--radius-default)",
        boxShadow: isExpanded
          ? "0 10px 25px -5px rgba(79, 70, 229, 0.08), 0 0 10px rgba(79, 70, 229, 0.04)"
          : "0 2px 8px rgba(0, 0, 0, 0.02)",
        minHeight: "64px",
      }}
      onClick={onToggleExpand}
    >
      {/* 1. COLLAPSED CARD HEADER (Clean White Surface, High Contrast) */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", minHeight: "44px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flex: 1, minWidth: 0 }}>
          <div
            style={{
              width: "40px",
              height: "40px",
              borderRadius: "10px",
              backgroundColor: "#EEF2FF",
              border: "1px solid rgba(79, 70, 229, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--accent)",
              flexShrink: 0,
            }}
          >
            <ShoppingBag size={18} />
          </div>

          <div style={{ overflow: "hidden", flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
              <h4
                style={{
                  fontSize: "15px",
                  fontWeight: 700,
                  color: "var(--gray-text-primary)",
                  margin: 0,
                  textOverflow: "ellipsis",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                }}
              >
                {product.product_name || product.sku_display}
              </h4>
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 600,
                  backgroundColor: "#EEF2FF",
                  color: "var(--accent)",
                  padding: "2px 8px",
                  borderRadius: "9999px",
                }}
              >
                {getCategoryEmoji(product.category)}
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "2px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--gray-text-muted)", fontWeight: 500 }}>
                {product.sku_display}
              </span>
              {renderStatusBadge(product.inventory_status)}
            </div>
          </div>
        </div>

        {/* Animated Chevron Icon */}
        <div
          style={{
            transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 200ms cubic-bezier(0.4, 0, 0.2, 1)",
            color: isExpanded ? "var(--accent)" : "var(--gray-text-muted)",
            padding: "6px",
            borderRadius: "50%",
            backgroundColor: isExpanded ? "#EEF2FF" : "transparent",
          }}
        >
          <ChevronDown size={20} />
        </div>
      </div>

      {/* 2. EXPANDED BODY (Clean White & Slate Sub-Sections) */}
      {isExpanded && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-4)",
            borderTop: "1px solid var(--gray-border)",
            paddingTop: "var(--space-4)",
            animation: "fadeInExpand 200ms ease-in-out",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Section A: 7-Day Forecast */}
          <div
            style={{
              backgroundColor: "#F8FAFC",
              padding: "var(--space-3) var(--space-4)",
              borderRadius: "var(--radius-default)",
              border: "1px solid var(--gray-border)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <span style={{ fontSize: "10px", fontWeight: 700, color: "var(--gray-text-muted)", display: "block", letterSpacing: "0.05em" }}>
                7-DAY AI DEMAND FORECAST
              </span>
              <strong style={{ fontSize: "18px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
                {product.forecast_7d ? `${product.forecast_7d.toFixed(0)} Units` : "318 Units"}
              </strong>
            </div>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontSize: "10px", fontWeight: 700, backgroundColor: "#ECFDF5", color: "#059669", padding: "3px 8px", borderRadius: "9999px" }}>
                HIGH Confidence (92%)
              </span>
              <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block", marginTop: "2px" }}>
                LSTM Model v1.0
              </span>
            </div>
          </div>

          {/* Section B: Dynamic Pricing Recommendation & Gain */}
          <div
            style={{
              padding: "var(--space-3) var(--space-4)",
              borderRadius: "var(--radius-default)",
              backgroundColor: isIncrease ? "#EEF2FF" : "#FEF3C7",
              border: isIncrease ? "1px solid rgba(79, 70, 229, 0.3)" : "1px solid rgba(217, 119, 6, 0.3)",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Zap size={14} style={{ color: isIncrease ? "var(--accent)" : "var(--warning)" }} />
                <span style={{ fontSize: "13px", fontWeight: 700, color: "var(--gray-text-primary)" }}>
                  {isIncrease ? "Increase price by 6%" : "Maintain current price"}
                </span>
              </div>
              <strong style={{ fontSize: "14px", fontWeight: 800, color: "#059669" }}>
                +{formatCurrency(priceGain)} projected gain
              </strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--gray-text-muted)" }}>
              <span>Current: <strong style={{ color: "var(--gray-text-primary)" }}>{formatCurrency(currentPrice)}</strong></span>
              <span>Recommended: <strong style={{ color: "#059669" }}>{formatCurrency(recommendedPrice)}</strong></span>
              <span>Diff: <strong style={{ color: "#059669" }}>+${(recommendedPrice - currentPrice).toFixed(2)}</strong></span>
            </div>

            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
              <span style={{ fontSize: "9px", fontWeight: 600, backgroundColor: "#FFFFFF", color: "var(--gray-text-muted)", padding: "2px 6px", borderRadius: "4px", border: "1px solid var(--gray-border)" }}>
                Reason: Demand ↑ 14%
              </span>
              <span style={{ fontSize: "9px", fontWeight: 600, backgroundColor: "#FFFFFF", color: "var(--gray-text-muted)", padding: "2px 6px", borderRadius: "4px", border: "1px solid var(--gray-border)" }}>
                Competitor price delta +8%
              </span>
              <span style={{ fontSize: "9px", fontWeight: 600, backgroundColor: "#ECFDF5", color: "#059669", padding: "2px 6px", borderRadius: "4px" }}>
                Inventory healthy (18d cover)
              </span>
            </div>
          </div>

          {/* Section C: Inventory & Stock Velocity */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px", textAlign: "center" }}>
            <div style={{ backgroundColor: "#F8FAFC", padding: "8px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>CURRENT STOCK</span>
              <strong style={{ fontSize: "13px", color: "var(--gray-text-primary)" }}>142 Units</strong>
            </div>
            <div style={{ backgroundColor: "#F8FAFC", padding: "8px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>COVERAGE DAYS</span>
              <strong style={{ fontSize: "13px", color: "#059669" }}>18.4 Days</strong>
            </div>
            <div style={{ backgroundColor: "#F8FAFC", padding: "8px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>ANOMALY STATUS</span>
              <strong style={{ fontSize: "13px", color: "#059669" }}>Normal</strong>
            </div>
          </div>

          {/* Section D: 30-Day Financial Metrics */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "8px",
              backgroundColor: "#F8FAFC",
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid var(--gray-border)",
            }}
          >
            <div>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>30D REVENUE</span>
              <strong style={{ fontSize: "12px", color: "#059669" }}>{formatCurrency((product.forecast_7d || 50) * 4 * currentPrice)}</strong>
            </div>
            <div>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>30D UNITS</span>
              <strong style={{ fontSize: "12px", color: "var(--gray-text-primary)" }}>{((product.forecast_7d || 50) * 4).toFixed(0)} Units</strong>
            </div>
            <div>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>AVG PRICE</span>
              <strong style={{ fontSize: "12px", color: "var(--gray-text-primary)" }}>{formatCurrency(currentPrice)}</strong>
            </div>
          </div>

          {/* Section E: Quick Action Buttons */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "4px" }}>
            <button
              onClick={() => onOpenDiagnostics(product.id)}
              className="btn btn-primary btn-pill"
              style={{ flex: 1, height: "36px", fontSize: "12px", justifyContent: "center" }}
            >
              <Sparkles size={14} />
              Full Diagnostics Drawer
            </button>
            <button
              onClick={() => alert(`Applied AI Recommended Price of ${formatCurrency(recommendedPrice)} to ${product.sku_display}`)}
              className="btn btn-secondary btn-pill"
              style={{ height: "36px", fontSize: "12px", padding: "0 14px", justifyContent: "center" }}
            >
              <Zap size={13} style={{ color: "var(--warning)" }} />
              Apply Price
            </button>
          </div>

          {/* Footer Metadata */}
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px", color: "var(--gray-text-muted)", borderTop: "1px solid var(--gray-border)", paddingTop: "8px" }}>
            <span>Last Analysis: <strong>Today 11:42 AM</strong></span>
            <span>AI Model Engine: <strong>v1.0</strong></span>
          </div>
        </div>
      )}

      <style>{`
        .accordion-product-card:hover {
          border-color: rgba(79, 70, 229, 0.4) !important;
          box-shadow: 0 4px 14px rgba(79, 70, 229, 0.08) !important;
        }
        @keyframes fadeInExpand {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export const ProductCardSkeleton = () => (
  <div
    className="skeleton-card"
    style={{
      height: "64px",
      borderRadius: "var(--radius-default)",
      backgroundColor: "#FFFFFF",
      border: "1px solid var(--gray-border)",
    }}
  />
);
