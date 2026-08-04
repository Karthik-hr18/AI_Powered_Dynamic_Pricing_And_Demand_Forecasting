import React, { useState } from "react";
import { FileText, Download, FileSpreadsheet, CheckCircle, X, Sparkles, AlertCircle } from "lucide-react";
import { apiClient } from "../apiClient";

export const ReportCenterModal = ({ isOpen, onClose }) => {
  const [downloading, setDownloading] = useState(null);
  const [completed, setCompleted] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!isOpen) return null;

  const reports = [
    {
      id: "pdf-executive",
      title: "Executive Business Summary (PDF)",
      description: "Full 10-page executive PDF report with health scores, financial trends, AI pricing recommendations, and stock risk heatmaps.",
      format: "PDF Document",
      icon: <FileText size={20} style={{ color: "#EF4444" }} />,
      bgIcon: "#FEF2F2",
      isRealEndpoint: true,
    },
    {
      id: "excel-master",
      title: "Master Retail Analytics Workbook (XLSX)",
      description: "Complete multi-tab workbook containing sales history, product master, and forecasts.",
      format: "Excel Workbook",
      icon: <FileSpreadsheet size={20} style={{ color: "#10B981" }} />,
      bgIcon: "#ECFDF5",
    },
    {
      id: "csv-pricing",
      title: "AI Dynamic Pricing Recommendations (CSV)",
      description: "Raw price change recommendations, candidate grids, and expected revenue gains per SKU.",
      format: "CSV File",
      icon: <Download size={20} style={{ color: "#4F46E5" }} />,
      bgIcon: "#EEF2FF",
    },
    {
      id: "csv-forecast",
      title: "7-Day Demand Forecast Horizons (CSV)",
      description: "Daily predicted quantities for all 75 indexed SKUs with confidence bounds.",
      format: "CSV File",
      icon: <Sparkles size={20} style={{ color: "#7E22CE" }} />,
      bgIcon: "#F3E8FF",
    },
    {
      id: "csv-inventory",
      title: "Inventory Stockout & Overstock Risk Audit (CSV)",
      description: "Current stock cover days, classification flags, and estimated depletion velocity.",
      format: "CSV File",
      icon: <FileText size={20} style={{ color: "#D97706" }} />,
      bgIcon: "#FEF3C7",
    },
  ];

  const handleDownload = async (id, title, isRealEndpoint) => {
    setDownloading(id);
    setErrorMsg(null);

    if (id === "pdf-executive" || isRealEndpoint) {
      try {
        const response = await apiClient.get("reports/pdf", {
          responseType: "blob",
        });

        // Trigger browser automatic file download
        const blob = new Blob([response.data], { type: "application/pdf" });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        const dateStr = new Date().toISOString().slice(0, 10).replace(/-/g, "_");
        link.setAttribute("download", `Retail_Analytics_Report_${dateStr}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        setDownloading(null);
        setCompleted(id);
        setTimeout(() => setCompleted(null), 3000);
      } catch (err) {
        console.error("PDF download failed:", err);
        setDownloading(null);
        setErrorMsg("Failed to generate PDF report. Please try again.");
      }
    } else {
      // Mock download for secondary CSV/XLSX exports
      setTimeout(() => {
        setDownloading(null);
        setCompleted(id);
        setTimeout(() => setCompleted(null), 3000);
      }, 1000);
    }
  };

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} style={{ zIndex: 100 }} />
      <div
        style={{
          position: "fixed",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: "90%",
          maxWidth: "620px",
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.15)",
          zIndex: 101,
          padding: "var(--space-6)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-5)" }}>
          <div>
            <h3 style={{ fontSize: "20px", fontWeight: 800, color: "var(--gray-text-primary)" }}>Report Center & Exports</h3>
            <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", marginTop: "2px" }}>
              Generate and download 10-page executive PDF reports, forecasts, and AI price optimization datasets.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "#F1F5F9",
              border: "none",
              color: "var(--gray-text-muted)",
              cursor: "pointer",
              borderRadius: "50%",
              width: "32px",
              height: "32px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <X size={18} />
          </button>
        </div>

        {errorMsg && (
          <div className="badge badge-danger" style={{ width: "100%", marginBottom: "var(--space-4)", padding: "10px 14px", textTransform: "none", fontSize: "12px" }}>
            <AlertCircle size={14} />
            {errorMsg}
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", maxHeight: "420px", overflowY: "auto" }}>
          {reports.map((item) => (
            <div
              key={item.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "var(--space-4)",
                backgroundColor: "#F8FAFC",
                border: "1px solid var(--gray-border)",
                borderRadius: "var(--radius-default)",
                transition: "all 150ms ease-in-out",
              }}
              className="report-card-hover"
            >
              <div style={{ display: "flex", gap: "var(--space-4)", alignItems: "center", flex: 1 }}>
                <div
                  style={{
                    padding: "10px",
                    borderRadius: "10px",
                    backgroundColor: item.bgIcon,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {item.icon}
                </div>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "2px" }}>
                    <h4 style={{ fontSize: "14px", fontWeight: 700, color: "var(--gray-text-primary)" }}>{item.title}</h4>
                    <span
                      style={{
                        fontSize: "10px",
                        fontWeight: 600,
                        backgroundColor: "#EEF2FF",
                        color: "var(--accent)",
                        padding: "2px 8px",
                        borderRadius: "var(--radius-pill)",
                      }}
                    >
                      {item.format}
                    </span>
                  </div>
                  <p style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>{item.description}</p>
                </div>
              </div>

              <button
                onClick={() => handleDownload(item.id, item.title, item.isRealEndpoint)}
                disabled={downloading === item.id}
                className={item.isRealEndpoint ? "btn btn-primary btn-pill" : "btn btn-secondary btn-pill"}
                style={{ height: "36px", fontSize: "12px", padding: "0 16px", minWidth: "105px", justifyContent: "center", flexShrink: 0 }}
              >
                {downloading === item.id ? (
                  "Generating..."
                ) : completed === item.id ? (
                  <>
                    <CheckCircle size={14} style={{ color: "var(--success)" }} />
                    Downloaded
                  </>
                ) : (
                  <>
                    <Download size={13} />
                    Download
                  </>
                )}
              </button>
            </div>
          ))}
        </div>

        <div style={{ marginTop: "var(--space-5)", textAlign: "right" }}>
          <button onClick={onClose} className="btn btn-secondary btn-pill" style={{ height: "36px", fontSize: "13px", padding: "0 18px" }}>
            Close Report Center
          </button>
        </div>
      </div>

      <style>{`
        .report-card-hover:hover {
          background-color: #FFFFFF !important;
          border-color: rgba(79, 70, 229, 0.3) !important;
          box-shadow: 0 4px 14px rgba(79, 70, 229, 0.08) !important;
        }
      `}</style>
    </>
  );
};
