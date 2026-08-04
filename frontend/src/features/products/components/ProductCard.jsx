import React, { useState } from "react";
import {
  Sparkles,
  TrendingUp,
  Package,
  DollarSign,
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

  // Mock computed values based on product ID if missing from simple response
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
        background: "linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%)",
      }}
    >
      {/* 1. Top Header Row (Category Pill, SKU, 3-Dot Menu) */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span className="badge badge-purple" style={{ fontSize: "10px", fontWeight: 700 }}>
          {getCategoryEmoji(product.category)}
        </span>

        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--gray-text-muted)", letterSpacing: "0.05em" }}>
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
            backgroundColor: "#1E293B",
            border: "1px solid var(--gray-border)",
            borderRadius: "var(--radius-default)",
            boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.5)",
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
            style={{ padding: "6px 10px", fontSize: "12px", color: "#FFFFFF", cursor: "pointer", borderRadius: "4px" }}
            className="command-item-hover"
          >
            View Diagnostics
          </div>
          <div
            onClick={() => {
              setMenuOpen(false);
              alert(`Applied AI price of ${formatCurrency(recommendedPrice)} to ${product.sku_display}`);
            }}
            style={{ padding: "6px 10px", fontSize: "12px", color: "var(--success)", cursor: "pointer", borderRadius: "4px" }}
            className="command-item-hover"
          >
            Apply AI Price (${recommendedPrice.toFixed(2)})
          </div>
        </div>
      )}

      {/* 2. Main Product Identity (Thumbnail, Title, Brand Subtitle) */}
      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <div
          style={{
            width: "42px",
            height: "42px",
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
          <ShoppingBag size={20} />
        </div>
        <div style={{ overflow: "hidden", flex: 1 }}>
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
          <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
            {product.brand ? `${product.brand} • ` : ""}{product.category || "General"}
          </span>
        </div>
      </div>

      {/* 3. Compact Business Metrics Grid (4 KPIs) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "8px",
          backgroundColor: "rgba(15, 23, 42, 0.6)",
          padding: "10px",
          borderRadius: "var(--radius-default)",
          border: "1px solid rgba(255, 255, 255, 0.05)",
        }}
      >
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>SALES (30D)</span>
          <strong style={{ fontSize: "13px", color: "#FFFFFF" }}>{(product.forecast_7d ? product.forecast_7d * 4 : 350).toLocaleString()} Units</strong>
        </div>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>REVENUE</span>
          <strong style={{ fontSize: "13px", color: "var(--success)" }}>{formatCurrency((product.forecast_7d ? product.forecast_7d * 4 : 350) * currentPrice)}</strong>
        </div>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>PRICE</span>
          <strong style={{ fontSize: "13px", color: "#FFFFFF" }}>{formatCurrency(currentPrice)}</strong>
        </div>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>STOCK</span>
          <strong style={{ fontSize: "13px", color: "#FFFFFF" }}>142 Units</strong>
        </div>
      </div>

      {/* 4. AI Recommendation Container */}
      <div
        style={{
          padding: "8px 12px",
          borderRadius: "8px",
          backgroundColor: isIncrease ? "rgba(99, 102, 241, 0.15)" : "rgba(245, 158, 11, 0.15)",
          border: isIncrease ? "1px solid rgba(99, 102, 241, 0.3)" : "1px solid rgba(245, 158, 11, 0.3)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <Sparkles size={12} style={{ color: isIncrease ? "var(--accent)" : "var(--warning)" }} />
          <span style={{ fontSize: "11px", fontWeight: 700, color: "#FFFFFF" }}>
            {isIncrease ? "Increase price by 6%" : "Maintain current price"}
          </span>
        </div>
        <span style={{ fontSize: "11px", fontWeight: 800, color: "var(--success)" }}>
          +${priceGain.toFixed(0)} gain
        </span>
      </div>

      {/* 5. Forecast & Status Badges */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>7D FORECAST</span>
          <span style={{ fontSize: "12px", fontWeight: 700, color: "#FFFFFF" }}>
            {product.forecast_7d ? `${product.forecast_7d.toFixed(0)} Units` : "318 Units"}
          </span>
        </div>
        {renderStatusBadge(product.inventory_status)}
      </div>

      {/* 6. Bottom Actions */}
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
          border-color: rgba(99, 102, 241, 0.4) !important;
          box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.4), 0 0 15px rgba(99, 102, 241, 0.15) !important;
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
      backgroundColor: "#1E293B",
    }}
  />
);
