import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Database,
  Search,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ChevronLeft,
  ChevronRight,
  Eye,
  FileSpreadsheet,
  Layers,
  Filter,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";
import { formatInteger } from "../../../shared/utils/formatters";
import { UploadDetailDrawer } from "../components/UploadDetailDrawer";

export const AdminDataOperationsPage = () => {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedUpload, setSelectedUpload] = useState(null);

  const { data: operationsData, isLoading, error } = useQuery({
    queryKey: ["adminDataOperations", page, statusFilter, searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(page),
        limit: "15",
      });
      if (statusFilter !== "ALL") params.append("status", statusFilter);
      if (searchTerm.trim()) params.append("search", searchTerm.trim());

      const res = await apiClient.get(`admin/data-operations?${params.toString()}`);
      return res.data;
    },
    refetchInterval: 15000,
  });

  const uploads = operationsData?.uploads || [];
  const stats = operationsData?.stats || {};
  const totalPages = operationsData?.total_pages || 1;
  const totalCount = operationsData?.total_count || 0;

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const renderStatusBadge = (status) => {
    if (status.includes("COMPLETED")) {
      return (
        <span className="badge badge-success" style={{ fontSize: "11px", fontWeight: 700 }}>
          {status}
        </span>
      );
    }
    if (status.includes("FAILED") || status.includes("REJECTED")) {
      return (
        <span className="badge badge-danger" style={{ fontSize: "11px", fontWeight: 700 }}>
          {status}
        </span>
      );
    }
    return (
      <span className="badge badge-warning" style={{ fontSize: "11px", fontWeight: 700 }}>
        {status}
      </span>
    );
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)", margin: 0 }}>
          Data Operations & Ingestion Monitoring
        </h1>
        <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: "4px 0 0" }}>
          Track real-time CSV pipeline execution, row yields, ML processing stages, and failure diagnostics.
        </p>
      </div>

      {/* KPI Stats Top Bar */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "var(--space-4)" }}>
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ fontSize: "12px", color: "var(--gray-text-muted)", fontWeight: 600, marginBottom: "4px" }}>
            Total Upload Jobs
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {formatInteger(stats.total || 0)}
          </div>
        </div>
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ fontSize: "12px", color: "var(--gray-text-muted)", fontWeight: 600, marginBottom: "4px" }}>
            Successfully Completed
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--success)" }}>
            {formatInteger(stats.completed || 0)}
          </div>
        </div>
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ fontSize: "12px", color: "var(--gray-text-muted)", fontWeight: 600, marginBottom: "4px" }}>
            Active Processing
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--warning)" }}>
            {formatInteger(stats.processing || 0)}
          </div>
        </div>
        <div className="card" style={{ padding: "var(--space-4)" }}>
          <div style={{ fontSize: "12px", color: "var(--gray-text-muted)", fontWeight: 600, marginBottom: "4px" }}>
            Failed Ingestions
          </div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: (stats.failed || 0) > 0 ? "var(--error)" : "var(--gray-text-primary)" }}>
            {formatInteger(stats.failed || 0)}
          </div>
        </div>
      </div>

      {/* Search & Status Filter */}
      <div className="card" style={{ padding: "var(--space-4)" }}>
        <div style={{ display: "flex", gap: "var(--space-4)", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between" }}>
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
              placeholder="Search by upload ID or filename..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setPage(1);
              }}
              className="input"
              style={{ paddingLeft: "36px", height: "38px" }}
            />
          </div>

          <div style={{ display: "flex", gap: "var(--space-1)", backgroundColor: "var(--gray-surface)", padding: "3px", borderRadius: "var(--radius-default)", border: "1px solid var(--gray-border)" }}>
            {["ALL", "COMPLETED", "PROCESSING", "FAILED"].map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setStatusFilter(tab);
                  setPage(1);
                }}
                style={{
                  padding: "6px 12px",
                  border: "none",
                  borderRadius: "4px",
                  fontSize: "12px",
                  fontWeight: 600,
                  cursor: "pointer",
                  backgroundColor: statusFilter === tab ? "#FFFFFF" : "transparent",
                  color: statusFilter === tab ? "var(--accent)" : "var(--gray-text-muted)",
                  boxShadow: statusFilter === tab ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
                }}
              >
                {tab.charAt(0) + tab.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table Card */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {isLoading ? (
          <div style={{ padding: "var(--space-6)", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            <div className="skeleton-card" style={{ height: "40px" }} />
            <div className="skeleton-card" style={{ height: "40px" }} />
            <div className="skeleton-card" style={{ height: "40px" }} />
          </div>
        ) : error ? (
          <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--error)" }}>
            Failed to load data operations.
          </div>
        ) : uploads.length === 0 ? (
          <div style={{ padding: "var(--space-8)", textAlign: "center", color: "var(--gray-text-muted)" }}>
            <FileSpreadsheet size={36} style={{ margin: "0 auto var(--space-3)", opacity: 0.5 }} />
            <div style={{ fontSize: "15px", fontWeight: 700, color: "var(--gray-text-primary)", marginBottom: "4px" }}>
              No dataset operations found
            </div>
            <div style={{ fontSize: "13px" }}>
              {searchTerm ? "No results matching your search." : "No uploads recorded for this status."}
            </div>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table" style={{ margin: 0 }}>
              <thead>
                <tr>
                  <th>Job ID</th>
                  <th>Retailer Business</th>
                  <th>Filename</th>
                  <th style={{ textAlign: "center" }}>Ingested</th>
                  <th>Status</th>
                  <th>Current Stage</th>
                  <th>Duration</th>
                  <th>Received</th>
                  <th style={{ textAlign: "right" }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {uploads.map((u) => (
                  <tr
                    key={u.id}
                    style={{ cursor: "pointer" }}
                    onClick={() => setSelectedUpload(u)}
                  >
                    <td>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: "12px", color: "var(--accent)" }}>
                        {u.upload_id}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: "var(--gray-text-primary)" }}>
                        {u.retailer_business_name}
                      </div>
                      <div style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
                        {u.retailer_email}
                      </div>
                    </td>
                    <td style={{ fontWeight: 600 }}>{u.original_filename}</td>
                    <td style={{ textAlign: "center", fontWeight: 700, color: "var(--success)" }}>
                      {formatInteger(u.rows_ingested || u.row_count || 0)}
                    </td>
                    <td>{renderStatusBadge(u.status)}</td>
                    <td style={{ fontSize: "12px", color: "var(--gray-text-primary)" }}>
                      {u.current_stage || "COMPLETED"}
                    </td>
                    <td style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                      {u.duration_seconds !== null ? `${u.duration_seconds}s` : "—"}
                    </td>
                    <td style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                      {formatDate(u.created_at)}
                    </td>
                    <td style={{ textAlign: "right" }} onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => setSelectedUpload(u)}
                        className="btn btn-secondary"
                        style={{ height: "30px", fontSize: "11px", padding: "0 8px" }}
                      >
                        <Eye size={12} />
                        Forensics
                      </button>
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
              Showing Page {page} of {totalPages} ({totalCount} total jobs)
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

      {/* Forensic Detail Drawer */}
      <UploadDetailDrawer
        isOpen={!!selectedUpload}
        onClose={() => setSelectedUpload(null)}
        upload={selectedUpload}
      />
    </div>
  );
};
