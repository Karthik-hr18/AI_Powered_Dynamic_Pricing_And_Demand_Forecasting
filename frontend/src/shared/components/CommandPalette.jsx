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
      label: "Go to Executive Dashboard",
      category: "Navigation",
      icon: <LayoutDashboard size={16} />,
      perform: () => {
        navigate("/dashboard");
        onClose();
      },
    },
    {
      id: "nav-products",
      label: "Browse Product Catalogue",
      category: "Navigation",
      icon: <ShoppingBag size={16} />,
      perform: () => {
        navigate("/products");
        onClose();
      },
    },
    {
      id: "nav-uploads",
      label: "Upload Sales CSV",
      category: "Actions",
      icon: <UploadCloud size={16} />,
      perform: () => {
        navigate("/uploads");
        onClose();
      },
    },
    {
      id: "action-reports",
      label: "Open Report Center (PDF, Excel, CSV)",
      category: "Reports",
      icon: <FileText size={16} />,
      perform: () => {
        onClose();
        if (onOpenReportCenter) onOpenReportCenter();
      },
    },
    {
      id: "action-search-milk",
      label: "Search SKU: Organic Whole Milk 1L",
      category: "Quick Search",
      icon: <Zap size={16} />,
      perform: () => {
        navigate("/products?search=milk");
        onClose();
      },
    },
    {
      id: "nav-admin",
      label: "Open Admin Management Portal",
      category: "Admin",
      icon: <ShieldCheck size={16} />,
      perform: () => {
        navigate("/admin");
        onClose();
      },
    },
  ];

  const filteredActions = actions.filter(
    (item) =>
      item.label.toLowerCase().includes(query.toLowerCase()) ||
      item.category.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <>
      <div className="slide-drawer-backdrop" onClick={onClose} style={{ zIndex: 100 }} />
      <div
        style={{
          position: "fixed",
          top: "15%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "90%",
          maxWidth: "600px",
          backgroundColor: "#1E293B",
          border: "1px solid var(--gray-border)",
          borderRadius: "var(--radius-lg)",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4)",
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
          }}
        >
          <Search size={18} style={{ color: "var(--accent)" }} />
          <input
            type="text"
            placeholder="Type a command or search (e.g. Milk, Upload, Reports)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            style={{
              flex: 1,
              background: "none",
              border: "none",
              color: "#FFFFFF",
              fontSize: "14px",
              outline: "none",
            }}
          />
          <span
            style={{
              fontSize: "11px",
              backgroundColor: "rgba(255, 255, 255, 0.1)",
              padding: "2px 6px",
              borderRadius: "4px",
              color: "var(--gray-text-muted)",
              fontFamily: "var(--font-mono)",
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
                  <div style={{ color: "var(--accent)" }}>{action.icon}</div>
                  <div>
                    <span style={{ fontSize: "14px", fontWeight: 600, color: "#FFFFFF", display: "block" }}>
                      {action.label}
                    </span>
                    <span style={{ fontSize: "11px", color: "var(--gray-text-muted)" }}>
                      {action.category}
                    </span>
                  </div>
                </div>
                <ArrowRight size={14} style={{ color: "var(--gray-text-muted)" }} />
              </div>
            ))
          ) : (
            <div style={{ padding: "var(--space-5)", textAlign: "center", color: "var(--gray-text-muted)", fontSize: "13px" }}>
              No commands matching "{query}". Try searching for <strong>Upload</strong> or <strong>Reports</strong>.
            </div>
          )}
        </div>

        {/* Footer info */}
        <div
          style={{
            padding: "8px 16px",
            backgroundColor: "rgba(15, 23, 42, 0.6)",
            borderTop: "1px solid var(--gray-border)",
            fontSize: "11px",
            color: "var(--gray-text-muted)",
            display: "flex",
            justifyContent: "space-between",
          }}
        >
          <span>Tip: Press <strong>Ctrl + K</strong> anywhere to toggle command palette</span>
          <span>AI Engine v1.0</span>
        </div>
      </div>
      <style>{`
        .command-item-hover:hover {
          background-color: rgba(99, 102, 241, 0.15) !important;
        }
      `}</style>
    </>
  );
};
