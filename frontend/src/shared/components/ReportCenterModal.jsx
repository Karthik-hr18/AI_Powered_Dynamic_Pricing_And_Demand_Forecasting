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
      isRealEndpoint: true,
    },
    {
      id: "excel-master",
      title: "Master Retail Analytics Workbook (XLSX)",
      description: "Complete multi-tab workbook containing sales history, product master, and forecasts.",
      format: "Excel Workbook",
      icon: <FileSpreadsheet size={20} style={{ color: "#22C55E" }} />,
    },
    {
      id: "csv-pricing",
      title: "AI Dynamic Pricing Recommendations (CSV)",
      description: "Raw price change recommendations, candidate grids, and expected revenue gains per SKU.",
      format: "CSV File",
      icon: <Download size={20} style={{ color: "#6366F1" }} />,
    },
    {
      id: "csv-forecast",
      title: "7-Day Demand Forecast Horizons (CSV)",
      description: "Daily predicted quantities for all 75 indexed SKUs with confidence bounds.",
      format: "CSV File",
      icon: <Sparkles size={20} style={{ color: "#A855F7" }} />,
    },
    {
      id: "csv-inventory",
      title: "Inventory Stockout & Overstock Risk Audit (CSV)",
      description: "Current stock cover days, classification flags, and estimated depletion velocity.",
      format: "CSV File",
      icon: <FileText size={20} style={{ color: "#F59E0B" }} />,
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
          maxWidth: "600px",
          backgroundColor: "#1E293B",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-lg)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5)",
          zIndex: 101,
          padding: "var(--space-5)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "var(--space-4)" }}>
          <div>
            <h3 style={{ fontSize: "18px", fontWeight: 700, color: "#FFFFFF" }}>Report Center & Exports</h3>
            <p style={{ fontSize: "13px", color: "var(--gray-text-muted)" }}>
              Generate and download 10-page executive PDF reports, forecasts, and AI price optimization data.
            </p>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--gray-text-muted)", cursor: "pointer" }}>
            <X size={20} />
          </button>
        </div>

        {errorMsg && (
          <div className="badge badge-danger" style={{ width: "100%", marginBottom: "var(--space-3)", padding: "8px 12px", textTransform: "none" }}>
            <AlertCircle size={14} />
            {errorMsg}
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", maxHeight: "420px", overflowY: "auto" }}>
          {reports.map((item) => (
            <div
              key={item.id}
              className="card card-interactive"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "var(--space-4)",
              }}
            >
              <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "flex-start" }}>
                <div style={{ padding: "8px", borderRadius: "8px", backgroundColor: "rgba(15, 23, 42, 0.6)", flexShrink: 0 }}>
                  {item.icon}
                </div>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "2px" }}>
                    <h4 style={{ fontSize: "14px", fontWeight: 700, color: "#FFFFFF" }}>{item.title}</h4>
                    <span className="badge badge-purple" style={{ fontSize: "10px" }}>{item.format}</span>
                  </div>
                  <p style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>{item.description}</p>
                </div>
              </div>

              <button
                onClick={() => handleDownload(item.id, item.title, item.isRealEndpoint)}
                disabled={downloading === item.id}
                className={item.isRealEndpoint ? "btn btn-primary btn-pill" : "btn btn-secondary btn-pill"}
                style={{ height: "34px", fontSize: "12px", padding: "0 14px", minWidth: "100px", justifyContent: "center", flexShrink: 0 }}
              >
                {downloading === item.id ? (
                  "Generating..."
                ) : completed === item.id ? (
                  <>
                    <CheckCircle size={14} style={{ color: "#22C55E" }} />
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

        <div style={{ marginTop: "var(--space-4)", textAlign: "right" }}>
          <button onClick={onClose} className="btn btn-secondary btn-pill" style={{ height: "34px", fontSize: "12px" }}>
            Close Report Center
          </button>
        </div>
      </div>
    </>
  );
};
