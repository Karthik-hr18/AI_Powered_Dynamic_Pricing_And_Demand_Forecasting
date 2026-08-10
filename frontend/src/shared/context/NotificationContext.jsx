import React, { createContext, useContext, useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../apiClient";
import { useAuth } from "../hooks/useAuth";

const NotificationContext = createContext(null);

const formatTimeAgo = (dateStr) => {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return "Recently";
    const diffSec = Math.floor((Date.now() - d.getTime()) / 1000);
    if (diffSec < 60) return "Just now";
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)} mins ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} hours ago`;
    return `${Math.floor(diffSec / 86400)} days ago`;
  } catch {
    return "Recently";
  }
};

export const NotificationProvider = ({ children }) => {
  const { user } = useAuth();
  const storageKey = user ? `profitsync_read_notifs_${user.id || user.email}` : "profitsync_read_notifs_guest";
  const prefsStorageKey = user ? `profitsync_notif_prefs_${user.id || user.email}` : "profitsync_notif_prefs_guest";

  const defaultPreferences = {
    stockoutAlerts: true,
    pricingAlerts: true,
    uploadAlerts: true,
    goalAlerts: true,
  };

  const [preferences, setPreferences] = useState(() => {
    try {
      const saved = localStorage.getItem(prefsStorageKey);
      return saved ? { ...defaultPreferences, ...JSON.parse(saved) } : defaultPreferences;
    } catch {
      return defaultPreferences;
    }
  });

  const [readIds, setReadIds] = useState(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Keep storage in sync when user changes
  useEffect(() => {
    try {
      const savedRead = localStorage.getItem(storageKey);
      setReadIds(savedRead ? JSON.parse(savedRead) : []);
      const savedPrefs = localStorage.getItem(prefsStorageKey);
      setPreferences(savedPrefs ? { ...defaultPreferences, ...JSON.parse(savedPrefs) } : defaultPreferences);
    } catch {
      setReadIds([]);
      setPreferences(defaultPreferences);
    }
  }, [storageKey, prefsStorageKey]);

  const updatePreferences = (newPrefs) => {
    const updated = { ...preferences, ...newPrefs };
    setPreferences(updated);
    try {
      localStorage.setItem(prefsStorageKey, JSON.stringify(updated));
    } catch (e) {
      console.warn("Could not save notification preferences:", e);
    }
  };

  // Fetch real-time dashboard data for the active retailer
  const { data: dashboardData, isLoading, refetch } = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: async () => {
      const res = await apiClient.get("dashboard/overview");
      return res.data;
    },
    enabled: !!user && user.role !== "ADMIN",
    staleTime: 30000,
  });

  // Dynamically generate data-specific notifications based on latest analysis and active preferences
  const notifications = useMemo(() => {
    if (!dashboardData) return [];
    const notifs = [];

    // 1. Last Upload Ingestion Status Notification (enforced by uploadAlerts)
    if (preferences.uploadAlerts && dashboardData.last_upload && dashboardData.last_upload.filename) {
      const uploadId = `upload-${dashboardData.last_upload.created_at || dashboardData.last_upload.filename}`;
      const rows = dashboardData.last_upload.total_rows
        ? Number(dashboardData.last_upload.total_rows).toLocaleString("en-IN")
        : "0";
      const status = dashboardData.last_upload.status || "COMPLETED";

      notifs.push({
        id: uploadId,
        type: status === "FAILED" || status === "REJECTED" ? "CRITICAL" : "COMPLETED",
        title: `Dataset ${status === "FAILED" || status === "REJECTED" ? "Upload Failed" : "Processed"}: ${dashboardData.last_upload.filename}`,
        message:
          status === "FAILED" || status === "REJECTED"
            ? "The uploaded file encountered validation errors. Review ingestion history."
            : `Ingested ${rows} sales records. Demand forecasting and pricing recommendations are up to date.`,
        timestamp: dashboardData.last_upload.created_at
          ? formatTimeAgo(dashboardData.last_upload.created_at)
          : "Recent",
        link: "/uploads",
        isRead: readIds.includes(uploadId),
      });
    }

    // 2. Live Critical Stockout / Overstock Risks (enforced by stockoutAlerts)
    if (preferences.stockoutAlerts && dashboardData.critical_risks && dashboardData.critical_risks.length > 0) {
      dashboardData.critical_risks.forEach((risk, idx) => {
        const riskSku = risk.sku || `risk-${idx}`;
        const riskId = `stockout-${riskSku}`;
        notifs.push({
          id: riskId,
          type: "CRITICAL",
          title: `Stockout Risk: ${risk.name || risk.sku}`,
          message:
            risk.reason || "Current inventory cover is critically low against forecast demand velocity.",
          timestamp: "Active Risk",
          link: `/products?search=${encodeURIComponent(risk.sku || risk.name || "")}`,
          isRead: readIds.includes(riskId),
        });
      });
    }

    // 3. Top Price Optimization Opportunities (enforced by pricingAlerts)
    if (preferences.pricingAlerts && dashboardData.top_opportunities && dashboardData.top_opportunities.length > 0) {
      dashboardData.top_opportunities.slice(0, 3).forEach((opp, idx) => {
        const oppSku = opp.sku || `opp-${idx}`;
        const oppId = `pricing-${oppSku}`;
        const recPrice = opp.recommended_price
          ? `₹${Math.round(opp.recommended_price)}`
          : "Recommended";
        const expGain = opp.expected_revenue_gain
          ? `+₹${Math.round(opp.expected_revenue_gain).toLocaleString("en-IN")}`
          : "+Gain";
        notifs.push({
          id: oppId,
          type: "WARNING",
          title: `Price Opportunity: ${opp.product_name || opp.sku}`,
          message: `Recommended price ${recPrice} can expand revenue by ${expGain}.`,
          timestamp: "Recommendation",
          link: `/products?search=${encodeURIComponent(opp.sku || opp.product_name || "")}`,
          isRead: readIds.includes(oppId),
        });
      });
    }

    // 4. Monthly Goal Progress Alert (enforced by goalAlerts)
    if (preferences.goalAlerts && dashboardData.goal_progress && dashboardData.goal_progress.progress_pct !== undefined) {
      const pct = Math.round(dashboardData.goal_progress.progress_pct || 0);
      const rev = Math.round(dashboardData.goal_progress.current_revenue || 0).toLocaleString("en-IN");
      const target = Math.round(dashboardData.goal_progress.target_revenue || 50000).toLocaleString("en-IN");
      const goalId = `goal-tracking-${dashboardData.last_upload?.created_at || "current"}`;

      notifs.push({
        id: goalId,
        type: "INFO",
        title: `Monthly Goal Progress: ${pct}%`,
        message: `Store revenue is ₹${rev} towards your ₹${target} monthly revenue target.`,
        timestamp: "Performance",
        link: "/dashboard",
        isRead: readIds.includes(goalId),
      });
    }

    return notifs;
  }, [dashboardData, readIds, preferences]);

  const unreadCount = useMemo(() => {
    return notifications.filter((n) => !readIds.includes(n.id)).length;
  }, [notifications, readIds]);

  const markAsRead = (id) => {
    if (!id || readIds.includes(id)) return;
    const next = [...readIds, id];
    setReadIds(next);
    try {
      localStorage.setItem(storageKey, JSON.stringify(next));
    } catch (e) {
      console.warn("Could not save read notification state:", e);
    }
  };

  const markAllAsRead = () => {
    const allIds = notifications.map((n) => n.id);
    const merged = Array.from(new Set([...readIds, ...allIds]));
    setReadIds(merged);
    try {
      localStorage.setItem(storageKey, JSON.stringify(merged));
    } catch (e) {
      console.warn("Could not save read notification state:", e);
    }
  };

  const clearAll = () => {
    markAllAsRead();
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        isLoading,
        preferences,
        updatePreferences,
        markAsRead,
        markAllAsRead,
        clearAll,
        refreshNotifications: refetch,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotifications must be used within a NotificationProvider");
  }
  return context;
};
