import React, { createContext, useContext, useEffect, useState } from "react";
import {
  createUserWithEmailAndPassword,
  onIdTokenChanged,
  sendEmailVerification,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signOut,
  reload,
} from "firebase/auth";

import { auth } from "../firebase/config";
import { apiClient } from "../apiClient";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isMockMode =
    !import.meta.env.VITE_FIREBASE_API_KEY ||
    import.meta.env.VITE_FIREBASE_API_KEY.includes("placeholder");

  // Sync Firebase auth state with backend MongoDB profile
  useEffect(() => {
    if (isMockMode) {
      const syncMockUser = async () => {
        setLoading(true);
        const storedUser = localStorage.getItem("mock_auth_user");
        if (storedUser) {
          try {
            const parsed = JSON.parse(storedUser);
            setFirebaseUser(parsed);
            const res = await apiClient.get("auth/me");
            setUser(res.data);
          } catch (e) {
            console.warn("Could not retrieve mock backend user profile:", e);
            setUser(null);
            setFirebaseUser(null);
          }
        } else {
          setFirebaseUser(null);
          setUser(null);
        }
        setLoading(false);
      };
      syncMockUser();
      return;
    }

    const unsubscribe = onIdTokenChanged(auth, async (fbUser) => {
      setLoading(true);
      if (fbUser) {
        setFirebaseUser(fbUser);
        try {
          const res = await apiClient.get("auth/me");
          setUser(res.data);
        } catch (e) {
          console.warn("Could not retrieve backend user profile, syncing might be pending...", e);
          setUser(null);
        }
      } else {
        setFirebaseUser(null);
        setUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, [isMockMode]);

  // ─── Mock helpers ────────────────────────────────────────────────────────────
  const executeMockLogin = async (email) => {
    const uid = email.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_");
    const mockFbUser = { uid, email, displayName: uid.toUpperCase(), emailVerified: true };
    const mockToken = `mock-token-${uid}`;
    localStorage.setItem("mock_auth_user", JSON.stringify(mockFbUser));
    localStorage.setItem("mock_auth_token", mockToken);
    setFirebaseUser(mockFbUser);
    const res = await apiClient.get("auth/me");
    setUser(res.data);
    setLoading(false);
    return mockFbUser;
  };

  const executeMockRegister = async (email, role, businessName) => {
    const uid = email.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_");
    const mockFbUser = { uid, email, displayName: uid.toUpperCase(), emailVerified: true };
    const mockToken = `mock-token-${uid}`;
    localStorage.setItem("mock_auth_user", JSON.stringify(mockFbUser));
    localStorage.setItem("mock_auth_token", mockToken);
    setFirebaseUser(mockFbUser);
    await apiClient.post(
      "auth/sync",
      { role, business_name: role === "RETAILER" ? businessName : undefined },
      { headers: { Authorization: `Bearer ${mockToken}` } }
    );
    const res = await apiClient.get("auth/me");
    setUser(res.data);
    setLoading(false);
    return mockFbUser;
  };

  // ─── Login ───────────────────────────────────────────────────────────────────
  const login = async (email, password) => {
    setError(null);
    setLoading(true);
    if (isMockMode) {
      try { return await executeMockLogin(email); }
      catch (e) {
        setLoading(false);
        const msg = e.response?.data?.detail || e.message || "Failed local mock login";
        setError(msg); throw new Error(msg);
      }
    }
    try {
      const credential = await signInWithEmailAndPassword(auth, email, password);
      const res = await apiClient.get("auth/me");
      setUser(res.data);
      setLoading(false);
      return credential.user;
    } catch (e) {
      const isNetworkError =
        e.message?.includes("network-request-failed") ||
        e.message?.includes("DISCONNECTED") ||
        e.message?.includes("internet");
      if (isNetworkError) {
        console.warn("Firebase Auth network error. Falling back to local mock authentication.");
        try { return await executeMockLogin(email); }
        catch (mockErr) { setLoading(false); setError(mockErr.message); throw mockErr; }
      }
      setLoading(false);
      const msg = e.response?.data?.detail || e.message || "Failed to log in";
      setError(msg); throw new Error(msg);
    }
  };

  // ─── Register ────────────────────────────────────────────────────────────────
  const register = async (email, password, role, businessName) => {
    setError(null);
    setLoading(true);

    const ADMIN_EMAIL = "karthikhr676@gmail.com";
    if (email.trim().toLowerCase() === ADMIN_EMAIL.toLowerCase()) {
      const msg = "This email address is reserved and cannot be used for registration.";
      setError(msg); setLoading(false); throw new Error(msg);
    }

    if (isMockMode) {
      try { return await executeMockRegister(email, role, businessName); }
      catch (e) {
        setLoading(false);
        const msg = e.response?.data?.detail || e.message || "Failed local mock registration";
        setError(msg); throw new Error(msg);
      }
    }

    try {
      const credential = await createUserWithEmailAndPassword(auth, email, password);
      const fbUser = credential.user;

      // Send verification email immediately (no continueUrl — avoids unauthorized-continue-uri on localhost)
      await sendEmailVerification(fbUser);

      const token = await fbUser.getIdToken();
      await apiClient.post(
        "auth/sync",
        { role, business_name: role === "RETAILER" ? businessName : undefined },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const res = await apiClient.get("auth/me");
      setUser(res.data);
      setLoading(false);
      return fbUser;
    } catch (e) {
      const isNetworkError =
        e.message?.includes("network-request-failed") ||
        e.message?.includes("DISCONNECTED") ||
        e.message?.includes("internet");
      if (isNetworkError) {
        console.warn("Firebase Auth network error. Falling back to local mock registration.");
        try { return await executeMockRegister(email, role, businessName); }
        catch (mockErr) { setLoading(false); setError(mockErr.message); throw mockErr; }
      }
      setLoading(false);
      const msg = e.response?.data?.detail || e.message || "Failed to register account";
      setError(msg); throw new Error(msg);
    }
  };

  // ─── Email verification helpers ──────────────────────────────────────────────
  const resendVerificationEmail = async () => {
    if (isMockMode || !auth.currentUser) return;
    try {
      await sendEmailVerification(auth.currentUser);
    } catch (e) {
      throw new Error(e.message || "Failed to resend verification email.");
    }
  };

  const reloadFirebaseUser = async () => {
    if (isMockMode || !auth.currentUser) return;
    try {
      await reload(auth.currentUser);
      // Spread to trigger re-render
      setFirebaseUser({ ...auth.currentUser });
    } catch (e) {
      console.warn("Failed to reload Firebase user:", e);
    }
  };

  // ─── Password reset ───────────────────────────────────────────────────────────
  const forgotPassword = async (email) => {
    if (isMockMode) return; // In mock mode, pretend success
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (e) {
      throw new Error(e.message || "Failed to send password reset email.");
    }
  };

  // ─── Logout ───────────────────────────────────────────────────────────────────
  const logout = async () => {
    setError(null);
    setLoading(true);
    if (isMockMode || localStorage.getItem("mock_auth_token")) {
      localStorage.removeItem("mock_auth_user");
      localStorage.removeItem("mock_auth_token");
      setUser(null); setFirebaseUser(null); setLoading(false);
      return;
    }
    try {
      await signOut(auth);
      setUser(null); setFirebaseUser(null); setLoading(false);
    } catch (e) {
      setLoading(false); setError(e.message); throw e;
    }
  };

  const isEmailVerified = isMockMode ? true : (firebaseUser?.emailVerified ?? false);

  return (
    <AuthContext.Provider
      value={{
        user,
        firebaseUser,
        loading,
        error,
        login,
        register,
        logout,
        forgotPassword,
        resendVerificationEmail,
        reloadFirebaseUser,
        isAuthenticated: !!user,
        isEmailVerified,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};
