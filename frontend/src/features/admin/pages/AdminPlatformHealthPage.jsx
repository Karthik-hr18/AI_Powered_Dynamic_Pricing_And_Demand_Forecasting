import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  Server,
  Database,
  Cpu,
  Layers,
  ShieldCheck,
  Clock,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";

export const AdminPlatformHealthPage = () => {
  const {
    data: healthData,
    isLoading,
    isRefetching,
    refetch,
    error,
  } = useQuery({
    queryKey: ["adminPlatformHealth"],
    queryFn: async () => {
      const res = await apiClient.get("admin/platform-health");
      return res.data;
    },
    refetchInterval: 30000,
  });

  const getServiceIcon = (name) => {
    if (name.includes("API")) return <Server size={20} />;
    if (name.includes("MongoDB") || name.includes("Database")) return <Database size={20} />;
    if (name.includes("Worker")) return <Layers size={20} />;
    if (name.includes("ML") || name.includes("Engine")) return <Cpu size={20} />;
    return <Activity size={20} />;
  };

  const renderStatusBadge = (status) => {
    if (status === "HEALTHY") {
      return (
        <span className="badge badge-success" style={{ fontSize: "11px", fontWeight: 700 }}>
          <CheckCircle2 size={12} />
          HEALTHY
        </span>
      );
    }
    if (status === "DEGRADED") {
      return (
        <span className="badge badge-warning" style={{ fontSize: "11px", fontWeight: 700 }}>
          <AlertTriangle size={12} />
          DEGRADED
        </span>
      );
    }
    return (
      <span className="badge badge-danger" style={{ fontSize: "11px", fontWeight: 700 }}>
        <XCircle size={12} />
        UNAVAILABLE
      </span>
    );
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--space-3)" }}>
        <div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)", margin: 0 }}>
            Platform Infrastructure & Subsystem Health
          </h1>
          <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: "4px 0 0" }}>
            Live telemetry, database roundtrip ping latencies, worker job queues, and ML inference service availability.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isLoading || isRefetching}
          className="btn btn-secondary"
          style={{ height: "36px", fontSize: "12px" }}
        >
          <RefreshCw
            size={14}
            style={{ animation: isRefetching ? "spin 1s linear infinite" : "none" }}
          />
          Refresh Health Signals
        </button>
      </div>

      {/* Overall Health Status Banner */}
      <div
        className="card"
        style={{
          padding: "var(--space-5)",
          backgroundColor:
            healthData?.overall_status === "HEALTHY"
              ? "#F0FDF4"
              : healthData?.overall_status === "DEGRADED"
              ? "#FFFBEB"
              : "#FEF2F2",
          border:
            healthData?.overall_status === "HEALTHY"
              ? "1px solid rgba(34, 197, 94, 0.3)"
              : healthData?.overall_status === "DEGRADED"
              ? "1px solid rgba(245, 158, 11, 0.3)"
              : "1px solid rgba(239, 68, 68, 0.3)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--space-4)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
            <div
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "12px",
                backgroundColor: "#FFFFFF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color:
                  healthData?.overall_status === "HEALTHY"
                    ? "var(--success)"
                    : healthData?.overall_status === "DEGRADED"
                    ? "var(--warning)"
                    : "var(--error)",
                boxShadow: "0 2px 4px rgba(0,0,0,0.06)",
              }}
            >
              <ShieldCheck size={24} />
            </div>
            <div>
              <div style={{ fontSize: "11px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--gray-text-muted)" }}>
                Platform Operational State
              </div>
              <h2 style={{ fontSize: "20px", fontWeight: 800, margin: 0, color: "var(--gray-text-primary)" }}>
                {healthData?.overall_status === "HEALTHY"
                  ? "All Core Subsystems Operational"
                  : healthData?.overall_status === "DEGRADED"
                  ? "Subsystem Performance Degraded"
                  : "Critical Subsystem Issue Detected"}
              </h2>
            </div>
          </div>

          <div style={{ fontSize: "12px", color: "var(--gray-text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
            <Clock size={14} />
            Last checked: {healthData?.checked_at ? new Date(healthData.checked_at).toLocaleTimeString() : "Just now"}
          </div>
        </div>
      </div>

      {/* Subsystem Health Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "var(--space-5)" }}>
        {isLoading ? (
          [...Array(4)].map((_, i) => (
            <div key={i} className="skeleton-card" style={{ height: "180px" }} />
          ))
        ) : error || !healthData ? (
          <div className="card" style={{ padding: "var(--space-6)", textAlign: "center", gridColumn: "1 / -1" }}>
            <AlertTriangle size={32} style={{ color: "var(--error)", margin: "0 auto var(--space-2)" }} />
            <div>Failed to execute subsystem health checks.</div>
          </div>
        ) : (
          healthData.services.map((svc) => (
            <div key={svc.service_name} className="card" style={{ padding: "var(--space-5)", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-3)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                    <div
                      style={{
                        width: "38px",
                        height: "38px",
                        borderRadius: "10px",
                        backgroundColor: "var(--gray-surface)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        color: "var(--accent)",
                      }}
                    >
                      {getServiceIcon(svc.service_name)}
                    </div>
                    <div>
                      <h3 style={{ fontSize: "15px", fontWeight: 700, margin: 0, color: "var(--gray-text-primary)" }}>
                        {svc.service_name}
                      </h3>
                      {svc.latency_ms !== null && svc.latency_ms !== undefined && (
                        <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
                          Latency: <strong>{svc.latency_ms}ms</strong>
                        </span>
                      )}
                    </div>
                  </div>
                  {renderStatusBadge(svc.status)}
                </div>

                <p style={{ fontSize: "13px", color: "var(--gray-text-primary)", lineHeight: "1.5", margin: 0 }}>
                  {svc.details}
                </p>
              </div>

              <div
                style={{
                  marginTop: "var(--space-4)",
                  paddingTop: "var(--space-3)",
                  borderTop: "1px solid var(--gray-border)",
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "11px",
                  color: "var(--gray-text-muted)",
                }}
              >
                <span>Automated Heartbeat Check</span>
                <span>Active</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
