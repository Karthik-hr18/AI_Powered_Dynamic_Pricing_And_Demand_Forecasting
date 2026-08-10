import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { useAuth } from "../shared/hooks/useAuth";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { RegisterPage } from "../features/auth/pages/RegisterPage";
import { ForgotPasswordPage } from "../features/auth/pages/ForgotPasswordPage";
import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
import { AdminOverviewPage } from "../features/admin/pages/AdminOverviewPage";
import { AdminRetailersPage } from "../features/admin/pages/AdminRetailersPage";
import { AdminDataOperationsPage } from "../features/admin/pages/AdminDataOperationsPage";
import { AdminActivityLogPage } from "../features/admin/pages/AdminActivityLogPage";
import { AdminPlatformHealthPage } from "../features/admin/pages/AdminPlatformHealthPage";
import { AdminReportsPage } from "../features/admin/pages/AdminReportsPage";

import { AuthLayout } from "../shared/layouts/AuthLayout";
import { DashboardLayout } from "../shared/layouts/DashboardLayout";
import { EmailVerificationBanner } from "../shared/components/EmailVerificationBanner";

import { UploadPage } from "../features/uploads/pages/UploadPage";
import { ProductsListPage } from "../features/products/pages/ProductsListPage";

import { LandingPage } from "../features/landing/pages/LandingPage";

const LoadingScreen = () => (
  <div
    style={{
      display: "flex",
      minHeight: "100vh",
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "var(--gray-bg)",
    }}
  >
    <div className="skeleton-card" style={{ width: "320px", height: "120px" }} />
  </div>
);

// Route guard requiring authenticated user session
// Also renders the email-verification overlay for unverified retailers
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user, isEmailVerified } = useAuth();

  if (loading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (user?.role === "ADMIN") return <Navigate to="/admin" replace />;

  // Retailers must verify their email before accessing the platform
  const needsVerification =
    user?.role === "RETAILER" && !isEmailVerified;

  return (
    <DashboardLayout>
      {needsVerification && <EmailVerificationBanner />}
      {children}
    </DashboardLayout>
  );
};

// Route guard requiring admin privileges
const AdminRoute = ({ children }) => {
  const { user, isAuthenticated, loading } = useAuth();

  if (loading) return <LoadingScreen />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== "ADMIN") return <Navigate to="/dashboard" replace />;

  return <DashboardLayout>{children}</DashboardLayout>;
};

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Pages */}
      <Route
        path="/login"
        element={
          <AuthLayout>
            <LoginPage />
          </AuthLayout>
        }
      />
      <Route
        path="/register"
        element={
          <AuthLayout>
            <RegisterPage />
          </AuthLayout>
        }
      />
      <Route
        path="/forgot-password"
        element={
          <AuthLayout>
            <ForgotPasswordPage />
          </AuthLayout>
        }
      />

      {/* Authenticated Retailer Pages */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/uploads"
        element={
          <ProtectedRoute>
            <UploadPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/products"
        element={
          <ProtectedRoute>
            <ProductsListPage />
          </ProtectedRoute>
        }
      />

      {/* Admin Console Pages */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminOverviewPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/retailers"
        element={
          <AdminRoute>
            <AdminRetailersPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/data-operations"
        element={
          <AdminRoute>
            <AdminDataOperationsPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/activity-log"
        element={
          <AdminRoute>
            <AdminActivityLogPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/platform-health"
        element={
          <AdminRoute>
            <AdminPlatformHealthPage />
          </AdminRoute>
        }
      />
      <Route
        path="/admin/reports"
        element={
          <AdminRoute>
            <AdminReportsPage />
          </AdminRoute>
        }
      />

      {/* Fallback Redirections */}
      <Route path="/" element={<LandingPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppRoutes;
