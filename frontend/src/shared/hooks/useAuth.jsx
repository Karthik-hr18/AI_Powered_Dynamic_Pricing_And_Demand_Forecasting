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

  // Sync Firebase status with local backend metadata
  useEffect(() => {
    const unsubscribe = onIdTokenChanged(auth, async (fbUser) => {
      setLoading(true);
      setError(null);
      
      if (fbUser) {
        setFirebaseUser(fbUser);
        try {
          // Fetch synced metadata from MongoDB backend
          const res = await apiClient.get("/auth/me");
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
  }, []);

  // Login handler
  const login = async (email, password) => {
    setError(null);
    setLoading(true);
    try {
      const credential = await signInWithEmailAndPassword(auth, email, password);
      // Retrieve backend user profile immediately after sign in
      const res = await apiClient.get("/auth/me");
      setUser(res.data);
      setLoading(false);
      return credential.user;
    } catch (e) {
      setLoading(false);
      const msg = e.response?.data?.detail || e.message || "Failed to log in";
      setError(msg);
      throw new Error(msg);
    }
  };

  // Register handler (Firebase Auth + Backend Mongo Sync)
  const register = async (email, password, role, businessName) => {
    setError(null);
    setLoading(true);
    try {
      // 1. Create user in Firebase Auth
      const credential = await createUserWithEmailAndPassword(auth, email, password);
      const fbUser = credential.user;

      // 2. Retrieve the fresh token to make the sync request
      const token = await fbUser.getIdToken();

      // 3. Post profile sync payload to FastAPI database
      await apiClient.post(
        "/auth/sync",
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
      const res = await apiClient.get("/auth/me");
      setUser(res.data);
      setLoading(false);
      return fbUser;
    } catch (e) {
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
