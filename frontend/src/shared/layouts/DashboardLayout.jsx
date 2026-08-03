import React, { useState } from "react";
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
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";

export const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

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
      role: ["RETAILER", "ADMIN"],
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
      {/* 1. Desktop Sidebar Container */}
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
        {/* Sidebar Header Brand */}
        <div
          style={{
            padding: "var(--space-5)",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            alignItems: "center",
            gap: "var(--space-2)",
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
            A
          </div>
          <span
            style={{
              fontWeight: 700,
              fontSize: "18px",
              letterSpacing: "-0.015em",
              color: "var(--gray-text-primary)",
            }}
          >
            Antigravity
          </span>
        </div>

        {/* Sidebar Navigation Options */}
        <nav
          style={{
            flex: 1,
            padding: "var(--space-4) var(--space-3)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-1)",
          }}
        >
          {activeNavItems.map((item) => {
            const isActive = location.pathname === item.path;
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
                  color: isActive ? "var(--accent)" : "var(--gray-text-muted)",
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

        {/* Sidebar User Info & Logout Drawer Footer */}
        <div
          style={{
            padding: "var(--space-4)",
            borderTop: "1px solid var(--gray-border)",
            display: "flex",
            flexDirection: "column",
            gap: "var(--space-3)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div
              style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                backgroundColor: "var(--gray-bg)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--gray-text-muted)",
              }}
            >
              <User size={18} />
            </div>
            <div style={{ minWidth: 0 }}>
              <p
                style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  textOverflow: "ellipsis",
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                  color: "var(--gray-text-primary)",
                }}
              >
                {user?.business_name || "Administrator"}
              </p>
              <p
                style={{
                  fontSize: "12px",
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

          <button
            onClick={handleLogout}
            className="btn btn-secondary btn-pill"
            style={{ width: "100%", justifyContent: "center", height: "36px" }}
          >
            <LogOut size={16} />
            Logout
          </button>
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
        <span style={{ fontWeight: 700, fontSize: "16px", color: "var(--gray-text-primary)" }}>
          Antigravity
        </span>
        <button
          onClick={() => setMobileOpen(true)}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            color: "var(--gray-text-primary)",
            padding: "var(--space-1)",
          }}
        >
          <Menu size={24} />
        </button>
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
              <span style={{ fontWeight: 700, fontSize: "16px" }}>Menu</span>
              <button
                onClick={() => setMobileOpen(false)}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "var(--gray-text-primary)",
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
                      color: isActive ? "var(--accent)" : "var(--gray-text-muted)",
                      backgroundColor: isActive
                        ? "rgba(79, 70, 229, 0.08)"
                        : "transparent",
                      fontWeight: isActive ? 600 : 500,
                      textDecoration: "none",
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
