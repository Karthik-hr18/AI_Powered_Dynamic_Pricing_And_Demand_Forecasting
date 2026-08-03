import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import { useAuth } from "../shared/hooks/useAuth";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { RegisterPage } from "../features/auth/pages/RegisterPage";
import { ForgotPasswordPage } from "../features/auth/pages/ForgotPasswordPage";
import { DashboardPage } from "../features/dashboard/pages/DashboardPage";
import { AdminPage } from "../features/admin/pages/AdminPage";

import { AuthLayout } from "../shared/layouts/AuthLayout";
import { DashboardLayout } from "../shared/layouts/DashboardLayout";
import { EmailVerificationBanner } from "../shared/components/EmailVerificationBanner";

import { UploadPage } from "../features/uploads/pages/UploadPage";

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

      {/* Authenticated Pages */}
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
            <div className="card">
              <h3>Product Catalogue</h3>
              <p style={{ color: "var(--gray-text-muted)", fontSize: "14px" }}>
                Product grid details and analytical panels will be implemented in Milestone 12.
              </p>
            </div>
          </ProtectedRoute>
        }
      />

      {/* Admin Pages */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        }
      />

      {/* Fallback Redirections */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default AppRoutes;
