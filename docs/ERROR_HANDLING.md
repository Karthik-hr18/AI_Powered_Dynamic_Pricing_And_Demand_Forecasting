# Production-Grade Error Handling & Taxonomy Matrix

**Platform**: AI-Powered Dynamic Pricing & Demand Forecasting Platform  
**Document**: Centralized Error Handling, User Feedback, & Logging Matrix  
**Version**: 1.0.0 (Production Release)  

---

## 🏛️ Architecture Overview

The error handling architecture is built on five core principles:

1. **Strict Information Shielding**: Internal stack traces, database collection names, MongoDB exceptions, Axios internals, and file system paths are **never** exposed in user-facing UI or API response bodies.
2. **Standardized Error Envelopes**: All backend HTTP error responses follow a uniform structure:
   ```json
   {
     "success": false,
     "error": {
       "code": "CSV_VALIDATION_ERROR",
       "message": "The CSV file contains invalid data.",
       "details": ["Missing required columns: date, sku."],
       "reference_id": "ERR-8F32A"
     },
     "detail": "The CSV file contains invalid data."
   }
   ```
3. **Correlation & Forensics**: Unexpected 500 server errors generate a unique `reference_id` (e.g. `ERR-9B71X`), logged server-side alongside the full traceback for engineering diagnostics.
4. **Unified SaaS Notification & Toast System**: JavaScript `alert()` popups are strictly eliminated and replaced by an accessible, responsive Toast notification system.
5. **State Disambiguation**: Clear visual separation between **Loading**, **Empty**, **Processing**, and **Error** states across all views.

---

## 📋 Comprehensive Error Taxonomy Matrix

| Error Code | HTTP Status | User Message | Frontend Behavior | Backend Log Level | Safe to Retry? |
|---|---|---|---|---|---|
| **`AUTHENTICATION_ERROR`** | `401` | *"Your session has expired or is invalid. Please sign in again."* | Inline form error / Redirect to `/login` | `INFO` / `WARNING` | No (requires re-login) |
| **`AUTHORIZATION_ERROR`** | `403` | *"You don't have permission to perform this action."* | Warning toast / Action disabled | `WARNING` | No |
| **`RESOURCE_NOT_FOUND`** | `404` | *"The requested information could not be found."* | Error card with `[Back]` or `[Retry]` | `INFO` | Yes (if transient) |
| **`CONFLICT`** | `409` | *"This record already exists in the system."* | Inline field error or toast | `WARNING` | No |
| **`VALIDATION_ERROR`** | `422` | *"Some of the provided information is invalid. Please review and try again."* | Inline field error highlights | `WARNING` | No (requires edit) |
| **`RATE_LIMITED`** | `429` | *"You're making requests too quickly. Please wait a moment and try again."* | Warning toast with cooldown timer | `WARNING` | Yes (after cooldown) |
| **`UPLOAD_ERROR`** | `400` | *"We couldn't process this file. Please verify the format and try again."* | Upload error toast / dropzone reset | `WARNING` | Yes |
| **`CSV_VALIDATION_ERROR`** | `400` / `422` | *"The CSV file is missing required columns or contains invalid records."* | Upload error card with validation list | `WARNING` | Yes (with corrected file) |
| **`PROCESSING_ERROR`** | `500` | *"We couldn't complete the analysis. Your existing data has not been affected."* | Status badge `FAILED` + `[Try Again]` | `ERROR` | Yes |
| **`ML_PROCESSING_ERROR`** | `500` | *"Unable to generate forecast predictions for this dataset."* | Falls back to `FALLBACK_FLOOR` tier | `ERROR` | Yes |
| **`REPORT_GENERATION_ERROR`** | `500` | *"Unable to generate the PDF report. Please try again."* | Error toast with `[Try Again]` button | `ERROR` | Yes |
| **`DATABASE_ERROR`** | `500` | *"We couldn't complete your request. Please try again."* | Error card / Toast with reference ID | `CRITICAL` | Yes (transient) |
| **`SERVICE_UNAVAILABLE`** | `503` | *"The service is temporarily unavailable. Please try again shortly."* | Full-page service notice with retry | `WARNING` / `ERROR` | Yes |
| **`UNKNOWN_ERROR`** | `500` | *"We couldn't complete your request. Reference ID: ERR-XXXXX"* | Global error boundary / Toast with Ref ID | `ERROR` (with traceback) | Yes |
| **`NETWORK_ERROR`** | Client Offline | *"We couldn't connect to the server. Please check your internet connection."* | Offline banner / Retry action | N/A (Client-Side) | Yes |

---

## 🎨 User Feedback & State Guidelines

### 1. Upload Processing Lifecycle
- **`UPLOADING`**: *"Uploading your sales data..."* (Progress bar with live byte transfer)
- **`VALIDATING`**: *"Checking your sales data headers..."* (Pulsing badge)
- **`PROCESSING`**: *"Analyzing sales data and optimizing prices..."* (Active spinner)
- **`COMPLETED`**: *"Sales data processed successfully."* (Green check badge)
- **`FAILED`**: *"We couldn't process this dataset."* (Red badge with `[Try Again]` action)

### 2. State Triad Disambiguation
- **Loading State**: Render pulse skeleton cards (`.skeleton-card`).
- **Empty State**: Render descriptive empty message (*"No sales data available yet. Upload a CSV to get started."*).
- **Error State**: Render accessible error recovery card with `[Retry]` action.

---

## 🔒 Security & Privacy Rules
1. Never log customer PII, plain-text passwords, or unhashed secrets.
2. Never return file system paths (`/app/storage/...` or `C:\Users\...`) in error details.
3. Keep developer forensics in server logs keyed by `reference_id`.
