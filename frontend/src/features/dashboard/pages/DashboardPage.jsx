import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  TrendingUp,
  Package,
  DollarSign,
  AlertTriangle,
  ChevronRight,
  Activity,
  Layers,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { apiClient } from "../../../shared/apiClient";
import { ProductDetailDrawer } from "../../products/components/ProductDetailDrawer";

export const DashboardPage = () => {
  const [selectedProductId, setSelectedProductId] = useState(null);

  // Fetch dashboard overview aggregated analytics
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: async () => {
      const res = await apiClient.get("dashboard/overview");
      return res.data;
    },
  });

  // Utility to format numbers as Currency
  const formatCurrency = (val) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(val || 0);
  };

  // Utility to format dates inside charts
  const formatChartDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  // Render inventory classification badges
  const renderInventoryBadge = (status) => {
    const cleanStatus = String(status || "").toUpperCase();
    switch (cleanStatus) {
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
        return <span className="badge badge-info">{status || "UNKNOWN"}</span>;
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        {/* KPI Skeleton cards */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--space-4)" }}>
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
        </div>
        {/* Timeline skeleton */}
        <div className="skeleton-card" style={{ height: "300px" }} />
        {/* Table skeleton */}
        <div className="skeleton-card" style={{ height: "240px" }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="badge badge-danger" style={{ width: "100%", padding: "var(--space-3)", textTransform: "none" }}>
        <AlertTriangle size={16} />
        <span>Failed to load dashboard overview data. Please try again later.</span>
      </div>
    );
  }

  const { kpis, forecast_vs_actual, product_table } = data;

  return (
    <div>
      {/* 1. Header Toolbar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "var(--space-6)",
        }}
      >
        <div>
          <h2 style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            Retailer Analytics Dashboard
          </h2>
          <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
            Aggregate KPIs, demand forecasts, and optimized dynamic pricing recommendations.
          </p>
        </div>
      </div>

      {/* 2. Executive KPI Cards Row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "var(--space-5)",
          marginBottom: "var(--space-6)",
        }}
      >
        {/* Total Revenue 30d */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)", uppercase: "true" }}>
              Total Revenue (30d)
            </span>
            <div style={{ width: "34px", height: "34px", borderRadius: "10px", backgroundColor: "#EEF2FF", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--accent)" }}>
              <DollarSign size={18} />
            </div>
          </div>
          <span style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatCurrency(kpis.total_revenue_30d)}
          </span>
        </div>

        {/* Total Units Sold 30d */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)", uppercase: "true" }}>
              Units Ingested (30d)
            </span>
            <div style={{ width: "34px", height: "34px", borderRadius: "10px", backgroundColor: "#F0FDF4", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--success)" }}>
              <Package size={18} />
            </div>
          </div>
          <span style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {kpis.total_units_30d.toLocaleString()}
          </span>
        </div>

        {/* Weighted Average Price */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)", uppercase: "true" }}>
              Weighted Avg Price
            </span>
            <div style={{ width: "34px", height: "34px", borderRadius: "10px", backgroundColor: "#FAF5FF", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--purple)" }}>
              <TrendingUp size={18} />
            </div>
          </div>
          <span style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatCurrency(kpis.avg_price_30d)}
          </span>
        </div>

        {/* Active Alerts */}
        <div
          className="card card-interactive"
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-2)",
            borderColor: kpis.active_alerts_count > 0 ? "rgba(239, 68, 68, 0.3)" : "var(--gray-border)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)", uppercase: "true" }}>
              Active Anomaly Alerts
            </span>
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "10px",
                backgroundColor: kpis.active_alerts_count > 0 ? "#FEF2F2" : "#EFF6FF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: kpis.active_alerts_count > 0 ? "var(--error)" : "var(--info)",
              }}
            >
              <AlertTriangle size={18} />
            </div>
          </div>
          <span
            style={{
              fontSize: "28px",
              fontWeight: 800,
              color: kpis.active_alerts_count > 0 ? "var(--error)" : "var(--gray-text-primary)",
            }}
          >
            {kpis.active_alerts_count}
          </span>
        </div>
      </div>

      {/* 3. Main Chart Panel: 7-Day Actual vs Forecast Timeline */}
      <div className="card" style={{ padding: "var(--space-5)", marginBottom: "var(--space-6)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-5)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
            <Activity size={18} style={{ color: "var(--accent)" }} />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>7-Day Actual vs Forecast Tracking</h3>
          </div>
          
          {/* Confidence Legend Counts */}
          <div style={{ display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
            <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
              Forecasting Pipeline Tiers:
            </span>
            <span className="badge badge-success" style={{ fontSize: "11px" }}>
              High ({kpis.confidence_breakdown?.HIGH ?? 0})
            </span>
            <span className="badge badge-warning" style={{ fontSize: "11px" }}>
              Low ({kpis.confidence_breakdown?.LOW ?? 0})
            </span>
            <span className="badge badge-danger" style={{ fontSize: "11px" }}>
              None ({kpis.confidence_breakdown?.NONE ?? 0})
            </span>
          </div>
        </div>

        <div style={{ width: "100%", height: "260px" }}>
          {forecast_vs_actual && forecast_vs_actual.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecast_vs_actual} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatChartDate}
                  stroke="#94A3B8"
                  style={{ fontSize: "12px" }}
                />
                <YAxis stroke="#94A3B8" style={{ fontSize: "12px" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--gray-surface)",
                    borderColor: "var(--gray-border)",
                    borderRadius: "var(--radius-default)",
                    fontSize: "12px",
                  }}
                  labelFormatter={(lbl) => `Date: ${new Date(lbl).toLocaleDateString()}`}
                />
                <Legend wrapperStyle={{ fontSize: "12px", marginTop: "10px" }} />
                <Line
                  name="Actual Quantity"
                  type="monotone"
                  dataKey="actual_units"
                  stroke="var(--accent)"
                  strokeWidth={3}
                  activeDot={{ r: 6 }}
                />
                <Line
                  name="Forecasted Quantity"
                  type="monotone"
                  dataKey="forecasted_units"
                  stroke="#93C5FD"
                  strokeDasharray="5 5"
                  strokeWidth={3}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "var(--gray-text-muted)" }}>
              No forecast tracking dataset available. Upload data to view.
            </div>
          )}
        </div>
      </div>

      {/* 4. Product Table Grid */}
      <div className="table-container">
        <div style={{ padding: "var(--space-4) var(--space-5)", borderBottom: "1px solid var(--gray-border)", display: "flex", alignItems: "center", gap: "10px" }}>
          <Layers size={18} style={{ color: "var(--gray-text-muted)" }} />
          <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Active Product Diagnostics</h3>
        </div>

        <div className="table-responsive">
          {product_table && product_table.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Product Name</th>
                  <th>Category</th>
                  <th>7d Forecast</th>
                  <th>Recommended Price</th>
                  <th>Inventory Status</th>
                  <th>Alerts</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {product_table.map((row) => (
                  <tr key={row.id}>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "13px" }}>
                      {row.sku_display}
                    </td>
                    <td style={{ fontWeight: 600 }}>{row.product_name || "Unknown SKU"}</td>
                    <td>
                      <span className="badge badge-purple" style={{ fontSize: "11px" }}>
                        {row.category || "General"}
                      </span>
                    </td>
                    <td>
                      {row.forecast_7d !== null ? (
                        <strong>{row.forecast_7d.toFixed(0)} units</strong>
                      ) : (
                        <span style={{ color: "var(--gray-text-muted)" }}>N/A</span>
                      )}
                    </td>
                    <td>
                      {row.recommended_price !== null ? (
                        <strong>${row.recommended_price.toFixed(2)}</strong>
                      ) : (
                        <span style={{ color: "var(--gray-text-muted)" }}>N/A</span>
                      )}
                    </td>
                    <td>{renderInventoryBadge(row.inventory_status)}</td>
                    <td>
                      {row.alert_status ? (
                        <span className="badge badge-danger">
                          <AlertTriangle size={12} />
                          Alert
                        </span>
                      ) : (
                        <span className="badge badge-success">Clear</span>
                      )}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        onClick={() => setSelectedProductId(row.id)}
                        className="btn btn-secondary btn-pill"
                        style={{ height: "30px", padding: "0 var(--space-3)", fontSize: "12px" }}
                      >
                        Details
                        <ChevronRight size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: "60px var(--space-4)", textAlign: "center" }}>
              <Package size={36} style={{ color: "var(--gray-text-muted)", marginBottom: "var(--space-2)", opacity: 0.5 }} />
              <p style={{ fontWeight: 600, color: "var(--gray-text-muted)" }}>No products indexed yet.</p>
            </div>
          )}
        </div>
      </div>

      {/* 5. Product Summary Slide Drawer Overlay */}
      {selectedProductId && (
        <ProductDetailDrawer
          productId={selectedProductId}
          onClose={() => setSelectedProductId(null)}
        />
      )}
    </div>
  );
};

export default DashboardPage;
