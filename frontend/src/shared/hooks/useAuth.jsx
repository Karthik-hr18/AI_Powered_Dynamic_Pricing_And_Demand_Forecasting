import React, { createContext, useContext, useEffect, useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  sendEmailVerification,
  sendPasswordResetEmail,
  onAuthStateChanged,
} from "firebase/auth";
import axios from "axios";

import { auth, googleProvider } from "../firebase/config";

const AuthContext = createContext(null);

// Global temporary cache to store custom attributes during registration sync
let pendingRegistrationData = null;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // Firebase User object
  const [mongoUser, setMongoUser] = useState(null); // MongoDB User Profile DTO
  const [idToken, setIdToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  // Setup API Client using base URL from environment
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  const apiClient = axios.create({ baseURL: apiBaseUrl });

  useEffect(() => {
    // Listen for Firebase auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setLoading(true);
      setAuthError(null);

      if (firebaseUser) {
        try {
          // 1. Retrieve current Firebase JWT ID Token
          const token = await firebaseUser.getIdToken(true);
          
          // 2. Resolve synchronization payload attributes
          const syncPayload = pendingRegistrationData || {
            role: "RETAILER",
            businessName: null,
          };
          pendingRegistrationData = null; // Clear registration cache

          // 3. Post verification sync to backend FastAPI server
          const response = await apiClient.post(
            "/api/v1/auth/sync",
            {
              role: syncPayload.role,
              business_name: syncPayload.businessName,
            },
            {
              headers: { Authorization: `Bearer ${token}` },
            }
          );

          setUser(firebaseUser);
          setIdToken(token);
          setMongoUser(response.data);
        } catch (err) {
          console.error("Authentication sync failed:", err);
          setAuthError(err.response?.data?.detail || "Failed to synchronize profile.");
          // Reset states to fail-closed
          setUser(null);
          setIdToken(null);
          setMongoUser(null);
        }
      } else {
        setUser(null);
        setIdToken(null);
        setMongoUser(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  /** Register user using email/password and sync custom profile attributes. */
  const registerWithEmail = async (email, password, role, businessName) => {
    setLoading(true);
    setAuthError(null);
    try {
      // Store registration variables for the onAuthStateChanged sync callback
      pendingRegistrationData = { role, businessName };

      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // Trigger email verification natively via Firebase Auth
      await sendEmailVerification(userCredential.user);
      return userCredential.user;
    } catch (err) {
      pendingRegistrationData = null;
      setAuthError(err.message);
      setLoading(false);
      throw err;
    }
  };

  /** Login user using email/password. */
  const loginWithEmail = async (email, password) => {
    setLoading(true);
    setAuthError(null);
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return userCredential.user;
    } catch (err) {
      setAuthError(err.message);
      setLoading(false);
      throw err;
    }
  };

  /** Google OAuth Popup sign-in. */
  const loginWithGoogle = async () => {
    setLoading(true);
    setAuthError(null);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      return result.user;
    } catch (err) {
      setAuthError(err.message);
      setLoading(false);
      throw err;
    }
  };

  /** Signs out the active user. */
  const logout = async () => {
    setLoading(true);
    try {
      await signOut(auth);
    } catch (err) {
      setAuthError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /** Sends a password reset verification link. */
  const resetPassword = async (email) => {
    setAuthError(null);
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (err) {
      setAuthError(err.message);
      throw err;
    }
  };

  const contextValue = {
    user,
    mongoUser,
    idToken,
    loading,
    authError,
    registerWithEmail,
    loginWithEmail,
    loginWithGoogle,
    logout,
    resetPassword,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be consumed inside an AuthProvider.");
  }
  return context;
};
