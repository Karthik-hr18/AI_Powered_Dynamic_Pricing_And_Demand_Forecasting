import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  UploadCloud,
  RefreshCw,
  FileText,
  ShoppingBag,
  LayoutDashboard,
  ShieldCheck,
  Zap,
  X,
  ArrowRight,
} from "lucide-react";

export const CommandPalette = ({ isOpen, onClose, onOpenReportCenter }) => {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  // Keyboard shortcut listener (Ctrl+K or Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Trigger open
          window.dispatchEvent(new CustomEvent("open-command-palette"));
        }
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const actions = [
    {
      id: "nav-dash",
      label: "Go to Dashboard",
      category: "Navigation",
      icon: <LayoutDashboard size={16} />,
      perform: () => {
        navigate("/dashboard");
        onClose();
      },
    },
    {
      id: "nav-products",
      label: "Browse Products",
      category: "Navigation",
      icon: <ShoppingBag size={16} />,
      perform: () => {
        navigate("/products");
        onClose();
      },
    },
    {
      id: "nav-uploads",
      label: "Upload Sales Data",
      category: "Navigation",
      icon: <UploadCloud size={16} />,
      perform: () => {
        navigate("/uploads");
        onClose();
      },
    },
    {
      id: "nav-admin",
      label: "Administration",
      category: "Navigation",
      icon: <ShieldCheck size={16} />,
      perform: () => {
        navigate("/admin");
        onClose();
      },
    },
    {
      id: "act-report",
      label: "Open Report Center (PDF Export)",
      category: "Actions",
      icon: <FileText size={16} style={{ color: "var(--accent)" }} />,
      perform: () => {
        onClose();
        onOpenReportCenter();
      },
    },
    {
      id: "act-analysis",
      label: "Run AI Analysis",
      category: "Actions",
      icon: <RefreshCw size={16} style={{ color: "#10B981" }} />,
      perform: () => {
        onClose();
        alert("Running AI Analysis...");
      },
    },
  ];

  const filteredActions = actions.filter((item) =>
    item.label.toLowerCase().includes(query.toLowerCase()) ||
    item.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} style={{ zIndex: 100 }} />
      <div
        style={{
          position: "fixed",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "90%",
          maxWidth: "600px",
          backgroundColor: "#FFFFFF",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-card)",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.15)",
          zIndex: 101,
          overflow: "hidden",
        }}
      >
        {/* Search input header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            padding: "var(--space-3) var(--space-4)",
            borderBottom: "1px solid var(--gray-border)",
            gap: "var(--space-3)",
            backgroundColor: "#FFFFFF",
          }}
        >
          <Search size={18} style={{ color: "var(--gray-text-muted)" }} />
          <input
            type="text"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            style={{
              flex: 1,
              background: "none",
              border: "none",
              color: "var(--gray-text-primary)",
              fontSize: "14px",
              outline: "none",
            }}
          />
          <span
            style={{
              fontSize: "11px",
              backgroundColor: "#F1F5F9",
              padding: "2px 6px",
              borderRadius: "4px",
              color: "var(--gray-text-muted)",
              fontFamily: "var(--font-mono)",
              border: "1px solid var(--gray-border)",
            }}
          >
            ESC to close
          </span>
          <button
            onClick={onClose}
            style={{ background: "none", border: "none", color: "var(--gray-text-muted)", cursor: "pointer" }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Command list */}
        <div style={{ maxHeight: "340px", overflowY: "auto", padding: "var(--space-2)" }}>
          {filteredActions.length > 0 ? (
            filteredActions.map((action) => (
              <div
                key={action.id}
                onClick={action.perform}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "var(--space-3) var(--space-4)",
                  borderRadius: "var(--radius-default)",
                  cursor: "pointer",
                  transition: "background-color 0.15s",
                }}
                className="command-item-hover"
              >
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-3)" }}>
                  <div style={{ color: "var(--gray-text-muted)" }}>{action.icon}</div>
                  <span style={{ fontSize: "14px", color: "var(--gray-text-primary)", fontWeight: 500 }}>
                    {action.label}
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "var(--space-2)" }}>
                  <span
                    style={{
                      fontSize: "10px",
                      backgroundColor: "#EEF2FF",
                      color: "var(--accent)",
                      padding: "2px 6px",
                      borderRadius: "4px",
                      fontWeight: 600,
                    }}
                  >
                    {action.category}
                  </span>
                  <ArrowRight size={14} style={{ color: "var(--gray-text-muted)" }} />
                </div>
              </div>
            ))
          ) : (
            <div style={{ padding: "var(--space-6)", textAlign: "center", color: "var(--gray-text-muted)", fontSize: "13px" }}>
              No commands match "{query}"
            </div>
          )}
        </div>
      </div>

      <style>{`
        .command-item-hover:hover {
          background-color: #F8FAFC !important;
        }
      `}</style>
    </>
  );
};
