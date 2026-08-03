import axios from "axios";
import { auth } from "../firebase/config";

// Setup base client with environment-aware endpoints
export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to dynamically inject the active Firebase ID token
apiClient.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      try {
        // Retrieve fresh token (Firebase automatically handles rotation internally)
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch (e) {
        console.error("Failed to retrieve Firebase ID token", e);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle authorization lapses globally
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response) {
      const { status, data } = error.response;
      
      // Auto logout if account gets deactivated backend-side
      const isDeactivated = data && typeof data.detail === "string" && data.detail.toLowerCase().includes("deactivated");
      if ((status === 401 || status === 403) && isDeactivated) {
        console.warn("User account deactivated. Revoking local session.");
        await auth.signOut();
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
