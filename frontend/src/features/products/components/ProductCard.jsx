import React, { useState } from "react";
import {
  Sparkles,
  ChevronRight,
  MoreVertical,
  AlertTriangle,
  CheckCircle,
  Eye,
  ShoppingBag,
} from "lucide-react";

export const ProductCard = ({ product, onSelect }) => {
  const [menuOpen, setMenuOpen] = useState(false);

  if (!product) return null;

  // Category label formatter
  const getCategoryLabel = (categoryStr) => {
    const clean = String(categoryStr || "").trim();
    return clean || "General";
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
      className="card card-interactive executive-product-card"
      onClick={() => onSelect(product.id)}
      style={{
        padding: "var(--space-4)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        gap: "var(--space-3)",
        position: "relative",
        transition: "all 200ms cubic-bezier(0.4, 0, 0.2, 1)",
        cursor: "pointer",
        backgroundColor: "#FFFFFF",
        border: "1px solid var(--gray-border)",
        borderRadius: "var(--radius-default)",
        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.02)",
      }}
    >
      {/* Top Header Row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span
          style={{
            fontSize: "10px",
            fontWeight: 700,
            backgroundColor: "#EEF2FF",
            color: "var(--accent)",
            padding: "2px 8px",
            borderRadius: "9999px",
          }}
        >
          {getCategoryLabel(product.category)}
        </span>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--gray-text-muted)" }}>
            {product.sku_display}
          </span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setMenuOpen(!menuOpen);
            }}
            style={{
              background: "none",
              border: "none",
              color: "var(--gray-text-muted)",
              cursor: "pointer",
              padding: "2px",
              borderRadius: "4px",
            }}
          >
            <MoreVertical size={14} />
          </button>
        </div>
      </div>

      {/* Dropdown Menu Overlay */}
      {menuOpen && (
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            position: "absolute",
            top: "36px",
            right: "16px",
            backgroundColor: "#FFFFFF",
            border: "1px solid var(--gray-border)",
            borderRadius: "var(--radius-default)",
            boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
            zIndex: 30,
            padding: "4px",
            minWidth: "160px",
          }}
        >
          <div
            onClick={() => {
              setMenuOpen(false);
              onSelect(product.id);
            }}
            style={{ padding: "6px 10px", fontSize: "12px", color: "var(--gray-text-primary)", cursor: "pointer", borderRadius: "4px" }}
            className="command-item-hover"
          >
            View Diagnostics
          </div>
          <div
            onClick={() => {
              setMenuOpen(false);
              alert(`Applied AI price of ${formatCurrency(recommendedPrice)} to ${product.sku_display}`);
            }}
            style={{ padding: "6px 10px", fontSize: "12px", color: "#059669", cursor: "pointer", borderRadius: "4px" }}
            className="command-item-hover"
          >
            Apply AI Price (${recommendedPrice.toFixed(2)})
          </div>
        </div>
      )}

      {/* Main Product Identity */}
      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <div
          style={{
            width: "42px",
            height: "42px",
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
          <ShoppingBag size={20} />
        </div>
        <div style={{ overflow: "hidden", flex: 1 }}>
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
          <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
            {product.brand ? `${product.brand} • ` : ""}{product.category || "General"}
          </span>
        </div>
      </div>

      {/* Compact Business Metrics Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "8px",
          backgroundColor: "#F8FAFC",
          padding: "10px",
          borderRadius: "var(--radius-default)",
          border: "1px solid var(--gray-border)",
        }}
      >
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>SALES (30D)</span>
          <strong style={{ fontSize: "13px", color: "var(--gray-text-primary)" }}>{(product.forecast_7d ? product.forecast_7d * 4 : 350).toLocaleString()} Units</strong>
        </div>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>REVENUE</span>
          <strong style={{ fontSize: "13px", color: "#059669" }}>{formatCurrency((product.forecast_7d ? product.forecast_7d * 4 : 350) * currentPrice)}</strong>
        </div>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>PRICE</span>
          <strong style={{ fontSize: "13px", color: "var(--gray-text-primary)" }}>{formatCurrency(currentPrice)}</strong>
        </div>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>STOCK</span>
          <strong style={{ fontSize: "13px", color: "var(--gray-text-primary)" }}>142 Units</strong>
        </div>
      </div>

      {/* AI Recommendation Box */}
      <div
        style={{
          padding: "8px 12px",
          borderRadius: "8px",
          backgroundColor: isIncrease ? "#EEF2FF" : "#FEF3C7",
          border: isIncrease ? "1px solid rgba(79, 70, 229, 0.3)" : "1px solid rgba(217, 119, 6, 0.3)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <Sparkles size={12} style={{ color: isIncrease ? "var(--accent)" : "var(--warning)" }} />
          <span style={{ fontSize: "11px", fontWeight: 700, color: "var(--gray-text-primary)" }}>
            {isIncrease ? "Increase price by 6%" : "Maintain current price"}
          </span>
        </div>
        <span style={{ fontSize: "11px", fontWeight: 800, color: "#059669" }}>
          +${priceGain.toFixed(0)} gain
        </span>
      </div>

      {/* Forecast & Status Badges */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>7D FORECAST</span>
          <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--gray-text-primary)" }}>
            {product.forecast_7d ? `${product.forecast_7d.toFixed(0)} Units` : "318 Units"}
          </span>
        </div>
        {renderStatusBadge(product.inventory_status)}
      </div>

      {/* Bottom Actions */}
      <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect(product.id);
          }}
          className="btn btn-primary btn-pill"
          style={{ flex: 1, height: "34px", fontSize: "12px", justifyContent: "center" }}
        >
          <Sparkles size={13} />
          Diagnostics
          <ChevronRight size={13} />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect(product.id);
          }}
          className="btn btn-secondary btn-pill"
          style={{ height: "34px", fontSize: "12px", padding: "0 12px", justifyContent: "center" }}
        >
          <Eye size={13} />
        </button>
      </div>

      {/* Hover Lift & Glow Animations */}
      <style>{`
        .executive-product-card:hover {
          transform: translateY(-3px) scale(1.01) !important;
          border-color: rgba(79, 70, 229, 0.4) !important;
          box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.08), 0 0 15px rgba(79, 70, 229, 0.08) !important;
        }
      `}</style>
    </div>
  );
};

export const ProductCardSkeleton = () => (
  <div
    className="skeleton-card"
    style={{
      height: "320px",
      borderRadius: "var(--radius-default)",
      backgroundColor: "#FFFFFF",
      border: "1px solid var(--gray-border)",
    }}
  />
);
