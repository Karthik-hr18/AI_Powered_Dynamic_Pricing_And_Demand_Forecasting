/**
 * Centralized User-Friendly Error Formatting & Taxonomy Parser.
 *
 * Translates HTTP status codes, Axios errors, backend error envelopes,
 * and Firebase authentication codes into clean, non-technical, actionable messages.
 */

// HTTP Status Code to Plain-English Retailer Messages
const HTTP_ERROR_MESSAGES = {
  400: "The request contains invalid information. Please check the inputs and try again.",
  401: "Your session has expired or is invalid. Please sign in again.",
  403: "You don't have permission to perform this action.",
  404: "We couldn't find the requested information.",
  409: "This information already exists in the system.",
  422: "Some information provided is invalid. Please review and try again.",
  429: "You're making requests too quickly. Please wait a moment and try again.",
  500: "We couldn't complete that request right now. Please try again.",
  502: "The server is currently unavailable. Please try again shortly.",
  503: "The service is temporarily under maintenance. Please try again shortly.",
  504: "The server took too long to respond. Please try again.",
};

// Backend Error Codes to Plain-English Messages
const ERROR_CODE_MESSAGES = {
  AUTHENTICATION_ERROR: "Please sign in to access this feature.",
  AUTHORIZATION_ERROR: "You don't have permission to perform this action.",
  VALIDATION_ERROR: "Please review the form fields and correct any invalid values.",
  RESOURCE_NOT_FOUND: "The requested record was not found.",
  CONFLICT: "A conflicting record already exists.",
  RATE_LIMITED: "Too many requests. Please wait a moment before trying again.",
  UPLOAD_ERROR: "We couldn't process this file. Please verify the format and try again.",
  CSV_VALIDATION_ERROR: "The CSV file is missing required columns or contains invalid records.",
  PROCESSING_ERROR: "We couldn't complete the analysis. Your existing data is safe.",
  ML_PROCESSING_ERROR: "Unable to generate forecast predictions for this dataset.",
  REPORT_GENERATION_ERROR: "Unable to generate the PDF report. Please try again.",
  DATABASE_ERROR: "A database error occurred. Please try again.",
  SERVICE_UNAVAILABLE: "The service is temporarily unavailable. Please try again.",
  UNKNOWN_ERROR: "An unexpected problem occurred. Please try again.",
};

// Firebase Error Codes to Plain-English Messages
const FIREBASE_AUTH_MESSAGES = {
  "auth/invalid-credential": "Email or password is incorrect. Please try again.",
  "auth/wrong-password": "Email or password is incorrect. Please try again.",
  "auth/user-not-found": "No account found with this email address.",
  "auth/email-already-in-use": "An account with this email address already exists.",
  "auth/weak-password": "Password must be at least 6 characters.",
  "auth/invalid-email": "Please enter a valid email address.",
  "auth/user-disabled": "This account has been disabled. Please contact support.",
  "auth/too-many-requests": "Too many failed attempts. Please wait a moment and try again.",
  "auth/network-request-failed": "Network error. Please check your internet connection.",
  "auth/popup-closed-by-user": "Sign in popup was closed before completing.",
  "auth/requires-recent-login": "Please sign in again to complete this sensitive action.",
};

/**
 * Extracts a safe, user-friendly error message from any error object.
 * Guaranteed never to expose stack traces, database strings, or internal paths.
 */
export const getErrorMessage = (error, fallback = "An unexpected error occurred. Please try again.") => {
  if (!error) return fallback;

  // 1. Network connectivity / offline failure
  if (
    error.code === "ERR_NETWORK" ||
    error.message === "Network Error" ||
    error.name === "AxiosError" && !error.response
  ) {
    return "We couldn't connect to the server. Please check your internet connection.";
  }

  // 2. Firebase authentication error codes
  if (typeof error.code === "string" && error.code.startsWith("auth/")) {
    return FIREBASE_AUTH_MESSAGES[error.code] || "Authentication failed. Please try again.";
  }

  // 3. Backend standardized error envelope { error: { message, code } }
  const respData = error.response?.data;
  if (respData) {
    // Check for standardized backend code
    if (respData.error?.message && typeof respData.error.message === "string") {
      return sanitizeString(respData.error.message);
    }
    
    // Check for standard detail string
    if (typeof respData.detail === "string") {
      return sanitizeString(respData.detail);
    }
    
    // Check for detail array/object (e.g. FastAPI validation list)
    if (Array.isArray(respData.detail) && respData.detail.length > 0) {
      const first = respData.detail[0];
      if (typeof first === "string") return sanitizeString(first);
      if (first.msg) return sanitizeString(first.msg);
    }

    if (respData.error?.code && ERROR_CODE_MESSAGES[respData.error.code]) {
      return ERROR_CODE_MESSAGES[respData.error.code];
    }
  }

  // 4. HTTP Status Code fallback
  const status = error.response?.status;
  if (status && HTTP_ERROR_MESSAGES[status]) {
    return HTTP_ERROR_MESSAGES[status];
  }

  // 5. Error message string if clean
  if (typeof error.message === "string" && error.message.trim().length > 0) {
    return sanitizeString(error.message);
  }

  return fallback;
};

/**
 * Strips technical exception jargon, file paths, and database names.
 */
const sanitizeString = (text) => {
  if (!text) return "";
  const lower = text.toLowerCase();

  if (
    lower.includes("traceback") ||
    lower.includes("mongoservererror") ||
    lower.includes("e11000") ||
    lower.includes("pydantic") ||
    lower.includes("fastapi") ||
    lower.includes("axioserror") ||
    lower.includes("syntaxerror") ||
    lower.includes("operationalerror")
  ) {
    return "We couldn't complete your request. Please try again.";
  }

  // Remove technical prefixes like "Error: ", "ValueError: "
  return text.replace(/^[a-zA-Z]+Error:\s*/i, "").trim();
};
