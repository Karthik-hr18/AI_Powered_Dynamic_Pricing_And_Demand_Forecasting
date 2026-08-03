import React from "react";
import { useAuth } from "../../../shared/hooks/useAuth";

export const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div>
      <div style={{ marginBottom: "var(--space-6)" }}>
        <h2 style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
          Dashboard Overview
        </h2>
        <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
          Real-time metrics, demand forecasting tracking, and optimization recommendations.
        </p>
      </div>

      <div className="card" style={{ padding: "var(--space-6)" }}>
        <h4 style={{ marginBottom: "var(--space-2)", fontWeight: 700 }}>
          Welcome, {user?.business_name || "Retailer Partner"}!
        </h4>
        <p style={{ color: "var(--gray-text-muted)", fontSize: "14px", marginBottom: "var(--space-4)" }}>
          Your retail account is fully active. Use the sidebar to upload daily sales data spreadsheets, list active product details, or manage configurations.
        </p>

        <div
          style={{
            padding: "var(--space-4)",
            backgroundColor: "var(--gray-bg)",
            borderRadius: "var(--radius-default)",
            border: "1px solid var(--gray-border)",
            fontSize: "13px",
            color: "var(--gray-text-muted)",
          }}
        >
          <p><strong>Account ID:</strong> {user?.id}</p>
          <p><strong>Email Address:</strong> {user?.email}</p>
          <p><strong>Assigned Role:</strong> <span className="badge badge-info">{user?.role}</span></p>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
