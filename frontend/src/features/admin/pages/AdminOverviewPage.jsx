import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Users,
  UserCheck,
  UserX,
  UserPlus,
  Database,
  Layers,
  AlertOctagon,
  Activity,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileSpreadsheet,
  Clock,
  TrendingUp,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import { apiClient } from "../../../shared/apiClient";
import { formatInteger } from "../../../shared/utils/formatters";

export const AdminOverviewPage = () => {
  const { data: overview, isLoading, error } = useQuery({
    queryKey: ["adminOverview"],
    queryFn: async () => {
      const res = await apiClient.get("admin/overview");
      return res.data;
    },
    refetchInterval: 30000,
  });

  const formatChartDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--space-4)" }}>
          {[...Array(8)].map((_, i) => (
            <div key={i} className="skeleton-card" style={{ height: "100px" }} />
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "var(--space-5)" }}>
          <div className="skeleton-card" style={{ height: "300px" }} />
          <div className="skeleton-card" style={{ height: "300px" }} />
        </div>
      </div>
    );
  }

  if (error || !overview) {
    return (
      <div className="card" style={{ padding: "var(--space-6)", textAlign: "center" }}>
        <AlertTriangle size={32} style={{ color: "var(--error)", margin: "0 auto var(--space-3)" }} />
        <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Failed to Load Admin Overview</h3>
        <p style={{ fontSize: "13px", color: "var(--gray-text-muted)" }}>
          Please verify your administrator permissions and try again.
        </p>
      </div>
    );
  }

  const {
    total_retailers,
    active_retailers,
    disabled_retailers,
    new_retailers_30d,
    total_datasets,
    total_sales_records,
    failed_uploads,
    processing_uploads,
    platform_health_status,
    retailer_growth_30d = [],
    upload_breakdown = {},
    recent_activity = [],
  } = overview;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "var(--space-3)" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span className="badge badge-primary" style={{ fontSize: "11px", fontWeight: 700 }}>
              SaaS Administration
            </span>
            <span
              className={`badge ${
                platform_health_status === "HEALTHY"
                  ? "badge-success"
                  : platform_health_status === "DEGRADED"
                  ? "badge-warning"
                  : "badge-danger"
              }`}
              style={{ fontSize: "11px", fontWeight: 700 }}
            >
              ● Platform {platform_health_status}
            </span>
          </div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)", margin: 0 }}>
            Platform Overview & Operations
          </h1>
        </div>

        <div style={{ display: "flex", gap: "var(--space-2)" }}>
          <Link to="/admin/retailers" className="btn btn-secondary" style={{ height: "36px", fontSize: "12px" }}>
            <Users size={14} />
            Manage Retailers
          </Link>
          <Link to="/admin/data-operations" className="btn btn-primary" style={{ height: "36px", fontSize: "12px" }}>
            <Database size={14} />
            Data Operations
          </Link>
        </div>
      </div>

      {/* 8 Primary SaaS KPI Cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "var(--space-4)",
        }}
      >
        {/* 1. Total Retailers */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Total Retailers</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#EEF2FF", color: "var(--accent)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Users size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatInteger(total_retailers)}
          </div>
        </div>

        {/* 2. Active Retailers */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Active Accounts</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#F0FDF4", color: "var(--success)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserCheck size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--success)" }}>
            {formatInteger(active_retailers)}
          </div>
        </div>

        {/* 3. Disabled Accounts */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Disabled Accounts</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#FEF2F2", color: "var(--error)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserX size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: disabled_retailers > 0 ? "var(--error)" : "var(--gray-text-primary)" }}>
            {formatInteger(disabled_retailers)}
          </div>
        </div>

        {/* 4. New Retailers (30D) */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>New Retailers (30D)</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#F5F3FF", color: "var(--purple)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <UserPlus size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--purple)" }}>
            +{formatInteger(new_retailers_30d)}
          </div>
        </div>

        {/* 5. Total Datasets Processed */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Total Datasets</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#EFF6FF", color: "#2563EB", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Database size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatInteger(total_datasets)}
          </div>
        </div>

        {/* 6. Total Sales Records */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Total Sales Records</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#ECFDF5", color: "#059669", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Layers size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatInteger(total_sales_records)}
          </div>
        </div>

        {/* 7. Processing Failures */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Processing Failures</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#FFF1F2", color: "#E11D48", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <AlertOctagon size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: failed_uploads > 0 ? "var(--error)" : "var(--gray-text-primary)" }}>
            {formatInteger(failed_uploads)}
          </div>
        </div>

        {/* 8. Active Ingestion Jobs */}
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--gray-text-muted)" }}>Active Pipeline Jobs</span>
            <div style={{ width: "32px", height: "32px", borderRadius: "8px", backgroundColor: "#FFFBEB", color: "#D97706", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Activity size={16} />
            </div>
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: processing_uploads > 0 ? "var(--warning)" : "var(--gray-text-primary)" }}>
            {formatInteger(processing_uploads)}
          </div>
        </div>
      </div>

      {/* 2 Column Operations Grid: 30D Growth Chart & Ingestion Status */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "var(--space-5)" }}>
        {/* Retailer Growth Chart */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <TrendingUp size={18} style={{ color: "var(--accent)" }} />
              <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Retailer Growth (Last 30 Days)</h3>
            </div>
            <span className="badge badge-info" style={{ fontSize: "11px" }}>
              +{new_retailers_30d} New Accounts
            </span>
          </div>

          <div style={{ width: "100%", height: "240px" }}>
            {retailer_growth_30d.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={retailer_growth_30d} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="date" tickFormatter={formatChartDate} stroke="#94A3B8" style={{ fontSize: "11px" }} />
                  <YAxis allowDecimals={false} stroke="#94A3B8" style={{ fontSize: "11px" }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "var(--gray-surface)", borderColor: "var(--gray-border)", borderRadius: "var(--radius-default)", fontSize: "12px" }}
                    formatter={(value) => [`${value} new retailer(s)`, "Registrations"]}
                    labelFormatter={(label) => formatChartDate(label)}
                  />
                  <Bar dataKey="new_retailers" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "var(--gray-text-muted)" }}>
                No registrations recorded in the last 30 days.
              </div>
            )}
          </div>
        </div>

        {/* Dataset Ingestion Summary Breakdown */}
        <div className="card" style={{ padding: "var(--space-5)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Database size={18} style={{ color: "var(--purple)" }} />
              <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Data Processing Breakdown</h3>
            </div>
            <Link to="/admin/data-operations" style={{ fontSize: "12px", color: "var(--accent)", textDecoration: "none", fontWeight: 600 }}>
              View Ingestion Monitor →
            </Link>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-4)" }}>
            {/* Visual Bar */}
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", marginBottom: "6px" }}>
                <span style={{ color: "var(--gray-text-muted)" }}>Job Success Rate</span>
                <strong style={{ color: "var(--success)" }}>
                  {total_datasets > 0 ? Math.round((upload_breakdown.completed / total_datasets) * 100) : 100}% Completed
                </strong>
              </div>
              <div style={{ display: "flex", height: "10px", borderRadius: "5px", overflow: "hidden", backgroundColor: "var(--gray-border)" }}>
                <div style={{ width: `${total_datasets > 0 ? (upload_breakdown.completed / total_datasets) * 100 : 0}%`, backgroundColor: "var(--success)" }} />
                <div style={{ width: `${total_datasets > 0 ? (upload_breakdown.processing / total_datasets) * 100 : 0}%`, backgroundColor: "var(--warning)" }} />
                <div style={{ width: `${total_datasets > 0 ? (upload_breakdown.failed / total_datasets) * 100 : 0}%`, backgroundColor: "var(--error)" }} />
              </div>
            </div>

            {/* Metrics List */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "var(--space-3)", textAlign: "center" }}>
              <div style={{ padding: "var(--space-3)", backgroundColor: "#F0FDF4", borderRadius: "var(--radius-default)" }}>
                <div style={{ fontSize: "11px", color: "#166534", fontWeight: 600 }}>Completed</div>
                <div style={{ fontSize: "18px", fontWeight: 800, color: "var(--success)" }}>
                  {formatInteger(upload_breakdown.completed || 0)}
                </div>
              </div>
              <div style={{ padding: "var(--space-3)", backgroundColor: "#FFFBEB", borderRadius: "var(--radius-default)" }}>
                <div style={{ fontSize: "11px", color: "#92400E", fontWeight: 600 }}>Processing</div>
                <div style={{ fontSize: "18px", fontWeight: 800, color: "var(--warning)" }}>
                  {formatInteger(upload_breakdown.processing || 0)}
                </div>
              </div>
              <div style={{ padding: "var(--space-3)", backgroundColor: "#FEF2F2", borderRadius: "var(--radius-default)" }}>
                <div style={{ fontSize: "11px", color: "#991B1B", fontWeight: 600 }}>Failed</div>
                <div style={{ fontSize: "18px", fontWeight: 800, color: "var(--error)" }}>
                  {formatInteger(upload_breakdown.failed || 0)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Platform Activity Stream */}
      <div className="card" style={{ padding: "var(--space-5)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Clock size={18} style={{ color: "var(--accent)" }} />
            <h3 style={{ fontSize: "16px", fontWeight: 700, margin: 0 }}>Recent Platform Activity</h3>
          </div>
          <Link to="/admin/activity-log" style={{ fontSize: "12px", color: "var(--accent)", textDecoration: "none", fontWeight: 600 }}>
            Full Audit Log →
          </Link>
        </div>

        {recent_activity.length === 0 ? (
          <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--gray-text-muted)", fontSize: "13px" }}>
            No platform activity recorded yet.
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
            {recent_activity.map((item) => (
              <div
                key={item.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-3) var(--space-4)",
                  backgroundColor: "var(--gray-surface)",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid var(--gray-border)",
                  fontSize: "13px",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                  <span
                    className={`badge ${
                      item.status === "SUCCESS" || item.status === "COMPLETED"
                        ? "badge-success"
                        : item.status === "FAILED"
                        ? "badge-danger"
                        : "badge-info"
                    }`}
                    style={{ fontSize: "10px", fontWeight: 700 }}
                  >
                    {item.action}
                  </span>
                  <span style={{ color: "var(--gray-text-primary)" }}>{item.description}</span>
                </div>
                <span style={{ color: "var(--gray-text-muted)", fontSize: "12px", whiteSpace: "nowrap" }}>
                  {formatDate(item.timestamp)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
