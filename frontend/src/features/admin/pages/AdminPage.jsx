import React from "react";

export const AdminPage = () => {
  return (
    <div>
      <div style={{ marginBottom: "var(--space-6)" }}>
        <h2 style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
          Admin Control Center
        </h2>
        <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
          Oversee retailer platform profiles and synchronize user sessions.
        </p>
      </div>

      <div className="card" style={{ padding: "var(--space-6)" }}>
        <h4 style={{ marginBottom: "var(--space-2)", fontWeight: 700 }}>
          System Administration
        </h4>
        <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
          Use the administrator options here to inspect synced profiles, disable accounts, or toggle database connections.
        </p>
      </div>
    </div>
  );
};

export default AdminPage;
