import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ShieldAlert,
  Users,
  CheckCircle2,
  XCircle,
  Calendar,
  Building,
  UserCheck,
  UserMinus,
  Loader2,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";
import { useToast } from "../../../shared/hooks/useToast";
import { getErrorMessage } from "../../../shared/utils/errorHandler";

export const AdminPage = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  // 1. Fetch retailer accounts list
  const { data: retailers = [], isLoading, error } = useQuery({
    queryKey: ["adminRetailers"],
    queryFn: async () => {
      const res = await apiClient.get("admin/retailers");
      return res.data;
    },
  });

  // 2. Status patch toggle mutation
  const toggleMutation = useMutation({
    mutationFn: async ({ userId, is_active }) => {
      const res = await apiClient.patch(`admin/retailers/${userId}/status`, {
        is_active,
      });
      return res.data;
    },
    onSuccess: () => {
      // Invalidate query to trigger cache refresh
      queryClient.invalidateQueries({ queryKey: ["adminRetailers"] });
      toast.success("Status Updated", "Retailer account status has been updated successfully.");
    },
    onError: (err) => {
      console.error("Failed to update status", err);
      toast.error("Status Update Failed", getErrorMessage(err, "Failed to update retailer status."));
    },
  });

  const handleToggleStatus = (userId, currentStatus) => {
    const confirmation = window.confirm(
      `Are you sure you want to ${currentStatus ? "deactivate" : "reactivate"} this retailer account?`
    );
    if (confirmation) {
      toggleMutation.mutate({ userId, is_active: !currentStatus });
    }
  };

  // Utility to format date strings
  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (isLoading) {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "var(--space-4)" }}>
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
          <div className="skeleton-card" style={{ height: "100px" }} />
        </div>
        <div className="skeleton-card" style={{ height: "280px" }} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="badge badge-danger" style={{ width: "100%", padding: "var(--space-3)", textTransform: "none" }}>
        <ShieldAlert size={16} />
        <span>Failed to load admin controls list. Admin role clearance required.</span>
      </div>
    );
  }

  // Aggregate metrics locally
  const totalRetailers = retailers.length;
  const activeCount = retailers.filter((r) => r.is_active).length;
  const disabledCount = totalRetailers - activeCount;

  return (
    <div>
      {/* Page Header */}
      <div style={{ marginBottom: "var(--space-5)" }}>
        <h2 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
          Administration
        </h2>
      </div>

      {/* KPI Aggregate cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "var(--space-5)",
          marginBottom: "var(--space-6)",
        }}
      >
        {/* Total Registered Accounts */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyBetween: "true", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              Total Registered Retailers
            </span>
            <div style={{ width: "34px", height: "34px", borderRadius: "10px", backgroundColor: "#EEF2FF", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--accent)" }}>
              <Users size={18} />
            </div>
          </div>
          <span style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {totalRetailers}
          </span>
        </div>

        {/* Active Accounts */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyBetween: "true", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              Active Retailers
            </span>
            <div style={{ width: "34px", height: "34px", borderRadius: "10px", backgroundColor: "#F0FDF4", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--success)" }}>
              <CheckCircle2 size={18} />
            </div>
          </div>
          <span style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {activeCount}
          </span>
        </div>

        {/* Disabled Accounts */}
        <div className="card card-interactive" style={{ display: "flex", flexDirection: "column", gap: "var(--space-2)" }}>
          <div style={{ display: "flex", justifyBetween: "true", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--gray-text-muted)" }}>
              Disabled Accounts
            </span>
            <div style={{ width: "34px", height: "34px", borderRadius: "10px", backgroundColor: "#FEF2F2", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--error)" }}>
              <XCircle size={18} />
            </div>
          </div>
          <span style={{ fontSize: "28px", fontWeight: 800, color: "var(--gray-text-primary)" }}>
            {disabledCount}
          </span>
        </div>
      </div>

      {/* Account Listing Grid Card */}
      <div className="table-container">
        <div
          style={{
            padding: "var(--space-4) var(--space-5)",
            borderBottom: "1px solid var(--gray-border)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <Building size={18} style={{ color: "var(--gray-text-muted)" }} />
          <h3 style={{ fontSize: "16px", fontWeight: 700 }}>Retailer Account Base</h3>
        </div>

        <div className="table-responsive">
          {retailers.length > 0 ? (
            <table className="table">
              <thead>
                <tr>
                  <th>Retailer ID</th>
                  <th>Email Address</th>
                  <th>Business Name</th>
                  <th>Signup Date</th>
                  <th>Account Status</th>
                  <th style={{ textAlign: "right" }}>Status Toggle Actions</th>
                </tr>
              </thead>
              <tbody>
                {retailers.map((row) => (
                  <tr key={row.id}>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "13px" }}>
                      {row.id}
                    </td>
                    <td style={{ fontWeight: 600 }}>{row.email}</td>
                    <td>{row.business_name}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <Calendar size={14} style={{ color: "var(--gray-text-muted)" }} />
                        {formatDate(row.created_at)}
                      </div>
                    </td>
                    <td>
                      {row.is_active ? (
                        <span className="badge badge-success">Active</span>
                      ) : (
                        <span className="badge badge-danger">Disabled</span>
                      )}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        onClick={() => handleToggleStatus(row.id, row.is_active)}
                        className={`btn btn-pill ${row.is_active ? "btn-secondary" : "btn-primary"}`}
                        style={{
                          height: "30px",
                          padding: "0 var(--space-3)",
                          fontSize: "12px",
                          color: row.is_active ? "var(--error)" : "#FFFFFF",
                          borderColor: row.is_active ? "rgba(239, 68, 68, 0.3)" : "transparent",
                          backgroundColor: row.is_active ? "rgba(239, 68, 68, 0.08)" : "var(--accent)",
                        }}
                        disabled={toggleMutation.isPending}
                      >
                        {toggleMutation.isPending &&
                        toggleMutation.variables?.userId === row.id ? (
                          <Loader2 size={12} style={{ animation: "spin 2s linear infinite" }} />
                        ) : row.is_active ? (
                          <>
                            <UserMinus size={12} />
                            Deactivate
                          </>
                        ) : (
                          <>
                            <UserCheck size={12} />
                            Reactivate
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div style={{ padding: "48px var(--space-4)", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
              <div className="empty-state-icon" style={{ width: "44px", height: "44px", marginBottom: "var(--space-3)" }}>
                <Users size={22} />
              </div>
              <h5 style={{ fontSize: "14px", fontWeight: 700, color: "var(--gray-text-primary)", marginBottom: "4px" }}>
                No Retailer Accounts
              </h5>
              <p style={{ fontSize: "12px", color: "var(--gray-text-muted)", maxWidth: "260px" }}>
                New store signups will appear here for administrative control.
              </p>
            </div>
          )}
        </div>
      </div>

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

export default AdminPage;
