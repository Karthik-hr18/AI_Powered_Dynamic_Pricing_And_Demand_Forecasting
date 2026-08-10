import React, { useState } from "react";
import {
  FileSpreadsheet,
  Download,
  Users,
  Database,
  History,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  FileText,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";
import { useToast } from "../../../shared/hooks/useToast";

export const AdminReportsPage = () => {
  const toast = useToast();
  const [downloadingType, setDownloadingType] = useState(null);

  const handleExportCSV = async (reportType, title) => {
    try {
      setDownloadingType(reportType);
      const res = await apiClient.get(`admin/reports/export?type=${reportType}`, {
        responseType: "blob",
      });

      // Create download blob link
      const blob = new Blob([res.data], { type: "text/csv;charset=utf-8;" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `profitsync_admin_${reportType}_${new Date().toISOString().slice(0, 10)}.csv`
      );
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success(
        "Export Generated",
        `${title} CSV report has been downloaded successfully.`
      );
    } catch (err) {
      console.error("Report export failed", err);
      toast.error("Export Failed", "Report could not be generated. Please try again.");
    } finally {
      setDownloadingType(null);
    }
  };

  const reportCards = [
    {
      type: "retailers",
      title: "Master Retailer Accounts Directory",
      description:
        "Comprehensive directory of all registered retailers, account activation statuses, email verification, total uploaded datasets, sales records, and catalog footprints.",
      icon: <Users size={24} />,
      format: "CSV (.csv)",
      badge: "Real-time Database",
    },
    {
      type: "uploads",
      title: "Dataset Ingestion & Operations Log",
      description:
        "Complete historical record of all CSV uploads across retailers, including row counts, ingestion stages, processing execution times, and failure forensics.",
      icon: <Database size={24} />,
      format: "CSV (.csv)",
      badge: "Full History",
    },
    {
      type: "activity",
      title: "Platform Activity & Security Audit Trail",
      description:
        "Chronological audit log of all administrative actions, account status modifications, user authentication events, and data processing milestones.",
      icon: <History size={24} />,
      format: "CSV (.csv)",
      badge: "Security Audit",
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)", margin: 0 }}>
          Administrative Data Reports & Exports
        </h1>
        <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: "4px 0 0" }}>
          Export platform-level operational telemetry, retailer directories, and security audit trails.
        </p>
      </div>

      {/* Reports Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "var(--space-5)" }}>
        {reportCards.map((r) => {
          const isDownloading = downloadingType === r.type;

          return (
            <div
              key={r.type}
              className="card"
              style={{
                padding: "var(--space-5)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
              }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-4)" }}>
                  <div
                    style={{
                      width: "44px",
                      height: "44px",
                      borderRadius: "10px",
                      backgroundColor: "rgba(79, 70, 229, 0.08)",
                      color: "var(--accent)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {r.icon}
                  </div>
                  <span className="badge badge-info" style={{ fontSize: "11px" }}>
                    {r.badge}
                  </span>
                </div>

                <h3 style={{ fontSize: "16px", fontWeight: 700, margin: "0 0 var(--space-2)", color: "var(--gray-text-primary)" }}>
                  {r.title}
                </h3>
                <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", lineHeight: "1.5", margin: 0 }}>
                  {r.description}
                </p>
              </div>

              <div
                style={{
                  marginTop: "var(--space-5)",
                  paddingTop: "var(--space-4)",
                  borderTop: "1px solid var(--gray-border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <span style={{ fontSize: "12px", color: "var(--gray-text-muted)", fontWeight: 600 }}>
                  Format: {r.format}
                </span>

                <button
                  onClick={() => handleExportCSV(r.type, r.title)}
                  disabled={isDownloading}
                  className="btn btn-primary"
                  style={{ height: "36px", fontSize: "12px" }}
                >
                  {isDownloading ? (
                    <>
                      <Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download size={14} />
                      Export CSV
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
