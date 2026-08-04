import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Menu,
  X,
  LayoutDashboard,
  UploadCloud,
  ShoppingBag,
  ShieldCheck,
  LogOut,
  User,
  Bell,
  Search,
  FileText,
  Sparkles,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { CommandPalette } from "../components/CommandPalette";
import { NotificationCenter } from "../components/NotificationCenter";
import { ReportCenterModal } from "../components/ReportCenterModal";
import { UserProfileMenu } from "../components/UserProfileMenu";

export const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Modals & Drawers state
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false);
  const [reportCenterOpen, setReportCenterOpen] = useState(false);
  const [userProfileMenuOpen, setUserProfileMenuOpen] = useState(false);

  // Custom listener for command palette trigger
  useEffect(() => {
    const handleOpenCommandPalette = () => setCommandPaletteOpen(true);
    window.addEventListener("open-command-palette", handleOpenCommandPalette);
    return () => window.removeEventListener("open-command-palette", handleOpenCommandPalette);
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (e) {
      console.error("Logout failed", e);
    }
  };

  const navItems = [
    {
      label: "Dashboard",
      path: "/dashboard",
      icon: <LayoutDashboard size={20} />,
      role: ["RETAILER"],
    },
    {
      label: "Upload Data",
      path: "/uploads",
      icon: <UploadCloud size={20} />,
      role: ["RETAILER"],
    },
    {
      label: "Products List",
      path: "/products",
      icon: <ShoppingBag size={20} />,
      role: ["RETAILER"],
    },
    {
      label: "Report Center",
      path: "#reports",
      isAction: true,
      action: () => setReportCenterOpen(true),
      icon: <FileText size={20} />,
      role: ["RETAILER"],
    },
    {
      label: "Admin Portal",
      path: "/admin",
      icon: <ShieldCheck size={20} />,
      role: ["ADMIN"],
    },
  ];

  // Filter navigation items by active user role
  const activeNavItems = navItems.filter((item) =>
    item.role.includes(user?.role)
  );

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        backgroundColor: "var(--gray-bg)",
      }}
    >
      {/* Modals & Drawers */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onOpenReportCenter={() => setReportCenterOpen(true)}
      />
      <NotificationCenter
        isOpen={notificationCenterOpen}
        onClose={() => setNotificationCenterOpen(false)}
      />
      <ReportCenterModal
        isOpen={reportCenterOpen}
        onClose={() => setReportCenterOpen(false)}
      />
      <UserProfileMenu
        isOpen={userProfileMenuOpen}
        onClose={() => setUserProfileMenuOpen(false)}
      />

      {/* 1. Primary Desktop Navigation Sidebar */}
      <aside
        style={{
          width: "260px",
          backgroundColor: "var(--gray-surface)",
          borderRight: "1px solid var(--gray-border)",
          display: "flex",
          flexDirection: "column",
          position: "fixed",
          top: 0,
          bottom: 0,
          left: 0,
          zIndex: 10,
        }}
        className="desktop-sidebar"
      >
        {/* Sidebar Brand Header */}
        <div
          style={{
            padding: "var(--space-5) var(--space-4)",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            alignItems: "center",
            gap: "var(--space-3)",
          }}
        >
          <div
            style={{
              width: "36px",
              height: "36px",
              borderRadius: "8px",
              backgroundColor: "var(--accent)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              fontWeight: 800,
              fontSize: "18px",
            }}
          >
            P
          </div>
          <span
            style={{
              fontWeight: 700,
              fontSize: "18px",
              letterSpacing: "-0.015em",
              color: "var(--gray-text-primary)",
            }}
          >
            ProfitSync
          </span>
        </div>

        {/* Global Search & Command Palette Button */}
        <div style={{ padding: "var(--space-3) var(--space-4)" }}>
          <button
            onClick={() => setCommandPaletteOpen(true)}
            style={{
              width: "100%",
              height: "36px",
              backgroundColor: "#FFFFFF",
              border: "1px solid var(--gray-border)",
              borderRadius: "var(--radius-default)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "0 10px",
              color: "var(--gray-text-muted)",
              fontSize: "13px",
              cursor: "pointer",
              boxShadow: "0 1px 2px rgba(0, 0, 0, 0.04)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Search size={14} style={{ color: "var(--gray-text-muted)" }} />
              <span>Search or type Ctrl+K...</span>
            </div>
            <span
              style={{
                fontSize: "10px",
                backgroundColor: "#F1F5F9",
                color: "var(--gray-text-muted)",
                padding: "2px 5px",
                borderRadius: "4px",
                fontFamily: "var(--font-mono)",
                border: "1px solid var(--gray-border)",
              }}
            >
              Ctrl+K
            </span>
          </button>
        </div>

        {/* Sidebar Navigation Options */}
        <nav
          style={{
            flex: 1,
            padding: "var(--space-2) var(--space-3)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-1)",
          }}
        >
          {activeNavItems.map((item) => {
            const isActive = location.pathname === item.path;
            if (item.isAction) {
              return (
                <button
                  key={item.label}
                  onClick={item.action}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "var(--space-3)",
                    padding: "10px var(--space-3)",
                    borderRadius: "var(--radius-default)",
                    color: "var(--gray-text-primary)",
                    backgroundColor: "transparent",
                    fontFamily: "inherit",
                    fontWeight: 500,
                    fontSize: "14px",
                    lineHeight: "1.5",
                    border: "none",
                    cursor: "pointer",
                    textAlign: "left",
                    width: "100%",
                    transition: "all var(--transition-speed-fast) var(--transition-timing)",
                  }}
                  className="sidebar-link"
                >
                  {item.icon}
                  {item.label}
                </button>
              );
            }
            return (
              <Link
                key={item.path}
                to={item.path}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "var(--space-3)",
                  padding: "10px var(--space-3)",
                  borderRadius: "var(--radius-default)",
                  color: isActive ? "var(--accent)" : "var(--gray-text-primary)",
                  backgroundColor: isActive
                    ? "rgba(79, 70, 229, 0.08)"
                    : "transparent",
                  fontWeight: isActive ? 600 : 500,
                  fontSize: "14px",
                  textDecoration: "none",
                  transition: "all var(--transition-speed-fast) var(--transition-timing)",
                }}
                className="sidebar-link"
              >
                {item.icon}
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer & Profile Trigger */}
        <div
          style={{
            padding: "var(--space-4)",
            borderTop: "1px solid var(--gray-border)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-3)",
          }}
        >
          <div
            onClick={() => setUserProfileMenuOpen(!userProfileMenuOpen)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              cursor: "pointer",
              padding: "6px",
              borderRadius: "var(--radius-default)",
              backgroundColor: "rgba(255, 255, 255, 0.03)",
            }}
          >
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                backgroundColor: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#FFFFFF",
                fontWeight: 700,
                fontSize: "14px",
                flexShrink: 0,
              }}
            >
              {user?.business_name ? user.business_name[0].toUpperCase() : "U"}
            </div>
            <div style={{ overflow: "hidden", flex: 1 }}>
              <p
                style={{
                  fontWeight: 600,
                  fontSize: "13px",
                  color: "var(--gray-text-primary)",
                  textOverflow: "ellipsis",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                }}
              >
                {user?.business_name || "Administrator"}
              </p>
              <p
                style={{
                  fontSize: "11px",
                  color: "var(--gray-text-muted)",
                  textOverflow: "ellipsis",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                }}
              >
                {user?.email}
              </p>
            </div>
          </div>

          <div
            onClick={() => setNotificationCenterOpen(!notificationCenterOpen)}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "6px 12px",
              backgroundColor: "rgba(15, 23, 42, 0.5)",
              borderRadius: "var(--radius-default)",
              border: "1px solid var(--gray-border)",
              cursor: "pointer",
            }}
          >
            <span style={{ fontSize: "12px", color: "var(--gray-text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
              <Bell size={14} style={{ color: "var(--accent)" }} /> Notifications
            </span>
            <span className="badge badge-danger" style={{ fontSize: "10px", padding: "2px 6px" }}>
              4 New
            </span>
          </div>
        </div>
      </aside>

      {/* 2. Mobile Responsive Top Nav Bar */}
      <header
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          height: "60px",
          backgroundColor: "var(--gray-surface)",
          borderBottom: "1px solid var(--gray-border)",
          display: "none",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 var(--space-4)",
          zIndex: 20,
        }}
        className="mobile-header"
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            style={{
              width: "28px",
              height: "28px",
              borderRadius: "6px",
              backgroundColor: "var(--accent)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFFFFF",
              fontWeight: 800,
              fontSize: "14px",
            }}
          >
            P
          </div>
          <span style={{ fontWeight: 800, fontSize: "16px", color: "var(--gray-text-primary)" }}>
            ProfitSync
          </span>
        </div>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            onClick={() => setCommandPaletteOpen(true)}
            style={{ background: "none", border: "none", color: "var(--gray-text-primary)", cursor: "pointer", padding: "6px" }}
          >
            <Search size={20} />
          </button>
          <button
            onClick={() => setNotificationCenterOpen(true)}
            style={{ background: "none", border: "none", color: "var(--gray-text-primary)", cursor: "pointer", position: "relative", padding: "6px" }}
          >
            <Bell size={20} />
          </button>
          <button
            onClick={() => setMobileOpen(true)}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--gray-text-primary)",
              padding: "6px",
            }}
          >
            <Menu size={24} />
          </button>
        </div>
      </header>

      {/* 3. Mobile Navigation Drawer Slide-Over */}
      {mobileOpen && (
        <div style={{ display: "none" }} className="mobile-nav-wrapper">
          <div
            className="slide-drawer-backdrop"
            onClick={() => setMobileOpen(false)}
          />
          <div className="slide-drawer" style={{ width: "300px" }}>
            <div
              style={{
                padding: "var(--space-4)",
                borderBottom: "1px solid var(--gray-border)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <div
                  style={{
                    width: "28px",
                    height: "28px",
                    borderRadius: "6px",
                    backgroundColor: "var(--accent)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#FFFFFF",
                    fontWeight: 800,
                    fontSize: "14px",
                  }}
                >
                  P
                </div>
                <span style={{ fontWeight: 800, fontSize: "16px" }}>ProfitSync Menu</span>
              </div>
              <button
                onClick={() => setMobileOpen(false)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "var(--gray-text-primary)",
                  padding: "6px",
                }}
              >
                <X size={24} />
              </button>
            </div>

            <nav
              style={{
                flex: 1,
                padding: "var(--space-4)",
                display: "flex",
                flexDirection: "column",
                gap: "var(--space-2)",
              }}
            >
              {activeNavItems.map((item) => {
                const isActive = location.pathname === item.path;
                if (item.isAction) {
                  return (
                    <button
                      key={item.label}
                      onClick={() => {
                        setMobileOpen(false);
                        if (item.action) item.action();
                      }}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "var(--space-3)",
                        padding: "12px var(--space-3)",
                        borderRadius: "var(--radius-default)",
                        color: "var(--gray-text-primary)",
                        backgroundColor: "transparent",
                        fontFamily: "inherit",
                        fontWeight: 500,
                        fontSize: "14px",
                        border: "none",
                        cursor: "pointer",
                        textAlign: "left",
                        width: "100%",
                        minHeight: "44px",
                      }}
                    >
                      {item.icon}
                      {item.label}
                    </button>
                  );
                }
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "var(--space-3)",
                      padding: "12px var(--space-3)",
                      borderRadius: "var(--radius-default)",
                      color: isActive ? "var(--accent)" : "var(--gray-text-primary)",
                      backgroundColor: isActive
                        ? "rgba(79, 70, 229, 0.08)"
                        : "transparent",
                      fontWeight: isActive ? 600 : 500,
                      textDecoration: "none",
                      minHeight: "44px",
                    }}
                  >
                    {item.icon}
                    {item.label}
                  </Link>
                );
              })}
            </nav>

            <div
              style={{
                padding: "var(--space-4)",
                borderTop: "1px solid var(--gray-border)",
                display: "flex",
                flexDirection: "column",
                gap: "var(--space-3)",
              }}
            >
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span style={{ fontSize: "13px", fontWeight: 600 }}>
                  {user?.business_name}
                </span>
                <span style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                  {user?.email}
                </span>
              </div>
              <button
                onClick={() => {
                  setMobileOpen(false);
                  handleLogout();
                }}
                className="btn btn-secondary btn-pill"
                style={{ width: "100%", justifyContent: "center" }}
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. Main Page Content Workspace */}
      <main
        style={{
          flex: 1,
          marginLeft: "260px",
          padding: "var(--space-6) var(--space-6) var(--space-8) var(--space-6)",
          minWidth: 0,
        }}
        className="main-workspace-stage"
      >
        <div style={{ maxWidth: "1240px", margin: "0 auto" }}>{children}</div>
      </main>

      {/* Responsive layout-shifting styles */}
      <style>{`
        @media (max-width: 991px) {
          .desktop-sidebar {
            display: none !important;
          }
          .mobile-header {
            display: flex !important;
          }
          .mobile-nav-wrapper {
            display: block !important;
          }
          .main-workspace-stage {
            margin-left: 0 !important;
            padding-top: 80px !important;
          }
        }
      `}</style>
    </div>
  );
};

export default DashboardLayout;
