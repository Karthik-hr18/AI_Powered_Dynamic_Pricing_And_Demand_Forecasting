import React from "react";
import {
  Sparkles,
  TrendingUp,
  Package,
  DollarSign,
  ChevronDown,
  AlertTriangle,
  CheckCircle,
  Eye,
  ShoppingBag,
  FileText,
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

  // Inventory badge styling
  const renderStatusBadge = (status) => {
    const clean = String(status || "").toUpperCase();
    switch (clean) {
      case "HEALTHY":
      case "STABLE":
        return <span className="badge badge-success" style={{ fontSize: "10px" }}><CheckCircle size={10} /> HEALTHY</span>;
      case "OVERSTOCK_RISK":
        return <span className="badge badge-warning" style={{ fontSize: "10px" }}><AlertTriangle size={10} /> OVERSTOCK RISK</span>;
      case "STOCKOUT_RISK":
        return <span className="badge badge-danger" style={{ fontSize: "10px" }}><AlertTriangle size={10} /> STOCKOUT RISK</span>;
      case "TOP_SELLER":
        return <span className="badge badge-purple" style={{ fontSize: "10px" }}><Sparkles size={10} /> TOP SELLER</span>;
      default:
        return <span className="badge badge-info" style={{ fontSize: "10px" }}>{clean || "ACTIVE"}</span>;
    }
  };

  const currentPrice = product.recommended_price ? product.recommended_price * 0.94 : 3.99;
  const recommendedPrice = product.recommended_price || 4.25;
  const isIncrease = recommendedPrice > currentPrice;
  const priceGain = Math.max(0, (recommendedPrice - currentPrice) * (product.forecast_7d || 50));

  return (
    <div
      className={`card card-interactive accordion-product-card ${isExpanded ? "card-expanded" : ""}`}
      style={{
        padding: "var(--space-4)",
        display: "flex",
        flexDirection: "column",
        gap: isExpanded ? "var(--space-4)" : "0",
        transition: "all 300ms cubic-bezier(0.4, 0, 0.2, 1)",
        cursor: "pointer",
        background: isExpanded
          ? "linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%)"
          : "rgba(30, 41, 59, 0.7)",
        borderColor: isExpanded ? "rgba(99, 102, 241, 0.5)" : "var(--gray-border)",
        boxShadow: isExpanded ? "0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 0 15px rgba(99, 102, 241, 0.15)" : "none",
        minHeight: "64px",
      }}
      onClick={onToggleExpand}
    >
      {/* 1. COLLAPSED CARD HEADER (Always visible, compact, tap target >= 48px) */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "12px", minHeight: "44px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flex: 1, minWidth: 0 }}>
          <div
            style={{
              width: "38px",
              height: "38px",
              borderRadius: "10px",
              backgroundColor: "rgba(99, 102, 241, 0.15)",
              border: "1px solid rgba(99, 102, 241, 0.3)",
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
                  color: "#FFFFFF",
                  margin: 0,
                  textOverflow: "ellipsis",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                }}
              >
                {product.product_name || product.sku_display}
              </h4>
              <span className="badge badge-purple" style={{ fontSize: "9px" }}>
                {getCategoryEmoji(product.category)}
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginTop: "2px" }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--gray-text-muted)" }}>
                {product.sku_display}
              </span>
              {renderStatusBadge(product.inventory_status)}
            </div>
          </div>
        </div>

        {/* Animated Chevron Down Icon */}
        <div
          style={{
            transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 300ms cubic-bezier(0.4, 0, 0.2, 1)",
            color: isExpanded ? "var(--accent)" : "var(--gray-text-muted)",
            padding: "4px",
          }}
        >
          <ChevronDown size={20} />
        </div>
      </div>

      {/* 2. EXPANDED BODY (Smooth accordion expansion downward, lazy rendered) */}
      {isExpanded && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-4)",
            borderTop: "1px solid var(--gray-border)",
            paddingTop: "var(--space-4)",
            animation: "fadeInExpand 300ms ease-in-out",
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Section A: 7-Day Forecast */}
          <div
            style={{
              backgroundColor: "rgba(15, 23, 42, 0.6)",
              padding: "var(--space-3) var(--space-4)",
              borderRadius: "var(--radius-default)",
              border: "1px solid rgba(255, 255, 255, 0.05)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--gray-text-muted)", display: "block" }}>
                7-DAY AI DEMAND FORECAST
              </span>
              <strong style={{ fontSize: "18px", color: "#FFFFFF" }}>
                {product.forecast_7d ? `${product.forecast_7d.toFixed(0)} Units` : "318 Units"}
              </strong>
            </div>
            <div style={{ textAlign: "right" }}>
              <span className="badge badge-success" style={{ fontSize: "10px" }}>HIGH Confidence (92%)</span>
              <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block", marginTop: "2px" }}>
                LSTM Model v1.0
              </span>
            </div>
          </div>

          {/* Section B: Pricing Recommendation & Elasticity */}
          <div
            style={{
              padding: "var(--space-3) var(--space-4)",
              borderRadius: "var(--radius-default)",
              backgroundColor: isIncrease ? "rgba(99, 102, 241, 0.15)" : "rgba(245, 158, 11, 0.15)",
              border: isIncrease ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid rgba(245, 158, 11, 0.3)",
              display: "flex",
              flexDirection: "column",
              gap: "8px",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Zap size={14} style={{ color: isIncrease ? "var(--accent)" : "var(--warning)" }} />
                <span style={{ fontSize: "13px", fontWeight: 700, color: "#FFFFFF" }}>
                  {isIncrease ? "Increase price by 6%" : "Maintain current price"}
                </span>
              </div>
              <strong style={{ fontSize: "14px", color: "var(--success)" }}>
                +{formatCurrency(priceGain)} projected gain
              </strong>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--gray-text-muted)" }}>
              <span>Current: <strong>{formatCurrency(currentPrice)}</strong></span>
              <span>Recommended: <strong style={{ color: "var(--success)" }}>{formatCurrency(recommendedPrice)}</strong></span>
              <span>Diff: <strong style={{ color: "var(--success)" }}>+${(recommendedPrice - currentPrice).toFixed(2)}</strong></span>
            </div>

            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
              <span className="badge badge-secondary" style={{ fontSize: "9px" }}>Reason: Demand ↑ 14%</span>
              <span className="badge badge-secondary" style={{ fontSize: "9px" }}>Competitor price delta +8%</span>
              <span className="badge badge-success" style={{ fontSize: "9px" }}>Inventory healthy (18d cover)</span>
            </div>
          </div>

          {/* Section C: Inventory & Stock Velocity */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px", textAlign: "center" }}>
            <div style={{ backgroundColor: "rgba(15, 23, 42, 0.6)", padding: "8px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>CURRENT STOCK</span>
              <strong style={{ fontSize: "13px", color: "#FFFFFF" }}>142 Units</strong>
            </div>
            <div style={{ backgroundColor: "rgba(15, 23, 42, 0.6)", padding: "8px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>COVERAGE DAYS</span>
              <strong style={{ fontSize: "13px", color: "var(--success)" }}>18.4 Days</strong>
            </div>
            <div style={{ backgroundColor: "rgba(15, 23, 42, 0.6)", padding: "8px", borderRadius: "8px", border: "1px solid var(--gray-border)" }}>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>ANOMALY STATUS</span>
              <strong style={{ fontSize: "13px", color: "var(--success)" }}>Normal</strong>
            </div>
          </div>

          {/* Section D: 30-Day Quick Financial Metrics */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "8px",
              backgroundColor: "rgba(15, 23, 42, 0.4)",
              padding: "10px",
              borderRadius: "8px",
            }}
          >
            <div>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>30D REVENUE</span>
              <strong style={{ fontSize: "12px", color: "var(--success)" }}>{formatCurrency((product.forecast_7d || 50) * 4 * currentPrice)}</strong>
            </div>
            <div>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>30D UNITS</span>
              <strong style={{ fontSize: "12px", color: "#FFFFFF" }}>{((product.forecast_7d || 50) * 4).toFixed(0)} Units</strong>
            </div>
            <div>
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>AVG PRICE</span>
              <strong style={{ fontSize: "12px", color: "#FFFFFF" }}>{formatCurrency(currentPrice)}</strong>
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
              style={{ height: "36px", fontSize: "12px", padding: "0 12px", justifyContent: "center" }}
            >
              <Zap size={13} style={{ color: "var(--warning)" }} />
              Apply Price
            </button>
          </div>

          {/* Footer Metadata */}
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px", color: "var(--gray-text-muted)", borderTop: "1px solid rgba(255,255,255,0.05)", paddingTop: "8px" }}>
            <span>Last Analysis: <strong>Today 11:42 AM</strong></span>
            <span>AI Model Engine: <strong>v1.0</strong></span>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeInExpand {
          from { opacity: 0; transform: translateY(-6px); }
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
      backgroundColor: "#1E293B",
    }}
  />
);
