import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Sparkles,
  TrendingUp,
  Clock,
  Calendar,
  Users,
  Target,
  ShieldAlert,
  Zap,
  Info,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  HelpCircle,
  Percent,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Sliders,
  DollarSign,
  ChevronRight,
  Award,
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { apiClient } from "../../../shared/apiClient";
import { getErrorMessage } from "../../../shared/utils/errorHandler";

const DONUT_COLORS = ["#10B981", "#6366F1", "#EC4899", "#F59E0B", "#8B5CF6"];

export const MarketingInsightsPanel = ({ productId, productName, category }) => {
  const [datePreset, setDatePreset] = useState("30d");
  const [customBenchmarkPrice, setCustomBenchmarkPrice] = useState("");

  // Calculate start/end date query params based on preset
  const dateParams = useMemo(() => {
    const end = new Date();
    const start = new Date();
    if (datePreset === "7d") {
      start.setDate(end.getDate() - 7);
    } else if (datePreset === "60d") {
      start.setDate(end.getDate() - 60);
    } else if (datePreset === "90d") {
      start.setDate(end.getDate() - 90);
    } else {
      // default 30d
      start.setDate(end.getDate() - 30);
    }
    return {
      start_date: start.toISOString().split("T")[0],
      end_date: end.toISOString().split("T")[0],
    };
  }, [datePreset]);

  // Fetch Marketing Insights Data
  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ["marketingInsights", productId, dateParams.start_date, dateParams.end_date],
    queryFn: async () => {
      const res = await apiClient.get(
        `products/${productId}/marketing-insights?start_date=${dateParams.start_date}&end_date=${dateParams.end_date}`
      );
      return res.data;
    },
    enabled: !!productId,
    staleTime: 60000,
  });

  const formatCurrency = (val) => {
    const rounded = Math.round(Number(val) || 0);
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
      minimumFractionDigits: 0,
    }).format(rounded);
  };

  const isRuleBased = data?.generation_mode === "RULE_BASED_FALLBACK";

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "16px", padding: "8px 0" }}>
        <div className="skeleton-card" style={{ height: "120px" }} />
        <div className="skeleton-card" style={{ height: "200px" }} />
        <div className="skeleton-card" style={{ height: "180px" }} />
        <div className="skeleton-card" style={{ height: "160px" }} />
      </div>
    );
  }

  if (error) {
    return (
      <div
        role="alert"
        style={{
          padding: "24px",
          backgroundColor: "rgba(239, 68, 68, 0.05)",
          border: "1px solid rgba(239, 68, 68, 0.2)",
          borderRadius: "var(--radius-card)",
          textAlign: "center",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "12px",
          margin: "12px 0",
        }}
      >
        <AlertCircle size={28} style={{ color: "#EF4444" }} />
        <div>
          <h5 style={{ fontSize: "14px", fontWeight: 700, margin: "0 0 4px 0", color: "var(--gray-text-primary)" }}>
            Unable to Load Marketing Insights
          </h5>
          <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0 }}>
            {getErrorMessage(error, "Failed to compute sales aggregates and strategic recommendations.")}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="btn btn-secondary"
          style={{ fontSize: "12px", padding: "6px 14px", display: "inline-flex", alignItems: "center", gap: "6px" }}
        >
          <RefreshCw size={13} className={isRefetching ? "spin-clockwise" : ""} />
          {isRefetching ? "Retrying..." : "Retry Insights"}
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-5)", paddingBottom: "24px" }}>
      
      {/* 0. Top Controls & Truthful Sourcing Badges */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "12px",
          padding: "12px 16px",
          background: "linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%)",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
        }}
      >
        {/* Sourcing Badges */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
          <span
            className="badge badge-success"
            title="Aggregated from real transactional sales data in your catalog"
            style={{ display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "11px", fontWeight: 600 }}
          >
            <CheckCircle2 size={12} /> Real Telemetry Sourced
          </span>

          {isRuleBased ? (
            <span
              className="badge"
              title="Deterministic inference engine active (LLM API offline or unconfigured)"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                fontSize: "11px",
                fontWeight: 600,
                backgroundColor: "rgba(245, 158, 11, 0.12)",
                color: "#D97706",
                border: "1px solid rgba(245, 158, 11, 0.3)",
              }}
            >
              <ShieldAlert size={12} /> Deterministic Rule-Based Estimate
            </span>
          ) : (
            <span
              className="badge badge-purple"
              title="Generated via structured AI LLM reasoning with upload-level cache"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                fontSize: "11px",
                fontWeight: 600,
                background: "linear-gradient(135deg, #6366F1 0%, #A855F7 100%)",
                color: "#FFFFFF",
              }}
            >
              <Sparkles size={12} /> AI-Generated Strategic Insight
            </span>
          )}

          {data.is_cached && (
            <span
              style={{
                fontSize: "10px",
                color: "var(--gray-text-muted)",
                background: "rgba(0,0,0,0.04)",
                padding: "2px 6px",
                borderRadius: "4px",
              }}
            >
              Cached (24h)
            </span>
          )}
        </div>

        {/* Date Window Presets & Refresh */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div
            style={{
              display: "flex",
              background: "var(--gray-surface)",
              border: "1px solid var(--gray-border)",
              borderRadius: "var(--radius-input)",
              padding: "2px",
            }}
          >
            {["7d", "30d", "60d"].map((preset) => (
              <button
                key={preset}
                onClick={() => setDatePreset(preset)}
                style={{
                  padding: "4px 10px",
                  fontSize: "11px",
                  fontWeight: 600,
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  backgroundColor: datePreset === preset ? "var(--accent)" : "transparent",
                  color: datePreset === preset ? "#FFFFFF" : "var(--gray-text-muted)",
                  transition: "all 0.15s ease",
                }}
              >
                {preset.toUpperCase()}
              </button>
            ))}
          </div>

          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="btn btn-secondary"
            title="Refresh Insights"
            style={{ padding: "6px 10px", fontSize: "11px" }}
          >
            <RefreshCw size={12} className={isRefetching ? "spin-clockwise" : ""} />
          </button>
        </div>
      </div>

      {/* 1. SECTION: Price Psychology & Elasticity Card */}
      {data.price_psychology && (
        <div className="card" style={{ padding: "16px", position: "relative", overflow: "hidden" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div
                style={{
                  width: "28px",
                  height: "28px",
                  borderRadius: "8px",
                  backgroundColor: "rgba(99, 102, 241, 0.1)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--accent)",
                }}
              >
                <Percent size={16} />
              </div>
              <div>
                <h4 style={{ fontSize: "14px", fontWeight: 700, margin: 0 }}>Price Psychology & Positioning</h4>
                <p style={{ fontSize: "11px", color: "var(--gray-text-muted)", margin: 0 }}>
                  Willingness-to-pay elasticity & consumer psychological threshold
                </p>
              </div>
            </div>

            {data.price_psychology.charm_pricing_flag && (
              <span className="badge badge-purple" style={{ fontSize: "10px", fontWeight: 600 }}>
                .99 Charm Pricing Active
              </span>
            )}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
              gap: "12px",
              marginBottom: "14px",
            }}
          >
            <div
              style={{
                padding: "10px 12px",
                background: "var(--gray-bg)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>Active Price</span>
              <span style={{ fontSize: "18px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
                {formatCurrency(data.price_psychology.current_price)}
              </span>
            </div>

            <div
              style={{
                padding: "10px 12px",
                background: "var(--gray-bg)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>Baseline / MSRP</span>
              <span style={{ fontSize: "18px", fontWeight: 700, color: "var(--gray-text-muted)", textDecoration: "line-through" }}>
                {formatCurrency(data.price_psychology.original_price)}
              </span>
            </div>

            <div
              style={{
                padding: "10px 12px",
                background: "rgba(16, 185, 129, 0.06)",
                borderRadius: "var(--radius-default)",
                border: "1px solid rgba(16, 185, 129, 0.2)",
              }}
            >
              <span style={{ fontSize: "11px", color: "#059669", display: "block" }}>Discount Depth</span>
              <span style={{ fontSize: "18px", fontWeight: 800, color: "#10B981" }}>
                {data.price_psychology.discount_pct}% OFF
              </span>
            </div>

            <div
              style={{
                padding: "10px 12px",
                background: "var(--gray-bg)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>Elasticity Score</span>
              <span style={{ fontSize: "18px", fontWeight: 700, color: "var(--gray-text-primary)" }}>
                {data.price_psychology.price_elasticity_score?.toFixed(2) || "1.20"}
              </span>
            </div>
          </div>

          <div
            style={{
              padding: "10px 14px",
              background: "rgba(99, 102, 241, 0.05)",
              borderLeft: "3px solid var(--accent)",
              borderRadius: "0 var(--radius-default) var(--radius-default) 0",
              fontSize: "12px",
              color: "var(--gray-text-primary)",
              lineHeight: 1.4,
            }}
          >
            <span style={{ fontWeight: 600, color: "var(--accent)" }}>Positioning Diagnosis: </span>
            {data.price_psychology.positioning_note}
          </div>
        </div>
      )}

      {/* 2. SECTION: 30-Day Sales Trend (Line/Area Chart) */}
      <div className="card" style={{ padding: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <TrendingUp size={16} style={{ color: "var(--accent)" }} />
            <h4 style={{ fontSize: "14px", fontWeight: 700, margin: 0 }}>30-Day Daily Sales Velocity</h4>
          </div>
          <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
            Total Units: {data.sales_trend_30d.reduce((acc, p) => acc + p.units_sold, 0)}
          </span>
        </div>

        <div style={{ width: "100%", height: "180px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data.sales_trend_30d} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="marketingTrendGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="date"
                stroke="var(--gray-text-muted)"
                fontSize={10}
                tickLine={false}
                tickFormatter={(val) => {
                  try {
                    const d = new Date(val);
                    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
                  } catch {
                    return val;
                  }
                }}
              />
              <YAxis stroke="var(--gray-text-muted)" fontSize={10} tickLine={false} allowDecimals={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div
                        style={{
                          background: "#0F172A",
                          color: "#FFFFFF",
                          padding: "8px 12px",
                          borderRadius: "8px",
                          fontSize: "12px",
                          boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
                        }}
                      >
                        <p style={{ fontWeight: 700, marginBottom: "4px" }}>{d.date}</p>
                        <p style={{ color: "#818CF8", margin: 0 }}>Units Sold: <b>{d.units_sold}</b></p>
                        <p style={{ color: "#34D399", margin: 0 }}>Revenue: <b>{formatCurrency(d.revenue)}</b></p>
                        <p style={{ color: "#94A3B8", margin: 0, fontSize: "11px" }}>Avg Price: {formatCurrency(d.avg_selling_price)}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="units_sold"
                stroke="#6366F1"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#marketingTrendGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 3 & 4. SECTION: Day of Week & Price Range Distribution Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
        
        {/* 3. Sales by Day of Week BarChart */}
        <div className="card" style={{ padding: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Calendar size={16} style={{ color: "#10B981" }} />
              <h4 style={{ fontSize: "13px", fontWeight: 700, margin: 0 }}>Sales by Day of Week</h4>
            </div>
            <span style={{ fontSize: "10px", color: "var(--gray-text-muted)" }}>0=Mon .. 6=Sun</span>
          </div>

          <div style={{ width: "100%", height: "160px" }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.sales_by_day_of_week} margin={{ top: 5, right: 5, left: -15, bottom: 0 }}>
                <XAxis dataKey="day_name" stroke="var(--gray-text-muted)" fontSize={10} tickLine={false} />
                <YAxis stroke="var(--gray-text-muted)" fontSize={10} tickLine={false} allowDecimals={false} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div
                          style={{
                            background: "#0F172A",
                            color: "#FFFFFF",
                            padding: "8px 12px",
                            borderRadius: "8px",
                            fontSize: "12px",
                          }}
                        >
                          <p style={{ fontWeight: 700, marginBottom: "2px" }}>{d.day_name}</p>
                          <p style={{ color: "#34D399", margin: 0 }}>Total Units: <b>{d.total_units_sold}</b></p>
                          <p style={{ color: "#818CF8", margin: 0 }}>Avg Units/Day: <b>{d.avg_units_per_day}</b></p>
                          <p style={{ color: "#FCD34D", margin: 0 }}>Revenue Share: <b>{d.revenue_share_pct}%</b></p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="total_units_sold" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Sales by Price Range Donut/Pie Chart */}
        <div className="card" style={{ padding: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Layers size={16} style={{ color: "#EC4899" }} />
              <h4 style={{ fontSize: "13px", fontWeight: 700, margin: 0 }}>Sales by Price Range</h4>
            </div>
            <span style={{ fontSize: "10px", color: "var(--gray-text-muted)" }}>Volume Distribution</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", height: "160px" }}>
            <div style={{ width: "50%", height: "100%" }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.sales_by_price_range}
                    dataKey="units_sold"
                    nameKey="bucket_label"
                    cx="50%"
                    cy="50%"
                    innerRadius={35}
                    outerRadius={58}
                    paddingAngle={3}
                  >
                    {data.sales_by_price_range.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={DONUT_COLORS[index % DONUT_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const d = payload[0].payload;
                        return (
                          <div
                            style={{
                              background: "#0F172A",
                              color: "#FFFFFF",
                              padding: "6px 10px",
                              borderRadius: "6px",
                              fontSize: "11px",
                            }}
                          >
                            <p style={{ fontWeight: 700, margin: 0 }}>{d.bucket_label}</p>
                            <p style={{ margin: "2px 0 0 0" }}>Units: {d.units_sold} ({d.percentage_of_total}%)</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div style={{ width: "50%", display: "flex", flexDirection: "column", gap: "6px" }}>
              {data.sales_by_price_range.map((b, idx) => (
                <div key={idx} style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px" }}>
                  <div
                    style={{
                      width: "8px",
                      height: "8px",
                      borderRadius: "50%",
                      backgroundColor: DONUT_COLORS[idx % DONUT_COLORS.length],
                      flexShrink: 0,
                    }}
                  />
                  <div style={{ minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    <span style={{ color: "var(--gray-text-primary)", fontWeight: 600 }}>{b.percentage_of_total}%</span>{" "}
                    <span style={{ color: "var(--gray-text-muted)" }}>{b.bucket_label.split(" (")[0]}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* 5. SECTION: Top Marketing Recommendations */}
      <div className="card" style={{ padding: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "14px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Award size={16} style={{ color: "var(--accent)" }} />
            <h4 style={{ fontSize: "14px", fontWeight: 700, margin: 0 }}>Strategic Marketing Recommendations</h4>
          </div>
          <span className="badge badge-purple" style={{ fontSize: "10px" }}>
            {data.recommendations.length} Action Items
          </span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {data.recommendations.map((rec) => (
            <div
              key={rec.id}
              style={{
                padding: "12px 14px",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
                backgroundColor: "var(--gray-bg)",
                display: "flex",
                flexDirection: "column",
                gap: "6px",
                transition: "all 0.15s ease",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                <h5 style={{ fontSize: "13px", fontWeight: 700, color: "var(--gray-text-primary)", margin: 0 }}>
                  {rec.title}
                </h5>
                <span
                  className={rec.impact === "HIGH" ? "badge badge-danger" : "badge badge-warning"}
                  style={{ fontSize: "10px", fontWeight: 700, flexShrink: 0 }}
                >
                  {rec.impact} IMPACT
                </span>
              </div>

              <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0, lineHeight: 1.4 }}>
                {rec.action_summary}
              </p>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginTop: "4px",
                  paddingTop: "6px",
                  borderTop: "1px dashed var(--gray-border)",
                  fontSize: "11px",
                }}
              >
                <div style={{ display: "flex", gap: "12px", color: "var(--gray-text-muted)" }}>
                  <span>
                    Channel: <b style={{ color: "var(--gray-text-primary)" }}>{rec.channel}</b>
                  </span>
                  <span>
                    Window: <b style={{ color: "var(--gray-text-primary)" }}>{rec.timing}</b>
                  </span>
                </div>
                <span style={{ color: "var(--accent)", fontWeight: 600 }}>
                  Expected: {rec.expected_outcome}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 6 & 7. SECTION: Promotion Timing & Inferred Audience Profile Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "16px" }}>
        
        {/* 6. Best Time to Promote */}
        {data.promotion_timing && (
          <div className="card" style={{ padding: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <Clock size={16} style={{ color: "#F59E0B" }} />
              <h4 style={{ fontSize: "13px", fontWeight: 700, margin: 0 }}>Best Time to Promote</h4>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "8px 10px",
                  background: "rgba(245, 158, 11, 0.08)",
                  borderRadius: "6px",
                }}
              >
                <span style={{ fontSize: "11px", color: "#D97706", fontWeight: 600 }}>Velocity Multiplier</span>
                <span style={{ fontSize: "13px", fontWeight: 800, color: "#D97706" }}>
                  {data.promotion_timing.promo_velocity_multiplier}x
                </span>
              </div>

              <div style={{ fontSize: "12px" }}>
                <span style={{ color: "var(--gray-text-muted)", display: "block", fontSize: "11px" }}>Peak Days:</span>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "4px" }}>
                  {data.promotion_timing.best_days.map((day, i) => (
                    <span key={i} className="badge badge-info" style={{ fontSize: "10px" }}>
                      {day}
                    </span>
                  ))}
                </div>
              </div>

              <div style={{ fontSize: "12px" }}>
                <span style={{ color: "var(--gray-text-muted)", display: "block", fontSize: "11px" }}>Hourly Windows:</span>
                <span style={{ fontWeight: 600, color: "var(--gray-text-primary)" }}>
                  {data.promotion_timing.best_time_window}
                </span>
              </div>

              <div style={{ fontSize: "12px" }}>
                <span style={{ color: "var(--gray-text-muted)", display: "block", fontSize: "11px" }}>Seasonality:</span>
                <span style={{ fontWeight: 600, color: "var(--gray-text-primary)" }}>
                  {data.promotion_timing.peak_season}
                </span>
              </div>

              <p style={{ fontSize: "11px", color: "var(--gray-text-muted)", margin: 0, fontStyle: "italic" }}>
                {data.promotion_timing.timing_rationale}
              </p>
            </div>
          </div>
        )}

        {/* 7. Inferred Audience Profile */}
        {data.audience_profile && (
          <div className="card" style={{ padding: "16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
              <Users size={16} style={{ color: "#6366F1" }} />
              <h4 style={{ fontSize: "13px", fontWeight: 700, margin: 0 }}>Inferred Buyer Demographics</h4>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div style={{ fontSize: "12px" }}>
                <span style={{ color: "var(--gray-text-muted)", display: "block", fontSize: "11px" }}>Primary Segment:</span>
                <span style={{ fontWeight: 700, color: "var(--gray-text-primary)" }}>
                  {data.audience_profile.primary_users}
                </span>
                <span style={{ fontSize: "11px", color: "var(--gray-text-muted)", display: "block" }}>
                  Age: {data.audience_profile.age_group} • {data.audience_profile.location_tier}
                </span>
              </div>

              <div style={{ fontSize: "12px" }}>
                <span style={{ color: "var(--gray-text-muted)", display: "block", fontSize: "11px" }}>Purchase Triggers:</span>
                <div style={{ display: "flex", gap: "4px", flexWrap: "wrap", marginTop: "4px" }}>
                  {data.audience_profile.purchase_triggers.map((t, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: "10px",
                        background: "var(--gray-bg)",
                        border: "1px solid var(--gray-border)",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        color: "var(--gray-text-primary)",
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <p
                style={{
                  fontSize: "11px",
                  color: "var(--gray-text-muted)",
                  margin: 0,
                  lineHeight: 1.4,
                  background: "var(--gray-bg)",
                  padding: "8px",
                  borderRadius: "6px",
                }}
              >
                "{data.audience_profile.persona_summary}"
              </p>
            </div>
          </div>
        )}

      </div>

      {/* 8. SECTION: Competitor Price Benchmark (with Interactive Estimator) */}
      {data.competitor_benchmark && (
        <div className="card" style={{ padding: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Target size={16} style={{ color: "var(--accent)" }} />
              <div>
                <h4 style={{ fontSize: "14px", fontWeight: 700, margin: 0 }}>Competitor Price Benchmark</h4>
                <p style={{ fontSize: "11px", color: "var(--gray-text-muted)", margin: 0 }}>
                  Estimated competitive tiering & position index
                </p>
              </div>
            </div>

            <span
              className={
                data.competitor_benchmark.overall_position === "COMPETITIVE"
                  ? "badge badge-success"
                  : data.competitor_benchmark.overall_position === "PREMIUM"
                  ? "badge badge-purple"
                  : "badge badge-info"
              }
              style={{ fontSize: "10px", fontWeight: 700 }}
            >
              {data.competitor_benchmark.overall_position} POSITION
            </span>
          </div>

          {/* Sourcing Disclaimer Banner */}
          <div
            style={{
              padding: "8px 12px",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.2)",
              borderRadius: "6px",
              fontSize: "11px",
              color: "#D97706",
              marginBottom: "12px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Info size={14} style={{ flexShrink: 0 }} />
            <span>{data.competitor_benchmark.disclaimer}</span>
          </div>

          {/* Benchmark Table */}
          <div style={{ overflowX: "auto", marginBottom: "14px" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--gray-border)", textAlign: "left", color: "var(--gray-text-muted)" }}>
                  <th style={{ padding: "6px 8px", fontWeight: 600 }}>Channel / Competitor</th>
                  <th style={{ padding: "6px 8px", fontWeight: 600 }}>Est. Price</th>
                  <th style={{ padding: "6px 8px", fontWeight: 600 }}>Delta vs Your SKU</th>
                  <th style={{ padding: "6px 8px", fontWeight: 600 }}>Position</th>
                </tr>
              </thead>
              <tbody>
                {data.competitor_benchmark.rows.map((row, idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid var(--gray-border)" }}>
                    <td style={{ padding: "8px", fontWeight: 600, color: "var(--gray-text-primary)" }}>
                      {row.competitor_name}
                    </td>
                    <td style={{ padding: "8px", fontFamily: "var(--font-mono)", color: "var(--gray-text-primary)" }}>
                      {formatCurrency(row.estimated_price)}
                    </td>
                    <td style={{ padding: "8px" }}>
                      <span
                        style={{
                          color: row.price_difference_pct > 0 ? "#10B981" : row.price_difference_pct < 0 ? "#EF4444" : "inherit",
                          fontWeight: 600,
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "2px",
                        }}
                      >
                        {row.price_difference_pct > 0 ? (
                          <ArrowUpRight size={13} />
                        ) : row.price_difference_pct < 0 ? (
                          <ArrowDownRight size={13} />
                        ) : null}
                        {row.price_difference_pct > 0 ? `+${row.price_difference_pct}%` : `${row.price_difference_pct}%`}
                      </span>
                    </td>
                    <td style={{ padding: "8px" }}>
                      <span
                        style={{
                          fontSize: "10px",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontWeight: 600,
                          backgroundColor:
                            row.positioning === "BELOW"
                              ? "rgba(239, 68, 68, 0.1)"
                              : row.positioning === "ABOVE"
                              ? "rgba(16, 185, 129, 0.1)"
                              : "rgba(99, 102, 241, 0.1)",
                          color:
                            row.positioning === "BELOW"
                              ? "#EF4444"
                              : row.positioning === "ABOVE"
                              ? "#10B981"
                              : "var(--accent)",
                        }}
                      >
                        {row.positioning}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Interactive Benchmark Sandbox */}
          <div
            style={{
              padding: "10px 12px",
              background: "var(--gray-bg)",
              borderRadius: "var(--radius-default)",
              border: "1px dashed var(--gray-border)",
              display: "flex",
              alignItems: "center",
              gap: "10px",
              flexWrap: "wrap",
            }}
          >
            <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              Simulate Price Parity:
            </span>
            <input
              type="number"
              placeholder="Enter competitor price (₹)..."
              value={customBenchmarkPrice}
              onChange={(e) => setCustomBenchmarkPrice(e.target.value)}
              style={{
                padding: "4px 8px",
                fontSize: "11px",
                borderRadius: "var(--radius-input)",
                border: "1px solid var(--gray-border)",
                width: "160px",
              }}
            />
            {customBenchmarkPrice && data.price_psychology && (
              <span style={{ fontSize: "11px", fontWeight: 600 }}>
                Delta:{" "}
                <span
                  style={{
                    color:
                      Number(customBenchmarkPrice) > data.price_psychology.current_price
                        ? "#10B981"
                        : "#EF4444",
                  }}
                >
                  {(
                    ((Number(customBenchmarkPrice) - data.price_psychology.current_price) /
                      data.price_psychology.current_price) *
                    100
                  ).toFixed(1)}
                  %
                </span>{" "}
                ({Number(customBenchmarkPrice) > data.price_psychology.current_price ? "You are Cheaper" : "You are Higher"})
              </span>
            )}
          </div>
        </div>
      )}

      {/* 9. SECTION: Risks & Watchouts */}
      {data.risks_watchouts && data.risks_watchouts.length > 0 && (
        <div className="card" style={{ padding: "16px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
            <ShieldAlert size={16} style={{ color: "#EF4444" }} />
            <h4 style={{ fontSize: "14px", fontWeight: 700, margin: 0 }}>Campaign Risks & Watchouts</h4>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {data.risks_watchouts.map((risk, i) => (
              <div
                key={i}
                style={{
                  padding: "10px 12px",
                  borderRadius: "6px",
                  border: risk.severity === "CRITICAL"
                    ? "1px solid rgba(239, 68, 68, 0.3)"
                    : "1px solid rgba(245, 158, 11, 0.25)",
                  backgroundColor: risk.severity === "CRITICAL"
                    ? "rgba(239, 68, 68, 0.04)"
                    : "rgba(245, 158, 11, 0.04)",
                  fontSize: "12px",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2px" }}>
                  <span
                    style={{
                      fontWeight: 700,
                      color: risk.severity === "CRITICAL" ? "#EF4444" : "#D97706",
                    }}
                  >
                    {risk.title}
                  </span>
                  <span
                    style={{
                      fontSize: "9px",
                      fontWeight: 700,
                      padding: "1px 5px",
                      borderRadius: "4px",
                      backgroundColor: risk.severity === "CRITICAL" ? "#EF4444" : "#D97706",
                      color: "#FFFFFF",
                    }}
                  >
                    {risk.severity}
                  </span>
                </div>
                <p style={{ color: "var(--gray-text-primary)", margin: "0 0 4px 0", lineHeight: 1.3 }}>
                  {risk.description}
                </p>
                <p style={{ color: "var(--gray-text-muted)", margin: 0, fontSize: "11px" }}>
                  <b>Mitigation:</b> {risk.mitigation}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 10. SECTION: Expected 30-Day Impact Matrix */}
      {data.expected_impact_30d && (
        <div
          className="card"
          style={{
            padding: "16px",
            background: "linear-gradient(135deg, rgba(79, 70, 229, 0.04) 0%, rgba(16, 185, 129, 0.04) 100%)",
            border: "1px solid var(--accent)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px" }}>
            <Zap size={16} style={{ color: "var(--accent)" }} />
            <div>
              <h4 style={{ fontSize: "14px", fontWeight: 700, margin: 0 }}>Projected 30-Day Campaign Impact</h4>
              <p style={{ fontSize: "11px", color: "var(--gray-text-muted)", margin: 0 }}>
                Estimated uplift from promotional timing & dynamic price optimization
              </p>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
              gap: "12px",
              marginBottom: "12px",
            }}
          >
            <div
              style={{
                padding: "10px",
                background: "var(--gray-surface)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>Revenue Uplift</span>
              <span style={{ fontSize: "16px", fontWeight: 800, color: "#10B981" }}>
                {data.expected_impact_30d.revenue_uplift_pct_range}
              </span>
            </div>

            <div
              style={{
                padding: "10px",
                background: "var(--gray-surface)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>Volume Expansion</span>
              <span style={{ fontSize: "16px", fontWeight: 800, color: "var(--accent)" }}>
                {data.expected_impact_30d.units_sold_range}
              </span>
            </div>

            <div
              style={{
                padding: "10px",
                background: "var(--gray-surface)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>Conversion Rate</span>
              <span style={{ fontSize: "16px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
                {data.expected_impact_30d.conversion_rate_range}
              </span>
            </div>

            <div
              style={{
                padding: "10px",
                background: "var(--gray-surface)",
                borderRadius: "var(--radius-default)",
                border: "1px solid var(--gray-border)",
              }}
            >
              <span style={{ fontSize: "10px", color: "var(--gray-text-muted)", display: "block" }}>Target ROAS</span>
              <span style={{ fontSize: "16px", fontWeight: 800, color: "#F59E0B" }}>
                {data.expected_impact_30d.roi_range}
              </span>
            </div>
          </div>

          <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", margin: 0, lineHeight: 1.4 }}>
            💡 {data.expected_impact_30d.summary_note}
          </p>
        </div>
      )}

    </div>
  );
};
