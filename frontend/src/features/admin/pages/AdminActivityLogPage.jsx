import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  History,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ChevronLeft,
  ChevronRight,
  Shield,
  User,
  FileSpreadsheet,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";

export const AdminActivityLogPage = () => {
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  const { data: activityData, isLoading, error } = useQuery({
    queryKey: ["adminActivityLog", page, actionFilter, statusFilter, searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(page),
        limit: "20",
      });
      if (actionFilter !== "ALL") params.append("action", actionFilter);
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      if (searchTerm.trim()) params.append("search", searchTerm.trim());

      const res = await apiClient.get(`admin/activity-log?${params.toString()}`);
      return res.data;
    },
    refetchInterval: 20000,
  });

  const events = activityData?.events || [];
  const totalPages = activityData?.total_pages || 1;
  const totalCount = activityData?.total_count || 0;

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const renderActionBadge = (action) => {
    let colorClass = "badge-info";
    if (action.includes("RETAILER_DISABLED") || action.includes("FAILED")) {
      colorClass = "badge-danger";
    } else if (action.includes("RETAILER_ACTIVATED") || action.includes("SUCCESS")) {
      colorClass = "badge-success";
    } else if (action.includes("CSV_UPLOAD")) {
      colorClass = "badge-primary";
    }

    return (
      <span className={`badge ${colorClass}`} style={{ fontSize: "11px", fontWeight: 700 }}>
        {action}
      </span>
    );
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)", margin: 0 }}>
          Platform Activity Log & Audit Trail
        </h1>
        <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: "4px 0 0" }}>
          Immutable record of security events, administrative account toggles, dataset ingestions, and system operations.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: "var(--space-4)" }}>
        <div style={{ display: "flex", gap: "var(--space-4)", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between" }}>
          {/* Search */}
          <div style={{ position: "relative", minWidth: "260px", flex: 1 }}>
            <Search
              size={16}
              style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--gray-text-muted)",
              }}
            />
            <input
              type="text"
              placeholder="Search by actor, target, or description..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1);
              }}
              className="input"
              style={{ paddingLeft: "36px", height: "38px" }}
            />
          </div>

          {/* Action Category Filter */}
          <div style={{ display: "flex", gap: "var(--space-2)", alignItems: "center" }}>
            <select
              value={actionFilter}
              onChange={(e) => {
                setActionFilter(e.target.value);
                setPage(1);
              }}
              className="input"
              style={{ height: "38px", fontSize: "12px", minWidth: "150px" }}
            >
              <option value="ALL">All Actions</option>
              <option value="CSV_UPLOAD">CSV Ingestions</option>
              <option value="RETAILER_DISABLED">Account Disabled</option>
              <option value="RETAILER_ACTIVATED">Account Reactivated</option>
              <option value="USER_REGISTER">User Registrations</option>
              <option value="USER_LOGIN">User Logins</option>
              <option value="REPORT_EXPORT">Report Exports</option>
            </select>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
              className="input"
              style={{ height: "38px", fontSize: "12px", minWidth: "120px" }}
            >
              <option value="ALL">All Statuses</option>
              <option value="SUCCESS">Success</option>
              <option value="FAILED">Failed</option>
              <option value="WARNING">Warning</option>
            </select>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {isLoading ? (
          <div style={{ padding: "var(--space-6)", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            <div className="skeleton-card" style={{ height: "40px" }} />
            <div className="skeleton-card" style={{ height: "40px" }} />
            <div className="skeleton-card" style={{ height: "40px" }} />
          </div>
        ) : error ? (
          <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--error)" }}>
            Failed to load platform activity logs.
          </div>
        ) : events.length === 0 ? (
          <div style={{ padding: "var(--space-8)", textAlign: "center", color: "var(--gray-text-muted)" }}>
            <History size={36} style={{ margin: "0 auto var(--space-3)", opacity: 0.5 }} />
            <div style={{ fontSize: "15px", fontWeight: 700, color: "var(--gray-text-primary)", marginBottom: "4px" }}>
              No activity records found
            </div>
            <div style={{ fontSize: "13px" }}>
              {searchTerm ? "No events match your search term." : "No audit trail events recorded for this selection."}
            </div>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table" style={{ margin: 0, fontSize: "13px" }}>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Action</th>
                  <th>Actor</th>
                  <th>Target</th>
                  <th>Status</th>
                  <th>Operational Description</th>
                </tr>
              </thead>
              <tbody>
                {events.map((ev) => (
                  <tr key={ev.id}>
                    <td style={{ color: "var(--gray-text-muted)", whiteSpace: "nowrap", fontSize: "12px" }}>
                      {formatDate(ev.timestamp)}
                    </td>
                    <td>{renderActionBadge(ev.action)}</td>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--gray-text-primary)" }}>{ev.actor_email}</div>
                      <span className="badge badge-info" style={{ fontSize: "10px", padding: "1px 6px" }}>
                        {ev.actor_role}
                      </span>
                    </td>
                    <td style={{ color: "var(--gray-text-primary)", fontWeight: 600 }}>
                      {ev.target_name || "—"}
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          ev.status === "SUCCESS"
                            ? "badge-success"
                            : ev.status === "FAILED"
                            ? "badge-danger"
                            : "badge-warning"
                        }`}
                        style={{ fontSize: "10px" }}
                      >
                        {ev.status}
                      </span>
                    </td>
                    <td style={{ color: "var(--gray-text-primary)", maxWidth: "340px" }}>
                      {ev.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div
            style={{
              padding: "var(--space-3) var(--space-5)",
              borderTop: "1px solid var(--gray-border)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              backgroundColor: "var(--gray-surface)",
            }}
          >
            <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
              Page {page} of {totalPages} ({totalCount} total audit records)
            </span>
            <div style={{ display: "flex", gap: "var(--space-2)" }}>
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="btn btn-secondary"
                style={{ height: "30px", padding: "0 8px" }}
              >
                <ChevronLeft size={14} />
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="btn btn-secondary"
                style={{ height: "30px", padding: "0 8px" }}
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
