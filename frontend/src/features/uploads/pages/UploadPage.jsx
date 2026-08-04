import React, { useState, useEffect, useRef } from "react";
import {
  UploadCloud,
  FileSpreadsheet,
  Trash2,
  Play,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Loader2,
  History,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";
import { useUploadPolling } from "../hooks/useUploadPolling";
import { useAuth } from "../../../shared/hooks/useAuth";
import { ShieldAlert, MailCheck } from "lucide-react";

export const UploadPage = () => {
  const { user, isEmailVerified } = useAuth();
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [schemaMapping, setSchemaMapping] = useState("standard");
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const fileInputRef = useRef(null);

  // Block unverified retailers from uploading
  const isBlocked = user?.role === "RETAILER" && !isEmailVerified;

  // Load uploads history from database
  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const res = await apiClient.get("uploads/");
      // Sort history by created_at descending
      const sorted = res.data.sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      );
      setHistory(sorted);
    } catch (e) {
      console.error("Failed to load uploads history:", e);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  // Set up polling hook. Automatically refreshes history list on completion
  const { activeUpload, setActiveUpload, isPolling, startPolling } =
    useUploadPolling(() => {
      loadHistory();
    });

  // Client-side file selection handlers
  const handleFileChange = (selectedFile) => {
    if (!selectedFile) return;

    // Verify CSV extension
    const isCsv =
      selectedFile.name.endsWith(".csv") || selectedFile.type === "text/csv";
    if (!isCsv) {
      alert("Invalid format: Only CSV spreadsheets are accepted.");
      return;
    }

    setFile(selectedFile);
    // Reset active view when selecting a new file to upload
    setActiveUpload(null);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const onDragLeave = () => {
    setDragOver(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Upload request submission
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("schema_mapping_used", schemaMapping);

    try {
      const res = await apiClient.post("uploads/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const upload = res.data;
      // Start checking status in real time
      startPolling(upload.id);
      removeFile();
    } catch (err) {
      console.error("Upload failed", err);
      alert(err.response?.data?.detail || "Failed to upload file.");
    }
  };

  // Format file size utility
  const formatBytes = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  // Format date utility
  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleString();
  };

  // Render status badge mapping HSL colors with semantic icons
  const renderStatusBadge = (status) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="badge badge-success">
            <CheckCircle size={12} />
            Completed
          </span>
        );
      case "COMPLETED_WITH_WARNINGS":
        return (
          <span className="badge badge-warning">
            <AlertTriangle size={12} />
            Warnings
          </span>
        );
      case "REJECTED":
        return (
          <span className="badge badge-danger">
            <XCircle size={12} />
            Rejected
          </span>
        );
      case "FAILED":
        return (
          <span className="badge badge-danger">
            <XCircle size={12} />
            Failed
          </span>
        );
      case "PROCESSING":
      case "VALIDATING":
      case "UPLOADED":
      default:
        return (
          <span className="badge badge-info">
            <Loader2 size={12} className="pulse-dot" style={{ animation: "spin 2s linear infinite" }} />
            {status}
          </span>
        );
    }
  };

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: "var(--space-5)" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
          Uploads
        </h2>
      </div>

      {/* Email verification gate */}
      {isBlocked && (
        <div
          style={{
            background: "linear-gradient(135deg, rgba(217,119,6,0.08) 0%, rgba(251,191,36,0.05) 100%)",
            border: "1px solid rgba(217,119,6,0.4)",
            borderRadius: "var(--radius-card)",
            padding: "var(--space-6)",
            display: "flex",
            gap: "var(--space-4)",
            alignItems: "flex-start",
            marginBottom: "var(--space-6)",
          }}
        >
          <div
            style={{
              width: "44px", height: "44px", borderRadius: "50%",
              background: "rgba(217,119,6,0.15)",
              display: "flex", alignItems: "center", justifyContent: "center",
              flexShrink: 0,
            }}
          >
            <MailCheck size={22} style={{ color: "#FBBF24" }} />
          </div>
          <div>
            <p style={{ fontWeight: 700, color: "#FDE68A", fontSize: "15px", marginBottom: "6px" }}>
              Email Verification Required
            </p>
            <p style={{ color: "#FCD34D", fontSize: "13px", lineHeight: 1.65 }}>
              You must verify your email address before uploading data. Please check your inbox
              for the verification link we sent when you registered. Once verified, refresh the
              page and you can start uploading.
            </p>
          </div>
        </div>
      )}

      <div
        style={{
          display: "flex",
          gap: "var(--space-6)",
          flexWrap: "wrap",
        }}
      >
        {/* Left Column: Upload drag-drop area + Active upload details */}
        <div style={{ flex: "1.2", minWidth: "320px", display: "flex", flexDirection: "column", gap: "var(--space-5)" }}>
          
          {/* File Dropzone Card */}
          <div className="card" style={{ padding: "var(--space-5)" }}>
            <h4 style={{ marginBottom: "var(--space-3)", fontWeight: 700 }}>Upload Sales Sheet</h4>
            
            <div
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={isBlocked ? undefined : onDrop}
              onClick={isBlocked ? undefined : () => fileInputRef.current?.click()}
              style={{
                border: dragOver ? "2px solid var(--accent)" : "2px dashed var(--gray-border)",
                backgroundColor: isBlocked
                  ? "rgba(15,23,42,0.3)"
                  : dragOver ? "rgba(79, 70, 229, 0.04)" : "var(--gray-bg)",
                borderRadius: "var(--radius-card)",
                padding: "var(--space-6) var(--space-4)",
                textAlign: "center",
                cursor: isBlocked ? "not-allowed" : "pointer",
                transition: "all var(--transition-speed-fast) var(--transition-timing)",
                transform: dragOver ? "scale(1.01)" : "none",
                opacity: isBlocked ? 0.45 : 1,
                pointerEvents: isBlocked ? "none" : "auto",
              }}
              className="dropzone-area"
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => handleFileChange(e.target.files[0])}
                style={{ display: "none" }}
                accept=".csv"
              />
              <UploadCloud
                size={40}
                style={{
                  color: dragOver ? "var(--accent)" : "var(--gray-text-muted)",
                  marginBottom: "var(--space-3)",
                }}
              />
              <p style={{ fontSize: "15px", fontWeight: 600, color: "var(--gray-text-primary)" }}>
                Drag and drop your sales file here
              </p>
              <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", marginTop: "var(--space-1)" }}>
                Supports standard comma-separated text sheets (.csv) up to 25MB
              </p>
            </div>

            {/* Selected File Stats Panel */}
            {file && (
              <div
                style={{
                  marginTop: "var(--space-4)",
                  padding: "var(--space-4)",
                  backgroundColor: "var(--gray-bg)",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid var(--gray-border)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)", marginBottom: "var(--space-3)" }}>
                  <FileSpreadsheet size={24} style={{ color: "var(--accent)", flexShrink: 0 }} />
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <p
                      style={{
                        fontSize: "14px",
                        fontWeight: 600,
                        textOverflow: "ellipsis",
                        overflow: "hidden",
                        whiteSpace: "nowrap",
                        color: "var(--gray-text-primary)",
                      }}
                    >
                      {file.name}
                    </p>
                    <p style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>{formatBytes(file.size)}</p>
                  </div>
                </div>

                {/* Schema Selection */}
                <div className="form-group" style={{ marginBottom: "var(--space-4)" }}>
                  <label className="form-label">CSV Mapping Template</label>
                  <select
                    className="form-input"
                    value={schemaMapping}
                    onChange={(e) => setSchemaMapping(e.target.value)}
                    style={{ backgroundColor: "var(--gray-surface)" }}
                  >
                    <option value="standard">Standard Template (date, sku, quantity_sold, selling_price)</option>
                  </select>
                </div>

                {/* Action CTA Buttons */}
                <div style={{ display: "flex", gap: "var(--space-2)" }}>
                  <button
                    onClick={handleUploadSubmit}
                    className="btn btn-primary"
                    style={{ flex: 1, opacity: isBlocked ? 0.4 : 1 }}
                    disabled={isBlocked}
                  >
                    <Play size={16} />
                    Ingest Sales File
                  </button>
                  <button
                    onClick={removeFile}
                    className="btn btn-secondary"
                    style={{ color: "var(--error)", borderColor: "rgba(239, 68, 68, 0.3)" }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Active Job Status Card */}
          {activeUpload && (
            <div className="card" style={{ padding: "var(--space-5)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "var(--space-4)" }}>
                <div>
                  <h4 style={{ fontWeight: 700 }}>Upload Details</h4>
                  <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>ID: {activeUpload.upload_id}</span>
                </div>
                {renderStatusBadge(activeUpload.status)}
              </div>

              {/* Ingestion stats & current stage details */}
              <div
                style={{
                  padding: "var(--space-4)",
                  backgroundColor: "var(--gray-bg)",
                  borderRadius: "var(--radius-default)",
                  border: "1px solid var(--gray-border)",
                  display: "flex",
                  flexDirection: "column",
                  gap: "var(--space-3)",
                  marginBottom: "var(--space-4)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Filename:</span>
                  <span style={{ fontWeight: 600 }}>{activeUpload.original_filename}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>File size:</span>
                  <span style={{ fontWeight: 600 }}>{formatBytes(activeUpload.file_size_bytes)}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Inference pipeline state:</span>
                  <span style={{ fontWeight: 600, color: "var(--accent)" }}>
                    {activeUpload.current_stage || (isPolling ? "pending queue" : "completed")}
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Uploaded:</span>
                  <span>{formatDate(activeUpload.created_at)}</span>
                </div>
                <div style={{ height: "1px", backgroundColor: "var(--gray-border)", margin: "var(--space-1) 0" }} />
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Rows Ingested:</span>
                  <span style={{ fontWeight: 700, color: "var(--success)" }}>{activeUpload.rows_ingested ?? 0}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
                  <span style={{ color: "var(--gray-text-muted)" }}>Rows Rejected:</span>
                  <span style={{ fontWeight: 700, color: activeUpload.rows_rejected > 0 ? "var(--error)" : "var(--gray-text-muted)" }}>
                    {activeUpload.rows_rejected}
                  </span>
                </div>
              </div>

              {/* Real-time Loader Animation */}
              {isPolling && (
                <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--accent)", fontSize: "13px", fontWeight: 600, justifyContent: "center" }}>
                  <Loader2 size={16} style={{ animation: "spin 2s linear infinite" }} />
                  Processing rolling ML aggregates...
                </div>
              )}

              {/* Error Log Box */}
              {(activeUpload.status === "REJECTED" || activeUpload.status === "FAILED") && (
                <div
                  className="badge badge-danger"
                  style={{
                    width: "100%",
                    padding: "var(--space-3)",
                    borderRadius: "var(--radius-default)",
                    textTransform: "none",
                    letterSpacing: "normal",
                    fontSize: "13px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    gap: "var(--space-2)",
                    fontWeight: 500,
                  }}
                >
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <XCircle size={16} />
                    <strong>Failed: {activeUpload.error_reason || "Ingestion Error"}</strong>
                  </div>
                  {activeUpload.validation_errors && activeUpload.validation_errors.length > 0 && (
                    <ul style={{ paddingLeft: "24px", textAlign: "left", listStyleType: "disc" }}>
                      {activeUpload.validation_errors.map((err, i) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              {/* Completed with Warnings Log Box */}
              {activeUpload.status === "COMPLETED_WITH_WARNINGS" && activeUpload.row_warnings && activeUpload.row_warnings.length > 0 && (
                <div
                  className="badge badge-warning"
                  style={{
                    width: "100%",
                    padding: "var(--space-3)",
                    borderRadius: "var(--radius-default)",
                    textTransform: "none",
                    letterSpacing: "normal",
                    fontSize: "13px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    gap: "var(--space-2)",
                    color: "#7A4300",
                    fontWeight: 500,
                  }}
                >
                  <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                    <AlertTriangle size={16} />
                    <strong>Row-Level Warnings Detected</strong>
                  </div>
                  <div style={{ maxHeight: "150px", overflowY: "auto", width: "100%", paddingLeft: "10px", textAlign: "left" }}>
                    {activeUpload.row_warnings.map((warn, i) => (
                      <p key={i} style={{ fontSize: "12px", margin: "2px 0" }}>
                        • <strong>Row {warn.row}:</strong> {warn.reason}
                      </p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Upload history table */}
        <div style={{ flex: "1", minWidth: "320px" }} className="table-container">
          <div
            style={{
              padding: "var(--space-4) var(--space-5)",
              borderBottom: "1px solid var(--gray-border)",
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <History size={18} style={{ color: "var(--gray-text-muted)" }} />
            <h4 style={{ fontWeight: 700 }}>Ingestion History</h4>
          </div>

          <div className="table-responsive">
            {loadingHistory ? (
              // Pulsing skeletons during load state
              <div style={{ padding: "var(--space-5)", display: "flex", flexDirection: "column", gap: "10px" }}>
                <div className="skeleton-line" style={{ width: "90%" }} />
                <div className="skeleton-line" style={{ width: "85%" }} />
                <div className="skeleton-line" style={{ width: "95%" }} />
              </div>
            ) : history.length === 0 ? (
              // Empty State Container
              <div style={{ padding: "60px var(--space-4)", textAlign: "center" }}>
                <UploadCloud size={36} style={{ color: "var(--gray-text-muted)", marginBottom: "var(--space-2)", opacity: 0.5 }} />
                <p style={{ fontWeight: 600, fontSize: "14px", color: "var(--gray-text-muted)" }}>
                  No past datasets uploaded.
                </p>
              </div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Upload ID</th>
                    <th>Filename</th>
                    <th>Total Rows</th>
                    <th>Ingestion Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item) => (
                    <tr
                      key={item.id}
                      onClick={() => setActiveUpload(item)}
                      style={{ cursor: "pointer" }}
                    >
                      <td style={{ fontFamily: "var(--font-mono)", fontSize: "13px" }}>
                        {item.upload_id}
                      </td>
                      <td style={{ fontWeight: 600 }}>{item.original_filename}</td>
                      <td>{item.row_count ?? "N/A"}</td>
                      <td>{renderStatusBadge(item.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Basic spin animation styling */}
      <style>{`
        @keyframes spin {
          100% {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  );
};

export default UploadPage;
