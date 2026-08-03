import React, { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  X,
  TrendingUp,
  AlertTriangle,
  Coins,
  Clock,
  Sparkles,
} from "lucide-react";
import {
  AreaChart,
  Area,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { apiClient } from "../../../shared/apiClient";

export const ProductDetailDrawer = ({ productId, onClose }) => {
  // Fetch product summary details
  const { data, isLoading, error } = useQuery({
    queryKey: ["productSummary", productId],
    queryFn: async () => {
      const res = await apiClient.get(`/products/${productId}/summary`);
      return res.data;
    },
    enabled: !!productId,
  });

  // Handle Escape key dismissal
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!productId) return null;

  // Render status badge helper
  const renderStatusBadge = (status) => {
    switch (status) {
      case "HEALTHY":
      case "STABLE":
        return <span className="badge badge-success">{status}</span>;
      case "OVERSTOCK_RISK":
      case "RISING":
      case "FALLING":
        return <span className="badge badge-warning">{status}</span>;
      case "STOCKOUT_RISK":
        return <span className="badge badge-danger">{status}</span>;
      default:
        return <span className="badge badge-info">{status}</span>;
    }
  };

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} />
      <div className="slide-drawer" style={{ padding: "var(--space-5)", overflowY: "auto" }}>
        
        {/* Header toolbar */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            borderBottom: "1px solid var(--gray-border)",
            paddingBottom: "var(--space-4)",
            marginBottom: "var(--space-5)",
          }}
        >
          <div style={{ minWidth: 0 }}>
            <span
              className="badge badge-purple"
              style={{ marginBottom: "var(--space-2)", fontSize: "11px" }}
            >
              {data?.product?.category || "Loading Category..."}
            </span>
            <h3
              style={{
                fontSize: "18px",
                fontWeight: 700,
                textOverflow: "ellipsis",
                overflow: "hidden",
                whiteSpace: "nowrap",
                color: "var(--gray-text-primary)",
              }}
            >
              {data?.product?.product_name || "Product SKU details"}
            </h3>
            <p
              style={{
                fontFamily: "var(--font-mono)",
                fontSize: "12px",
                color: "var(--gray-text-muted)",
                marginTop: "var(--space-1)",
              }}
            >
              SKU: {data?.product?.sku_display || "loading..."}
            </p>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {isLoading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <div className="skeleton-card" style={{ height: "140px" }} />
            <div className="skeleton-card" style={{ height: "180px" }} />
            <div className="skeleton-card" style={{ height: "160px" }} />
          </div>
        ) : error ? (
          <div className="badge badge-danger" style={{ width: "100%", padding: "var(--space-3)", textTransform: "none" }}>
            <AlertTriangle size={16} />
            <span>Failed to load product details summary.</span>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
            
            {/* 1. 30-Day Sales Sparkline AreaChart */}
            <div className="card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-4)" }}>
                <TrendingUp size={16} style={{ color: "var(--accent)" }} />
                <h4 style={{ fontSize: "14px", fontWeight: 700 }}>Trailing 30-Day Sales Trend</h4>
              </div>
              <div style={{ width: "100%", height: "120px" }}>
                {data.sparkline && data.sparkline.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.sparkline.map((item, idx) => ({ ...item, idx }))}>
                      <defs>
                        <linearGradient id="sparklineGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "var(--gray-surface)",
                          borderColor: "var(--gray-border)",
                          borderRadius: "var(--radius-default)",
                          fontSize: "12px",
                        }}
                        labelFormatter={() => "Sales Day"}
                      />
                      <Area
                        type="monotone"
                        dataKey="quantity_sold"
                        stroke="var(--accent)"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#sparklineGrad)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "var(--gray-text-muted)", fontSize: "13px" }}>
                    No sales history record.
                  </div>
                )}
              </div>
            </div>

            {/* 2. Forecasting Horizons Info Box */}
            <div className="card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-3)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                  <Sparkles size={16} style={{ color: "var(--accent)" }} />
                  <h4 style={{ fontSize: "14px", fontWeight: 700 }}>Demand Forecast Horizon</h4>
                </div>
                <span className="badge badge-purple" style={{ fontSize: "11px" }}>
                  {data.forecast?.pipeline_type || "No Data"}
                </span>
              </div>

              {data.forecast?.horizon_7d ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                    <span style={{ color: "var(--gray-text-muted)" }}>Forecast Confidence:</span>
                    <strong style={{ textTransform: "uppercase" }}>{data.forecast.confidence_label}</strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                    <span style={{ color: "var(--gray-text-muted)" }}>Average daily projected demand:</span>
                    <strong>
                      {(
                        data.forecast.horizon_7d.predictions.reduce((acc, item) => acc + item.predicted_quantity, 0) /
                        data.forecast.horizon_7d.predictions.length
                      ).toFixed(1)}{" "}
                      units
                    </strong>
                  </div>
                </div>
              ) : (
                <p style={{ fontSize: "13px", color: "var(--gray-text-muted)" }}>
                  Insufficient baseline sales data history to construct daily predictive models.
                </p>
              )}
            </div>

            {/* 3. Dynamic Elasticity Pricing candidates Grid */}
            <div className="card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-3)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                  <Coins size={16} style={{ color: "var(--accent)" }} />
                  <h4 style={{ fontSize: "14px", fontWeight: 700 }}>Recommended Price Optimization</h4>
                </div>
                {data.pricing?.recommended_price ? (
                  <span className="badge badge-success" style={{ fontSize: "11px" }}>
                    ${data.pricing.recommended_price.toFixed(2)}
                  </span>
                ) : (
                  <span className="badge badge-danger" style={{ fontSize: "11px" }}>Ineligible</span>
                )}
              </div>

              {data.pricing?.candidate_grid && data.pricing.candidate_grid.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "10px", marginTop: "var(--space-3)" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: "var(--gray-text-muted)", borderBottom: "1px solid var(--gray-border)", paddingBottom: "4px" }}>
                    <span>Candidate Price</span>
                    <span>Est. Daily Demand</span>
                    <span>Est. Revenue</span>
                  </div>
                  {data.pricing.candidate_grid.map((cand, idx) => {
                    const isRecommended = cand.candidate_price === data.pricing.recommended_price;
                    return (
                      <div
                        key={idx}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          fontSize: "13px",
                          padding: "4px 8px",
                          borderRadius: "4px",
                          backgroundColor: isRecommended ? "rgba(16, 185, 129, 0.08)" : "transparent",
                          fontWeight: isRecommended ? 700 : 400,
                          border: isRecommended ? "1px solid rgba(16, 185, 129, 0.3)" : "none",
                        }}
                      >
                        <span>${cand.candidate_price.toFixed(2)}</span>
                        <span>{cand.estimated_demand.toFixed(1)} units</span>
                        <span style={{ color: isRecommended ? "var(--success)" : "inherit" }}>
                          ${cand.estimated_revenue.toFixed(2)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p style={{ fontSize: "13px", color: "var(--gray-text-muted)" }}>
                  Price optimization is disabled due to insufficient price variations in transaction history records.
                </p>
              )}
            </div>

            {/* 4. Inventory Days of Cover risk notices */}
            <div className="card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-3)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                  <Clock size={16} style={{ color: "var(--accent)" }} />
                  <h4 style={{ fontSize: "14px", fontWeight: 700 }}>Inventory Status</h4>
                </div>
                {data.inventory ? (
                  renderStatusBadge(
                    data.inventory.mode === "TRUE_RISK"
                      ? data.inventory.true_risk?.classification
                      : data.inventory.advisory?.demand_trend
                  )
                ) : (
                  <span className="badge badge-info">No Data</span>
                )}
              </div>

              {data.inventory ? (
                data.inventory.mode === "TRUE_RISK" ? (
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "13px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ color: "var(--gray-text-muted)" }}>Stock Level:</span>
                      <strong>{data.inventory.true_risk.current_inventory_level} units</strong>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span style={{ color: "var(--gray-text-muted)" }}>Days of Cover:</span>
                      <strong>{data.inventory.true_risk.days_of_cover.toFixed(1)} Days</strong>
                    </div>
                  </div>
                ) : (
                  <div style={{ fontSize: "13px", display: "flex", flexDirection: "column", gap: "6px" }}>
                    <p style={{ color: "var(--gray-text-muted)" }}>{data.inventory.advisory.message}</p>
                  </div>
                )
              ) : (
                <p style={{ fontSize: "13px", color: "var(--gray-text-muted)" }}>
                  No stock level data recorded. Please upload inventory files to activate risk analytics.
                </p>
              )}
            </div>

            {/* 5. Anomaly flags alert logs */}
            {data.anomaly?.flagged_anomalies && data.anomaly.flagged_anomalies.length > 0 && (
              <div className="card" style={{ padding: "var(--space-4)", borderColor: "rgba(239, 68, 68, 0.3)" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-3)" }}>
                  <AlertTriangle size={16} style={{ color: "var(--error)" }} />
                  <h4 style={{ fontSize: "14px", fontWeight: 700 }}>Flagged Anomalies</h4>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
                  {data.anomaly.flagged_anomalies.map((anom, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "var(--space-2) var(--space-3)",
                        borderRadius: "var(--radius-default)",
                        backgroundColor: "rgba(239, 68, 68, 0.08)",
                        fontSize: "12px",
                        border: "1px solid rgba(239, 68, 68, 0.2)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <strong style={{ color: "var(--error)" }}>
                          {anom.anomaly_type} ({anom.stage})
                        </strong>
                        <span style={{ color: "var(--gray-text-muted)" }}>
                          {new Date(anom.date).toLocaleDateString()}
                        </span>
                      </div>
                      <p style={{ color: "var(--gray-text-primary)" }}>{anom.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
};

export default ProductDetailDrawer;
