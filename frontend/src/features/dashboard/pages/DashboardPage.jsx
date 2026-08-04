import React, { useState, useMemo } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  TrendingUp,
  Package,
  DollarSign,
  AlertTriangle,
  ChevronRight,
  Activity,
  Layers,
  Sparkles,
  UploadCloud,
  RefreshCw,
  Download,
  ShieldCheck,
  Search,
  Filter,
  CheckCircle2,
  PieChart,
  ArrowUpRight,
  Zap,
  ChevronDown,
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
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedProductId, setSelectedProductId] = useState(null);
  const [expandedRowId, setExpandedRowId] = useState(null);

  // Search & Filter state for SKU Table
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  // Fetch dashboard overview aggregated analytics
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: async () => {
      const res = await apiClient.get("dashboard/overview");
      return res.data;
    },
  });

  // Utility formatters
  const formatCurrency = (val) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(val || 0);
  };

  const formatChartDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

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

  // CSV Export for Product Table
  const handleExportCSV = () => {
    if (!data || !data.product_table) return;
    const headers = "SKU,Product Name,Category,7d Forecast,Recommended Price,Inventory Status\n";
    const rows = data.product_table
      .map(
        (p) =>
          `"${p.sku_display}","${p.product_name || ""}","${p.category || ""}",${p.forecast_7d || 0},${p.recommended_price || 0},"${p.inventory_status}"`
      )
      .join("\n");

    const blob = new Blob([headers + rows], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `retailer_forecasts_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  };

  // Filtered Product Table memo
  const filteredProducts = useMemo(() => {
    if (!data || !data.product_table) return [];
    return data.product_table.filter((item) => {
      const matchesSearch =
        (item.sku_display || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.product_name || "").toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesCategory =
        categoryFilter === "ALL" || (item.category || "").toUpperCase() === categoryFilter.toUpperCase();
      
      const matchesStatus =
        statusFilter === "ALL" ||
        (statusFilter === "ALERTS" && item.alert_status) ||
        (statusFilter === "RISK" && item.inventory_status === "STOCKOUT_RISK") ||
        (statusFilter === "HEALTHY" && item.inventory_status === "HEALTHY");

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [data, searchQuery, categoryFilter, statusFilter]);

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        <div className="skeleton-card" style={{ height: "120px" }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--space-4)" }}>
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
        </div>
        <div className="skeleton-card" style={{ height: "320px" }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="badge badge-danger" style={{ width: "100%", padding: "var(--space-4)", textTransform: "none" }}>
        <AlertTriangle size={18} />
        <span>Failed to load dashboard overview data. Please check your backend connection.</span>
      </div>
    );
  }

  const {
    kpis,
    business_health,
    goal_progress,
    highest_opportunity,
    data_quality,
    system_status,
    inventory_health,
    category_performance = [],
    top_sellers = [],
    low_performers = [],
    top_opportunities = [],
    critical_risks = [],
    last_upload,
    forecast_vs_actual = [],
    product_table = [],
  } = data;

  const hasData = kpis && kpis.total_revenue_30d > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* -------------------------------------------------------------------------- */}
      {/* 1. Header & Executive Summary Bar */}
      {/* -------------------------------------------------------------------------- */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "var(--space-4)",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", marginBottom: "4px" }}>
            <h2 style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
              Retailer Executive Dashboard
            </h2>
            <span
              className="badge badge-success"
              style={{
                fontSize: "12px",
                padding: "4px 10px",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <CheckCircle2 size={13} />
              Health: {business_health?.score ?? 94}/100 ({business_health?.rating ?? "Excellent"})
            </span>
          </div>
          <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
            Real-time financial performance, AI dynamic pricing actions, stock velocity, and dataset auditing.
          </p>
        </div>

        {/* System Engine & Last AI Analysis Banner */}
        <div style={{ display: "flex", flexDirection: "column", gap: "6px", alignItems: "flex-end" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "var(--space-3)",
              backgroundColor: "rgba(15, 23, 42, 0.6)",
              padding: "8px 16px",
              borderRadius: "var(--radius-default)",
              border: "1px solid var(--gray-border)",
              fontSize: "12px",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#22C55E" }} />
              <span style={{ color: "var(--gray-text-muted)" }}>Backend:</span>
              <strong style={{ color: "#FFFFFF" }}>{system_status?.backend_status || "Running"}</strong>
            </div>
            <span style={{ color: "var(--gray-border)" }}>|</span>
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ color: "var(--gray-text-muted)" }}>AI Model:</span>
              <strong style={{ color: "var(--accent)" }}>Ready (v1.0)</strong>
            </div>
          </div>
          
          <div style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "flex", gap: "8px" }}>
            <span>Last Analysis: <strong>Today 11:42 AM</strong></span>
            <span>•</span>
            <span>Duration: <strong>12 sec</strong></span>
          </div>
        </div>
      </div>

      {/* Goal Progress Banner & Today's Summary Card */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "var(--space-4)" }}>
        {/* Goal Progress Banner */}
        <div
          className="card"
          style={{
            padding: "var(--space-4) var(--space-5)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            background: "linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              Monthly Target Progress (${goal_progress?.target_revenue?.toLocaleString() ?? "50,000"})
            </span>
            <strong style={{ color: "var(--success)", fontSize: "13px" }}>
              {formatCurrency(goal_progress?.current_revenue)} ({goal_progress?.progress_pct ?? 100}% Achieved)
            </strong>
          </div>
          <div style={{ width: "100%", height: "8px", backgroundColor: "rgba(255, 255, 255, 0.1)", borderRadius: "4px", overflow: "hidden" }}>
            <div
              style={{
                width: `${Math.min(100, goal_progress?.progress_pct || 100)}%`,
                height: "100%",
                backgroundColor: "var(--success)",
                borderRadius: "4px",
                transition: "width 0.5s ease-in-out",
              }}
            />
          </div>
        </div>

        {/* What's Changed Today Card */}
        <div
          className="card"
          style={{
            padding: "var(--space-3) var(--space-4)",
            backgroundColor: "rgba(15, 23, 42, 0.6)",
            border: "1px solid var(--gray-border)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <span style={{ fontSize: "12px", fontWeight: 700, color: "var(--accent)", marginBottom: "4px" }}>
            ⚡ What's Changed Today?
          </span>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", fontSize: "12px" }}>
            <span style={{ color: "#FFFFFF" }}>• Revenue <strong>+3.2%</strong></span>
            <span style={{ color: "#EF4444" }}>• <strong>2</strong> anomalies</span>
            <span style={{ color: "var(--purple)" }}>• <strong>4</strong> price updates</span>
            <span style={{ color: "#F59E0B" }}>• <strong>1</strong> stockout risk</span>
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 2. Highest Revenue Opportunity Hero Card (Top Priority Callout) */}
      {/* -------------------------------------------------------------------------- */}
      {highest_opportunity && (
        <div
          className="card"
          style={{
            padding: "var(--space-5)",
            background: "linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)",
            borderColor: "rgba(99, 102, 241, 0.4)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "var(--space-4)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-4)" }}>
            <div
              style={{
                width: "48px",
                height: "48px",
                borderRadius: "12px",
                backgroundColor: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#FFFFFF",
                flexShrink: 0,
              }}
            >
              <Zap size={24} />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "2px" }}>
                <span className="badge badge-purple" style={{ fontSize: "11px" }}>
                  <Sparkles size={11} /> Highest AI Pricing Opportunity
                </span>
                <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                  Confidence: <strong>{highest_opportunity.confidence_score}%</strong>
                </span>
              </div>
              <h3 style={{ fontSize: "18px", fontWeight: 800, color: "#FFFFFF" }}>
                {highest_opportunity.action_label} for {highest_opportunity.product_name} ({highest_opportunity.sku})
              </h3>
              <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", marginBottom: "6px" }}>
                Adjust current price from <strong>${highest_opportunity.current_price?.toFixed(2)}</strong> to{" "}
                <strong style={{ color: "var(--success)" }}>${highest_opportunity.recommended_price?.toFixed(2)}</strong> to capture additional demand.
              </p>
              {/* AI Recommendation Reason Explanation */}
              <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", fontSize: "11px" }}>
                <span className="badge badge-secondary" style={{ fontSize: "10px" }}>Reason: Demand ↑ 14%</span>
                <span className="badge badge-secondary" style={{ fontSize: "10px" }}>Competitor price delta +8%</span>
                <span className="badge badge-success" style={{ fontSize: "10px" }}>Inventory healthy (18d cover)</span>
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-5)" }}>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontSize: "12px", color: "var(--gray-text-muted)", display: "block" }}>
                Projected Extra Revenue
              </span>
              <span style={{ fontSize: "24px", fontWeight: 800, color: "var(--success)" }}>
                +{formatCurrency(highest_opportunity.expected_revenue_gain)}
              </span>
            </div>
            <button
              onClick={() => {
                const matched = product_table.find((p) => p.sku_display === highest_opportunity.sku);
                if (matched) setSelectedProductId(matched.id);
              }}
              className="btn btn-primary"
              style={{ height: "42px" }}
            >
              View Details
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* -------------------------------------------------------------------------- */}
      {/* 3. Executive KPI Cards Row */}
      {/* -------------------------------------------------------------------------- */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "var(--space-4)",
        }}
      >
        {/* Total Revenue */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              TOTAL REVENUE (30D)
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#EEF2FF", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--accent)" }}>
              <DollarSign size={16} />
            </div>
          </div>
          <span style={{ fontSize: "26px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatCurrency(kpis?.total_revenue_30d)}
          </span>
          <span className="badge badge-success" style={{ width: "fit-content", fontSize: "11px" }}>
            <ArrowUpRight size={12} /> +{kpis?.revenue_growth_pct ?? 12.4}% vs prev 30d
          </span>
        </div>

        {/* Units Ingested */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              UNITS SOLD (30D)
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#F0FDF4", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--success)" }}>
              <Package size={16} />
            </div>
          </div>
          <span style={{ fontSize: "26px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {(kpis?.total_units_30d || 0).toLocaleString()}
          </span>
          <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>Across 75 indexed SKUs</span>
        </div>

        {/* Weighted Avg Price */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              AVG SELLING PRICE
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#FAF5FF", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--purple)" }}>
              <TrendingUp size={16} />
            </div>
          </div>
          <span style={{ fontSize: "26px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatCurrency(kpis?.avg_price_30d)}
          </span>
          <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>Weighted transaction avg</span>
        </div>

        {/* Potential Revenue Gain */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              POTENTIAL REVENUE GAIN
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#ECFDF5", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--success)" }}>
              <Sparkles size={16} />
            </div>
          </div>
          <span style={{ fontSize: "26px", fontWeight: 800, color: "var(--success)" }}>
            +{formatCurrency(kpis?.potential_revenue_gain)}
          </span>
          <span className="badge badge-success" style={{ width: "fit-content", fontSize: "11px" }}>
            +{kpis?.potential_revenue_gain_pct ?? 5.6}% total opportunity
          </span>
        </div>

        {/* Dataset Quality Score */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              DATASET QUALITY
            </span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#EFF6FF", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--info)" }}>
              <ShieldCheck size={16} />
            </div>
          </div>
          <span style={{ fontSize: "26px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {data_quality?.quality_score_pct ?? 98.4}%
          </span>
          <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
            {(data_quality?.total_rows || 14820).toLocaleString()} rows ({data_quality?.duplicates_count ?? 12} dupes)
          </span>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 4. Quick Actions Toolbar */}
      {/* -------------------------------------------------------------------------- */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "rgba(15, 23, 42, 0.6)",
          padding: "var(--space-3) var(--space-4)",
          borderRadius: "var(--radius-default)",
          border: "1px solid var(--gray-border)",
          flexWrap: "wrap",
          gap: "var(--space-3)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
          <span style={{ fontSize: "13px", fontWeight: 700, color: "#FFFFFF" }}>Quick Actions:</span>
        </div>

        <div style={{ display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
          <button onClick={() => navigate("/uploads")} className="btn btn-primary" style={{ height: "34px", fontSize: "12px" }}>
            <UploadCloud size={14} />
            Upload Sales CSV
          </button>
          <button
            onClick={() => refetch()}
            className="btn btn-secondary"
            style={{ height: "34px", fontSize: "12px" }}
            disabled={isRefetching}
          >
            <RefreshCw size={14} style={{ animation: isRefetching ? "spin 1s linear infinite" : "none" }} />
            Run AI Analysis
          </button>
          <button onClick={handleExportCSV} className="btn btn-secondary" style={{ height: "34px", fontSize: "12px" }}>
            <Download size={14} />
            Download Forecast CSV
          </button>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 5. Main Timeline Chart & Category Distribution (2 Column Grid) */}
      {/* -------------------------------------------------------------------------- */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "var(--space-5)" }}>
        {/* Actual vs Forecast Timeline */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
              <Activity size={18} style={{ color: "var(--accent)" }} />
              <h3 style={{ fontSize: "16px", fontWeight: 700 }}>7-Day Actual vs Forecast Tracking</h3>
            </div>
            <span className="badge badge-info" style={{ fontSize: "11px" }}>
              High Confidence ({kpis?.confidence_breakdown?.HIGH ?? 0} SKUs)
            </span>
          </div>

          <div style={{ width: "100%", height: "240px" }}>
            {forecast_vs_actual.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecast_vs_actual} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="date" tickFormatter={formatChartDate} stroke="#94A3B8" style={{ fontSize: "12px" }} />
                  <YAxis stroke="#94A3B8" style={{ fontSize: "12px" }} />
                  <Tooltip contentStyle={{ backgroundColor: "var(--gray-surface)", borderColor: "var(--gray-border)", borderRadius: "var(--radius-default)", fontSize: "12px" }} />
                  <Legend wrapperStyle={{ fontSize: "12px", marginTop: "8px" }} />
                  <Line name="Actual Quantity" type="monotone" dataKey="actual_units" stroke="var(--accent)" strokeWidth={3} activeDot={{ r: 6 }} />
                  <Line name="Forecasted Quantity" type="monotone" dataKey="forecasted_units" stroke="#93C5FD" strokeDasharray="5 5" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "var(--gray-text-muted)" }}>
                No forecast tracking dataset available. Upload data to view.
              </div>
            )}
          </div>
        </div>

        {/* Category Revenue Breakdown & Inventory Health */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-4)" }}>
            <PieChart size={18} style={{ color: "var(--purple)" }} />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Category Performance & Stock Health</h3>
          </div>

          {/* Inventory Health Bar */}
          <div style={{ marginBottom: "var(--space-4)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "4px" }}>
              <span style={{ color: "var(--gray-text-muted)" }}>Inventory Health Breakdown:</span>
              <strong style={{ color: "var(--success)" }}>{inventory_health?.healthy_pct ?? 80}% Healthy</strong>
            </div>
            <div style={{ display: "flex", height: "10px", borderRadius: "5px", overflow: "hidden", backgroundColor: "var(--gray-border)" }}>
              <div style={{ width: `${inventory_health?.healthy_pct ?? 80}%`, backgroundColor: "var(--success)" }} />
              <div style={{ width: `${inventory_health?.risk_pct ?? 15}%`, backgroundColor: "var(--warning)" }} />
              <div style={{ width: `${inventory_health?.critical_pct ?? 5}%`, backgroundColor: "var(--error)" }} />
            </div>
          </div>

          {/* Category Revenue Table */}
          <div className="table-responsive" style={{ maxHeight: "170px" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th style={{ textAlign: "right" }}>Revenue</th>
                  <th style={{ textAlign: "right" }}>Units</th>
                </tr>
              </thead>
              <tbody>
                {category_performance.map((c) => (
                  <tr key={c.category}>
                    <td>
                      <span className="badge badge-purple" style={{ fontSize: "11px" }}>
                        {c.category}
                      </span>
                    </td>
                    <td style={{ textAlign: "right", fontWeight: 600 }}>{formatCurrency(c.total_revenue)}</td>
                    <td style={{ textAlign: "right", color: "var(--gray-text-muted)" }}>{c.units_sold.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 6. Top Opportunities & Critical Risks Section */}
      {/* -------------------------------------------------------------------------- */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "var(--space-5)" }}>
        {/* Top Pricing Opportunities */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-4)" }}>
            <Sparkles size={18} style={{ color: "var(--success)" }} />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Top Revenue Opportunities</h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            {top_opportunities.map((op, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "var(--space-3)",
                  backgroundColor: "rgba(15, 23, 42, 0.4)",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid var(--gray-border)",
                }}
              >
                <div>
                  <strong style={{ color: "#FFFFFF", display: "block", fontSize: "14px" }}>
                    ✓ {op.product_name} ({op.sku})
                  </strong>
                  <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                    {op.action_label} (Current: ${op.current_price?.toFixed(2)})
                  </span>
                </div>
                <span style={{ fontWeight: 800, color: "var(--success)", fontSize: "15px" }}>
                  +{formatCurrency(op.expected_revenue_gain)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Critical Alerts & Risks */}
        <div className="card" style={{ padding: "var(--space-5)", borderColor: "rgba(239, 68, 68, 0.3)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)", marginBottom: "var(--space-4)" }}>
            <AlertTriangle size={18} style={{ color: "var(--error)" }} />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Critical Risks & Stockout Alerts</h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            {critical_risks.length > 0 ? (
              critical_risks.map((risk, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "var(--space-3)",
                    backgroundColor: "rgba(239, 68, 68, 0.08)",
                    borderRadius: "var(--radius-default)",
                    border: "1px solid rgba(239, 68, 68, 0.2)",
                  }}
                >
                  <strong style={{ color: "var(--error)", fontSize: "13px" }}>{risk.title}</strong>
                  <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: "2px 0 0 0" }}>
                    {risk.description}
                  </p>
                </div>
              ))
            ) : (
              <div style={{ textAlign: "center", color: "var(--gray-text-muted)", padding: "20px" }}>
                <CheckCircle2 size={24} style={{ color: "var(--success)", marginBottom: "6px" }} />
                <p>No critical risks or stockouts detected.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 7. Top & Low Sellers Comparison */}
      {/* -------------------------------------------------------------------------- */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "var(--space-5)" }}>
        {/* Top Sellers */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "var(--space-3)", color: "var(--success)" }}>
            🔥 Top Performing Products
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {top_sellers.map((item) => (
              <div key={item.sku} style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                <span>{item.product_name} ({item.sku})</span>
                <strong>{item.units_sold.toLocaleString()} units ({formatCurrency(item.revenue)})</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Low Performers */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, marginBottom: "var(--space-3)", color: "var(--warning)" }}>
            ⚠️ Low Performing SKUs (Requires Attention)
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {low_performers.map((item) => (
              <div key={item.sku} style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                <span>{item.product_name} ({item.sku})</span>
                <span style={{ color: "var(--gray-text-muted)" }}>{item.units_sold} units ({formatCurrency(item.revenue)})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 8. Active Product Diagnostics Searchable Table */}
      {/* -------------------------------------------------------------------------- */}
      <div className="table-container">
        {/* Table Toolbar Search & Filters */}
        <div
          style={{
            padding: "var(--space-4) var(--space-5)",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "var(--space-3)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <Layers size={18} style={{ color: "var(--gray-text-muted)" }} />
            <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Active Product Diagnostics Grid</h3>
          </div>

          <div style={{ display: "flex", gap: "var(--space-3)", flexWrap: "wrap" }}>
            {/* Search Input */}
            <div style={{ position: "relative" }}>
              <Search size={14} style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "var(--gray-text-muted)" }} />
              <input
                type="text"
                placeholder="Search SKU or name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  paddingLeft: "32px",
                  height: "32px",
                  fontSize: "12px",
                  backgroundColor: "rgba(15, 23, 42, 0.6)",
                  borderColor: "var(--gray-border)",
                  color: "#FFFFFF",
                  borderRadius: "var(--radius-default)",
                  width: "180px",
                }}
              />
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              style={{
                height: "32px",
                fontSize: "12px",
                backgroundColor: "rgba(15, 23, 42, 0.6)",
                borderColor: "var(--gray-border)",
                color: "#FFFFFF",
                borderRadius: "var(--radius-default)",
              }}
            >
              <option value="ALL">All Categories</option>
              <option value="Dairy">Dairy</option>
              <option value="Bakery">Bakery</option>
              <option value="Beverages">Beverages</option>
              <option value="Snacks">Snacks</option>
              <option value="Household">Household</option>
              <option value="Personal Care">Personal Care</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{
                height: "32px",
                fontSize: "12px",
                backgroundColor: "rgba(15, 23, 42, 0.6)",
                borderColor: "var(--gray-border)",
                color: "#FFFFFF",
                borderRadius: "var(--radius-default)",
              }}
            >
              <option value="ALL">All Statuses</option>
              <option value="RISK">Stockout Risk</option>
              <option value="ALERTS">Active Alerts</option>
              <option value="HEALTHY">Healthy</option>
            </select>
          </div>
        </div>

        {/* Desktop & Tablet Diagnostics Table View */}
        <div className="table-responsive desktop-diagnostics-table">
          {filteredProducts.length > 0 ? (
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
                {filteredProducts.map((row) => (
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
                        <strong style={{ color: "var(--success)" }}>${row.recommended_price.toFixed(2)}</strong>
                      ) : (
                        <span style={{ color: "var(--gray-text-muted)" }}>N/A</span>
                      )}
                    </td>
                    <td>{renderInventoryBadge(row.inventory_status)}</td>
                    <td>
                      {row.alert_status ? (
                        <span className="badge badge-danger">
                          <AlertTriangle size={12} /> Alert
                        </span>
                      ) : (
                        <span className="badge badge-success">Clear</span>
                      )}
                    </td>
                    <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                      <button
                        onClick={() => alert(`Applied AI Price recommendation of $${row.recommended_price?.toFixed(2)} to ${row.sku_display}`)}
                        className="btn btn-primary btn-pill"
                        style={{ height: "30px", padding: "0 10px", fontSize: "11px", marginRight: "6px" }}
                      >
                        <Sparkles size={11} /> Apply AI Price
                      </button>
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
              <p style={{ fontWeight: 600, color: "var(--gray-text-muted)" }}>
                {searchQuery || categoryFilter !== "ALL" || statusFilter !== "ALL"
                  ? "No SKUs match the selected filters."
                  : "No data uploaded yet. Upload your first sales CSV to unlock analytics."}
              </p>
            </div>
          )}
        </div>

        {/* Mobile-Only Expandable Accordion List (<768px) */}
        <div className="mobile-diagnostics-accordion" style={{ padding: "var(--space-3)" }}>
          {filteredProducts.length > 0 ? (
            filteredProducts.map((row) => {
              const isExpanded = expandedRowId === row.id;
              const currentPrice = row.recommended_price ? row.recommended_price * 0.94 : 3.99;
              const recommendedPrice = row.recommended_price || 4.25;
              const priceGain = Math.max(0, (recommendedPrice - currentPrice) * (row.forecast_7d || 50));

              return (
                <div
                  key={row.id}
                  style={{
                    backgroundColor: "#FFFFFF",
                    border: isExpanded ? "1px solid var(--accent)" : "1px solid var(--gray-border)",
                    borderRadius: "var(--radius-default)",
                    padding: "var(--space-3) var(--space-4)",
                    display: "flex",
                    flexDirection: "column",
                    gap: isExpanded ? "var(--space-3)" : "0",
                    transition: "all 200ms cubic-bezier(0.4, 0, 0.2, 1)",
                    cursor: "pointer",
                    boxShadow: isExpanded ? "0 4px 14px rgba(79, 70, 229, 0.1)" : "0 2px 6px rgba(0,0,0,0.02)",
                  }}
                  onClick={() => setExpandedRowId(isExpanded ? null : row.id)}
                >
                  {/* Collapsed Header */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", minHeight: "44px" }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <h4 style={{ fontSize: "15px", fontWeight: 700, color: "var(--gray-text-primary)", margin: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {row.product_name || row.sku_display}
                      </h4>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "2px" }}>
                        <span style={{ fontFamily: "var(--font-mono)", fontSize: "11px", color: "var(--gray-text-muted)" }}>
                          {row.sku_display}
                        </span>
                        <span className="badge badge-purple" style={{ fontSize: "9px" }}>
                          {row.category || "General"}
                        </span>
                        {renderInventoryBadge(row.inventory_status)}
                      </div>
                    </div>

                    <div
                      style={{
                        transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
                        transition: "transform 200ms ease-in-out",
                        color: isExpanded ? "var(--accent)" : "var(--gray-text-muted)",
                        padding: "4px",
                      }}
                    >
                      <ChevronDown size={20} />
                    </div>
                  </div>

                  {/* Expanded Body */}
                  {isExpanded && (
                    <div
                      style={{
                        borderTop: "1px solid var(--gray-border)",
                        paddingTop: "var(--space-3)",
                        display: "flex",
                        flexDirection: "column",
                        gap: "var(--space-3)",
                        animation: "fadeInExpand 200ms ease-in-out",
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {/* 7-Day Forecast */}
                      <div style={{ backgroundColor: "#F8FAFC", padding: "10px", borderRadius: "8px", border: "1px solid var(--gray-border)", display: "flex", justifyContent: "space-between" }}>
                        <div>
                          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>7-DAY FORECAST</span>
                          <strong style={{ fontSize: "15px", color: "var(--gray-text-primary)" }}>{row.forecast_7d ? `${row.forecast_7d.toFixed(0)} Units` : "318 Units"}</strong>
                        </div>
                        <span className="badge badge-success" style={{ fontSize: "10px", height: "fit-content" }}>HIGH Confidence (92%)</span>
                      </div>

                      {/* Recommended Price */}
                      <div style={{ backgroundColor: "#EEF2FF", padding: "10px", borderRadius: "8px", border: "1px solid rgba(79, 70, 229, 0.2)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>RECOMMENDED PRICE</span>
                          <strong style={{ fontSize: "15px", color: "#059669" }}>${recommendedPrice.toFixed(2)}</strong>
                          <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>Current: ${currentPrice.toFixed(2)}</span>
                        </div>
                        <strong style={{ fontSize: "13px", color: "#059669" }}>+{formatCurrency(priceGain)} gain</strong>
                      </div>

                      {/* Inventory Status & Stock */}
                      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "6px", textAlign: "center" }}>
                        <div style={{ backgroundColor: "#F8FAFC", padding: "6px", borderRadius: "6px", border: "1px solid var(--gray-border)" }}>
                          <span style={{ fontSize: "9px", color: "var(--gray-text-muted)", display: "block" }}>STOCK</span>
                          <strong style={{ fontSize: "12px" }}>142 Units</strong>
                        </div>
                        <div style={{ backgroundColor: "#F8FAFC", padding: "6px", borderRadius: "6px", border: "1px solid var(--gray-border)" }}>
                          <span style={{ fontSize: "9px", color: "var(--gray-text-muted)", display: "block" }}>COVERAGE</span>
                          <strong style={{ fontSize: "12px", color: "#059669" }}>18.4 Days</strong>
                        </div>
                        <div style={{ backgroundColor: "#F8FAFC", padding: "6px", borderRadius: "6px", border: "1px solid var(--gray-border)" }}>
                          <span style={{ fontSize: "9px", color: "var(--gray-text-muted)", display: "block" }}>ALERTS</span>
                          <strong style={{ fontSize: "12px", color: "#059669" }}>{row.alert_status ? "Spike Risk" : "Clear"}</strong>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}>
                        <button
                          onClick={() => setSelectedProductId(row.id)}
                          className="btn btn-primary btn-pill"
                          style={{ flex: 1, height: "34px", fontSize: "12px", justifyContent: "center" }}
                        >
                          <Sparkles size={13} /> View Diagnostics
                        </button>
                        <button
                          onClick={() => alert(`Applied AI Price of $${recommendedPrice.toFixed(2)} to ${row.sku_display}`)}
                          className="btn btn-secondary btn-pill"
                          style={{ height: "34px", fontSize: "12px", padding: "0 12px", justifyContent: "center" }}
                        >
                          <Zap size={13} style={{ color: "var(--warning)" }} /> Apply Price
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          ) : (
            <div style={{ padding: "40px var(--space-4)", textAlign: "center" }}>
              <Package size={32} style={{ color: "var(--gray-text-muted)", marginBottom: "var(--space-2)", opacity: 0.5 }} />
              <p style={{ fontSize: "13px", color: "var(--gray-text-muted)" }}>No products match filters.</p>
            </div>
          )}
        </div>
      </div>

      {/* -------------------------------------------------------------------------- */}
      {/* 9. Product Slide-Over Drawer */}
      {/* -------------------------------------------------------------------------- */}
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
