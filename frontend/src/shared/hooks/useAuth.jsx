import React, { createContext, useContext, useEffect, useState } from "react";
import {
  createUserWithEmailAndPassword,
  onIdTokenChanged,
  signInWithEmailAndPassword,
  signOut,
} from "firebase/auth";

import { auth } from "../firebase/config";
import { apiClient } from "../apiClient";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Backend user metadata (role, business_name, is_active)
  const [firebaseUser, setFirebaseUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if mock mode is required based on placeholder configuration
  const isMockMode =
    !import.meta.env.VITE_FIREBASE_API_KEY ||
    import.meta.env.VITE_FIREBASE_API_KEY.includes("placeholder");

  // Sync Firebase status with local backend metadata
  useEffect(() => {
    if (isMockMode) {
      const syncMockUser = async () => {
        setLoading(true);
        setError(null);
        const storedUser = localStorage.getItem("mock_auth_user");
        if (storedUser) {
          try {
            const parsed = JSON.parse(storedUser);
            setFirebaseUser(parsed);
            // Fetch synced metadata from MongoDB backend using the local mock token
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
      setError(null);
      
      if (fbUser) {
        setFirebaseUser(fbUser);
        try {
          // Fetch synced metadata from MongoDB backend
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

  // Login handler helper for local mock mode
  const executeMockLogin = async (email) => {
    const uid = email.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_");
    const mockFbUser = {
      uid,
      email,
      displayName: uid.replace("_", " ").toUpperCase(),
    };
    const mockToken = `mock-token-${uid}`;
    
    localStorage.setItem("mock_auth_user", JSON.stringify(mockFbUser));
    localStorage.setItem("mock_auth_token", mockToken);
    setFirebaseUser(mockFbUser);

    const res = await apiClient.get("auth/me");
    setUser(res.data);
    setLoading(false);
    return mockFbUser;
  };

  // Login handler
  const login = async (email, password) => {
    setError(null);
    setLoading(true);

    if (isMockMode) {
      try {
        return await executeMockLogin(email);
      } catch (e) {
        setLoading(false);
        const msg = e.response?.data?.detail || e.message || "Failed local mock login";
        setError(msg);
        throw new Error(msg);
      }
    }

    try {
      const credential = await signInWithEmailAndPassword(auth, email, password);
      // Retrieve backend user profile immediately after sign in
      const res = await apiClient.get("auth/me");
      setUser(res.data);
      setLoading(false);
      return credential.user;
    } catch (e) {
      // Auto-fallback to local mock login if internet/Firebase server is unavailable
      const isNetworkError =
        e.message?.includes("network-request-failed") ||
        e.message?.includes("DISCONNECTED") ||
        e.message?.includes("internet");
      
      if (isNetworkError) {
        console.warn("Firebase Auth network error. Falling back to local mock authentication.");
        try {
          return await executeMockLogin(email);
        } catch (mockErr) {
          setLoading(false);
          setError(mockErr.message);
          throw mockErr;
        }
      }

      setLoading(false);
      const msg = e.response?.data?.detail || e.message || "Failed to log in";
      setError(msg);
      throw new Error(msg);
    }
  };

  // Register handler helper for local mock mode
  const executeMockRegister = async (email, role, businessName) => {
    const uid = email.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_");
    const mockFbUser = {
      uid,
      email,
      displayName: uid.replace("_", " ").toUpperCase(),
    };
    const mockToken = `mock-token-${uid}`;

    localStorage.setItem("mock_auth_user", JSON.stringify(mockFbUser));
    localStorage.setItem("mock_auth_token", mockToken);
    setFirebaseUser(mockFbUser);

    // Post profile sync payload to FastAPI database
    await apiClient.post(
      "auth/sync",
      {
        role: role,
        business_name: role === "RETAILER" ? businessName : undefined,
      },
      {
        headers: {
          Authorization: `Bearer ${mockToken}`,
        },
      }
    );

    // Load final profile data
    const res = await apiClient.get("auth/me");
    setUser(res.data);
    setLoading(false);
    return mockFbUser;
  };

  // Register handler (Firebase Auth + Backend Mongo Sync)
  const register = async (email, password, role, businessName) => {
    setError(null);
    setLoading(true);

    if (isMockMode) {
      try {
        return await executeMockRegister(email, role, businessName);
      } catch (e) {
        setLoading(false);
        const msg = e.response?.data?.detail || e.message || "Failed local mock registration";
        setError(msg);
        throw new Error(msg);
      }
    }

    try {
      // 1. Create user in Firebase Auth
      const credential = await createUserWithEmailAndPassword(auth, email, password);
      const fbUser = credential.user;

      // 2. Retrieve the fresh token to make the sync request
      const token = await fbUser.getIdToken();

      // 3. Post profile sync payload to FastAPI database
      await apiClient.post(
        "auth/sync",
        {
          role: role,
          business_name: role === "RETAILER" ? businessName : undefined,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // 4. Load final profile data
      const res = await apiClient.get("auth/me");
      setUser(res.data);
      setLoading(false);
      return fbUser;
    } catch (e) {
      // Auto-fallback to local mock register if internet/Firebase server is unavailable
      const isNetworkError =
        e.message?.includes("network-request-failed") ||
        e.message?.includes("DISCONNECTED") ||
        e.message?.includes("internet");
      
      if (isNetworkError) {
        console.warn("Firebase Auth network error. Falling back to local mock registration.");
        try {
          return await executeMockRegister(email, role, businessName);
        } catch (mockErr) {
          setLoading(false);
          setError(mockErr.message);
          throw mockErr;
        }
      }

      setLoading(false);
      const msg = e.response?.data?.detail || e.message || "Failed to register account";
      setError(msg);
      throw new Error(msg);
    }
  };

  // Logout handler
  const logout = async () => {
    setError(null);
    setLoading(true);
    
    if (isMockMode || localStorage.getItem("mock_auth_token")) {
      localStorage.removeItem("mock_auth_user");
      localStorage.removeItem("mock_auth_token");
      setUser(null);
      setFirebaseUser(null);
      setLoading(false);
      return;
    }

    try {
      await signOut(auth);
      setUser(null);
      setFirebaseUser(null);
      setLoading(false);
    } catch (e) {
      setLoading(false);
      setError(e.message);
      throw e;
    }
  };

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
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
