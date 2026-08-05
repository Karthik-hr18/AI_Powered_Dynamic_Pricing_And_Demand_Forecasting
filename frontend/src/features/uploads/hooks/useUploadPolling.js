import { useState, useEffect, useRef } from "react";
import { apiClient } from "../../../shared/apiClient";

export const useUploadPolling = (onComplete) => {
  const [activeUpload, setActiveUpload] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const pollIntervalRef = useRef(null);

  const stopPolling = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setIsPolling(false);
  };

  const pollStatus = async (uploadId) => {
    try {
      const res = await apiClient.get(`uploads/${uploadId}`);
      const upload = res.data;
      setActiveUpload(upload);

      if (onComplete) {
        onComplete(upload);
      }

      // Check if job completed or failed
      const terminalStatuses = ["COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED", "REJECTED"];
      if (terminalStatuses.includes(upload.status)) {
        stopPolling();
      }
    } catch (e) {
      console.error("Error polling upload status:", e);
      stopPolling();
    }
  };

  const startPolling = (uploadId) => {
    stopPolling();
    setIsPolling(true);
    // Poll immediately, then set interval
    pollStatus(uploadId);
    pollIntervalRef.current = setInterval(() => {
      pollStatus(uploadId);
    }, 2000);
  };

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  return {
    activeUpload,
    setActiveUpload,
    isPolling,
    startPolling,
    stopPolling,
  };
};

export default useUploadPolling;
