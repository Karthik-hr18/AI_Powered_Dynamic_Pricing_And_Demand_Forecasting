import React, { useState } from "react";
import { FileText, Download, FileSpreadsheet, CheckCircle, X, Sparkles } from "lucide-react";

export const ReportCenterModal = ({ isOpen, onClose }) => {
  const [downloading, setDownloading] = useState(null);
  const [completed, setCompleted] = useState(null);

  if (!isOpen) return null;

  const reports = [
    {
      id: "pdf-executive",
      title: "Executive Business Summary (PDF)",
      description: "Full executive overview with KPIs, AI pricing opportunities, and stock risk heatmaps.",
      format: "PDF Document",
      icon: <FileText size={20} style={{ color: "#EF4444" }} />,
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

  const handleDownload = (id, title) => {
    setDownloading(id);
    setTimeout(() => {
      setDownloading(null);
      setCompleted(id);
      setTimeout(() => setCompleted(null), 3000);
    }, 1200);
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
          maxWidth: "580px",
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
              Generate and download executive reports, forecasts, and AI price optimization data.
            </p>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--gray-text-muted)", cursor: "pointer" }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-3)", maxHeight: "400px", overflowY: "auto" }}>
          {reports.map((item) => (
            <div
              key={item.id}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "var(--space-4)",
                backgroundColor: "rgba(15, 23, 42, 0.5)",
                border: "1px solid var(--gray-border)",
                borderRadius: "var(--radius-default)",
              }}
            >
              <div style={{ display: "flex", gap: "var(--space-3)", alignItems: "flex-start" }}>
                {item.icon}
                <div>
                  <h4 style={{ fontSize: "14px", fontWeight: 600, color: "#FFFFFF", marginBottom: "2px" }}>{item.title}</h4>
                  <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", marginBottom: "4px" }}>{item.description}</p>
                  <span className="badge badge-secondary" style={{ fontSize: "10px" }}>{item.format}</span>
                </div>
              </div>

              <button
                onClick={() => handleDownload(item.id, item.title)}
                disabled={downloading === item.id}
                className="btn btn-secondary btn-pill"
                style={{ height: "32px", fontSize: "12px", padding: "0 12px", minWidth: "90px", justifyContent: "center" }}
              >
                {downloading === item.id ? (
                  "Exporting..."
                ) : completed === item.id ? (
                  <>
                    <CheckCircle size={14} style={{ color: "#22C55E" }} />
                    Ready
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
