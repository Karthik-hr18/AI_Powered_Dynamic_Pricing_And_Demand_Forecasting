import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Users,
  Search,
  CheckCircle2,
  XCircle,
  Eye,
  UserCheck,
  UserX,
  Filter,
  ShieldAlert,
  Building,
  Calendar,
} from "lucide-react";

import { apiClient } from "../../../shared/apiClient";
import { useToast } from "../../../shared/hooks/useToast";
import { getErrorMessage } from "../../../shared/utils/errorHandler";
import { formatInteger } from "../../../shared/utils/formatters";
import { RetailerDetailDrawer } from "../components/RetailerDetailDrawer";
import { ConfirmStatusModal } from "../components/ConfirmStatusModal";

export const AdminRetailersPage = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedRetailerId, setSelectedRetailerId] = useState(null);
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [retailerToToggle, setRetailerToToggle] = useState(null);

  // 1. Fetch retailer accounts list
  const { data: retailers = [], isLoading, error } = useQuery({
    queryKey: ["adminRetailers"],
    queryFn: async () => {
      const res = await apiClient.get("admin/retailers");
      return res.data;
    },
  });

  // 2. Status toggle mutation
  const toggleMutation = useMutation({
    mutationFn: async ({ userId, is_active }) => {
      const res = await apiClient.patch(`admin/retailers/${userId}/status`, {
        is_active,
      });
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["adminRetailers"] });
      queryClient.invalidateQueries({ queryKey: ["adminRetailerDetail", data.id] });
      queryClient.invalidateQueries({ queryKey: ["adminOverview"] });
      setConfirmModalOpen(false);
      setRetailerToToggle(null);
      toast.success(
        "Account Status Updated",
        `Retailer account status set to ${data.is_active ? "Active" : "Disabled"}.`
      );
    },
    onError: (err) => {
      toast.error("Status Update Failed", getErrorMessage(err, "Failed to update retailer status."));
    },
  });

  const handleOpenToggleModal = (retailer) => {
    setRetailerToToggle(retailer);
    setConfirmModalOpen(true);
  };

  const handleConfirmToggle = () => {
    if (retailerToToggle) {
      toggleMutation.mutate({
        userId: retailerToToggle.id,
        is_active: !retailerToToggle.is_active,
      });
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  // Filter retailers
  const filteredRetailers = retailers.filter((r) => {
    const matchesSearch =
      (r.business_name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (r.email || "").toLowerCase().includes(searchTerm.toLowerCase());

    if (statusFilter === "ACTIVE") return matchesSearch && r.is_active;
    if (statusFilter === "DISABLED") return matchesSearch && !r.is_active;
    return matchesSearch;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--space-6)" }}>
      {/* Page Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "var(--space-3)" }}>
        <div>
          <h1 style={{ fontSize: "24px", fontWeight: 800, color: "var(--gray-text-primary)", margin: 0 }}>
            Retailer Account Management
          </h1>
          <p style={{ fontSize: "13px", color: "var(--gray-text-muted)", margin: "4px 0 0" }}>
            Monitor and administer registered retailer profiles, catalog footprints, and platform access.
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="card" style={{ padding: "var(--space-4)" }}>
        <div style={{ display: "flex", gap: "var(--space-4)", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between" }}>
          {/* Search */}
          <div style={{ position: "relative", minWidth: "260px", flex: 1 }}>
            <Search
              size={16}
              style={{
                position: "absolute",
                left: "12px",
                top: "50%",
                transform: "translateY(-50%)",
                color: "var(--gray-text-muted)",
              }}
            />
            <input
              type="text"
              placeholder="Search by business name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input"
              style={{ paddingLeft: "36px", height: "38px" }}
            />
          </div>

          {/* Status Tabs */}
          <div style={{ display: "flex", gap: "var(--space-1)", backgroundColor: "var(--gray-surface)", padding: "3px", borderRadius: "var(--radius-default)", border: "1px solid var(--gray-border)" }}>
            <button
              onClick={() => setStatusFilter("ALL")}
              style={{
                padding: "6px 12px",
                border: "none",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                backgroundColor: statusFilter === "ALL" ? "#FFFFFF" : "transparent",
                color: statusFilter === "ALL" ? "var(--accent)" : "var(--gray-text-muted)",
                boxShadow: statusFilter === "ALL" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
              }}
            >
              All ({retailers.length})
            </button>
            <button
              onClick={() => setStatusFilter("ACTIVE")}
              style={{
                padding: "6px 12px",
                border: "none",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                backgroundColor: statusFilter === "ACTIVE" ? "#FFFFFF" : "transparent",
                color: statusFilter === "ACTIVE" ? "var(--success)" : "var(--gray-text-muted)",
                boxShadow: statusFilter === "ACTIVE" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
              }}
            >
              Active ({retailers.filter((r) => r.is_active).length})
            </button>
            <button
              onClick={() => setStatusFilter("DISABLED")}
              style={{
                padding: "6px 12px",
                border: "none",
                borderRadius: "4px",
                fontSize: "12px",
                fontWeight: 600,
                cursor: "pointer",
                backgroundColor: statusFilter === "DISABLED" ? "#FFFFFF" : "transparent",
                color: statusFilter === "DISABLED" ? "var(--error)" : "var(--gray-text-muted)",
                boxShadow: statusFilter === "DISABLED" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
              }}
            >
              Disabled ({retailers.filter((r) => !r.is_active).length})
            </button>
          </div>
        </div>
      </div>

      {/* Retailers Table Card */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {isLoading ? (
          <div style={{ padding: "var(--space-6)", display: "flex", flexDirection: "column", gap: "var(--space-3)" }}>
            <div className="skeleton-card" style={{ height: "40px" }} />
            <div className="skeleton-card" style={{ height: "40px" }} />
            <div className="skeleton-card" style={{ height: "40px" }} />
          </div>
        ) : error ? (
          <div style={{ padding: "var(--space-6)", textAlign: "center" }}>
            <ShieldAlert size={32} style={{ color: "var(--error)", margin: "0 auto var(--space-2)" }} />
            <div style={{ fontWeight: 700, color: "var(--error)" }}>Failed to Load Retailers</div>
          </div>
        ) : filteredRetailers.length === 0 ? (
          <div style={{ padding: "var(--space-8)", textAlign: "center", color: "var(--gray-text-muted)" }}>
            <Users size={36} style={{ margin: "0 auto var(--space-3)", opacity: 0.5 }} />
            <div style={{ fontSize: "15px", fontWeight: 700, color: "var(--gray-text-primary)", marginBottom: "4px" }}>
              No retailers found
            </div>
            <div style={{ fontSize: "13px" }}>
              {searchTerm ? "Try searching with a different term." : "No retailers registered yet."}
            </div>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table" style={{ margin: 0 }}>
              <thead>
                <tr>
                  <th>Retailer Business</th>
                  <th>Status</th>
                  <th style={{ textAlign: "center" }}>Datasets</th>
                  <th style={{ textAlign: "center" }}>Sales Records</th>
                  <th style={{ textAlign: "center" }}>Products</th>
                  <th>Last Active</th>
                  <th>Registered</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRetailers.map((r) => (
                  <tr
                    key={r.id}
                    style={{ cursor: "pointer" }}
                    onClick={() => setSelectedRetailerId(r.id)}
                  >
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <div
                          style={{
                            width: "34px",
                            height: "34px",
                            borderRadius: "8px",
                            backgroundColor: "rgba(79, 70, 229, 0.08)",
                            color: "var(--accent)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontWeight: 800,
                            fontSize: "14px",
                          }}
                        >
                          {r.business_name ? r.business_name.charAt(0).toUpperCase() : "R"}
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, color: "var(--gray-text-primary)" }}>
                            {r.business_name}
                          </div>
                          <div style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                            {r.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span
                        className={`badge ${r.is_active ? "badge-success" : "badge-danger"}`}
                        style={{ fontSize: "11px", fontWeight: 700 }}
                      >
                        {r.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td style={{ textAlign: "center", fontWeight: 700 }}>
                      {formatInteger(r.dataset_count)}
                    </td>
                    <td style={{ textAlign: "center", fontWeight: 700, color: "var(--success)" }}>
                      {formatInteger(r.sales_record_count)}
                    </td>
                    <td style={{ textAlign: "center", fontWeight: 700, color: "var(--purple)" }}>
                      {formatInteger(r.product_count)}
                    </td>
                    <td style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                      {formatDate(r.last_active_at)}
                    </td>
                    <td style={{ fontSize: "12px", color: "var(--gray-text-muted)" }}>
                      {formatDate(r.created_at)}
                    </td>
                    <td style={{ textAlign: "right" }} onClick={(e) => e.stopPropagation()}>
                      <div style={{ display: "inline-flex", gap: "var(--space-2)" }}>
                        <button
                          onClick={() => setSelectedRetailerId(r.id)}
                          className="btn btn-secondary"
                          style={{ height: "30px", fontSize: "11px", padding: "0 8px" }}
                        >
                          <Eye size={12} />
                          Details
                        </button>
                        <button
                          onClick={() => handleOpenToggleModal(r)}
                          className={r.is_active ? "btn btn-danger" : "btn btn-primary"}
                          style={{ height: "30px", fontSize: "11px", padding: "0 8px" }}
                        >
                          {r.is_active ? <UserX size={12} /> : <UserCheck size={12} />}
                          {r.is_active ? "Disable" : "Reactivate"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Retailer Detail Slide-Over Drawer */}
      <RetailerDetailDrawer
        isOpen={!!selectedRetailerId}
        onClose={() => setSelectedRetailerId(null)}
        retailerId={selectedRetailerId}
        onToggleStatus={(retailer) => handleOpenToggleModal(retailer)}
      />

      {/* Confirmation Modal */}
      <ConfirmStatusModal
        isOpen={confirmModalOpen}
        onClose={() => {
          setConfirmModalOpen(false);
          setRetailerToToggle(null);
        }}
        onConfirm={handleConfirmToggle}
        retailerName={retailerToToggle?.business_name}
        currentStatus={retailerToToggle?.is_active}
        isLoading={toggleMutation.isPending}
      />
    </div>
  );
};
