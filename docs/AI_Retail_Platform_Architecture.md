# AI-Powered Dynamic Pricing & Demand Forecasting Platform
## Complete Architecture Document — Phase 1 + Phase 2

**Project:** Major Project, BIT, Dept. of CS&E, 2025–2026  
**Stack:** FastAPI · React + Vite · MongoDB · Prophet · XGBoost · scikit-learn  
**Status:** Phase 2 (System Design) Frozen — Implementation Ready  
**Document:** Canonical architecture reference — do not modify without explicit scope decision

---

## Table of Contents

1. [Product Vision & Principles (Phase 1)](#1-product-vision--principles-phase-1)
2. [Database Schema Design](#2-database-schema-design)
3. [MongoDB Collections — Full Specification](#3-mongodb-collections--full-specification)
4. [Master Indexing Strategy](#4-master-indexing-strategy)
5. [API Design](#5-api-design)
6. [Backend Folder Structure](#6-backend-folder-structure)
7. [Frontend Folder Structure](#7-frontend-folder-structure)
8. [ML Folder Structure](#8-ml-folder-structure)
9. [Complete System Architecture](#9-complete-system-architecture)
10. [Authentication Flow](#10-authentication-flow)
11. [Request Flow](#11-request-flow)
12. [File Upload Flow](#12-file-upload-flow)
13. [ML Pipeline Flow](#13-ml-pipeline-flow)
14. [Deployment Architecture](#14-deployment-architecture)
15. [Testing Strategy](#15-testing-strategy)
16. [Logging & Monitoring](#16-logging--monitoring)
17. [Scalability](#17-scalability)

---

## 1. Product Vision & Principles (Phase 1)

### Problem Statement
SME retailers face difficulty accurately forecasting product demand and setting optimal prices due to reliance on manual methods, static pricing rules, and intuition-based decision-making. Existing enterprise-grade tools (SAP, Oracle, IBM) are too costly and complex for SME deployment.

### Product Goal
A web-based, AI-driven retail analytics platform giving SME retailers demand forecasts, data-driven pricing recommendations, and inventory risk visibility through a single non-technical-friendly dashboard — transparent about the limits of what the underlying data can support.

### Seven Binding Design Principles

| Principle | What It Means in Practice |
|---|---|
| Evidence-Based Decision Support | Never produce a recommendation not backed by sufficient data; say so explicitly rather than guessing |
| Graceful Degradation Under Data Sparsity | Every ML feature has a defined fallback or explicit 'insufficient data' state |
| Separation of Forecasting and Pricing Pipelines | Independent modeling responsibilities composed by a separate optimization layer |
| Bounded Optimization for Pricing | Price recommendations restricted to ±15% of current price, constrained to historical range |
| Transparent Communication of Model Limitations | UI never silently omits low-confidence results — labels fallbacks, flags insufficient data |
| Production-Aware MVP Architecture | Every component built so future expansion is additive, not a rewrite |
| Business-Oriented, Not Model-Oriented UX | Dashboard answers 'what should the retailer do today,' not 'here is what the model predicted' |

### ML Architecture (Locked)
- **Forecasting:** Three-tier adaptive (Prophet+XGBoost for ≥30 days, moving average fallback, explicit exclusion below minimum floor)
- **Pricing:** Two-pipeline separation — demand forecasting and price-elasticity regression composed by an optimization layer; bounded ±15%; revenue maximization only for MVP
- **Anomaly Detection:** Two-stage Isolation Forest — pre-forecast flagging + post-upload alerting; no auto-exclusion
- **Inventory Risk:** True risk (days of cover) when inventory_level present; soft advisory otherwise

---

## 2. Database Schema Design

### Cross-Cutting Decisions

| Decision | Choice Locked | Rationale |
|---|---|---|
| Multi-tenancy | Shared collections + `retailer_id` on every tenant-scoped document, enforced via MongoDB schema validation + middleware | Structural defect prevention, not discipline |
| Sales data modeling | Hybrid: `raw_sales` (immutable, one doc per uploaded record) + `processed_sales` (cleaned, feature-engineered) | Clean separation of source data and analytical data |
| Forecast/pricing retention | Hybrid current/history: `_current` overwritten per run (dashboard reads); `_history` append-only (audit/traceability) | Operational reads vs historical traceability |
| Pipeline output collections | Separate collections per pipeline (`forecast_current/_history`, `pricing_current/_history`, `inventory_current`, `anomaly_current`) | Consistent with separation-of-pipelines principle |
| Product creation | Implicit on upload (no Product Management UI) | Consistent with frozen PRD scope |
| Upload + job tracking | Single `uploads` collection (file metadata + job state) | One upload = one lifecycle |
| User accounts | Single `users` collection with `role` field (RETAILER/ADMIN) | Extensible RBAC without separate collections |
| Refresh tokens | Separate `refresh_tokens` collection with rotation + reuse-detection | Rotation + reuse-detection with family revocation |
| ID strategy | MongoDB `_id` (ObjectId) as universal PK; business IDs only where externally meaningful (`sku`, `upload_id`) | Fast internal joins + stable external handles |

### Standing Schema Principle
**States of "we don't know" must be structurally distinct from states of "we do know."**
Applied to: `forecast_current` (`INSUFFICIENT_DATA` → both horizons explicitly `null` + `eligibility_reason` required), `inventory_current` (mode-segregated nested objects — `true_risk` and `advisory` mutually exclusive), `anomaly_current` (flagging is purely additive, never triggers data exclusion).

---

## 3. MongoDB Collections — Full Specification

### 3.1 `users`

**Purpose:** Single source of truth for authentication and account identity (Retailers + Admins via RBAC).  
**Ownership:** Authentication / Master Data

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `_id` | ObjectId | auto | auto | Primary key |
| `email` | String | required | — | Unique, lowercase normalized |
| `password_hash` | String | required | — | Argon2 hash, never plaintext |
| `role` | String enum | required | `RETAILER` | `RETAILER` or `ADMIN` |
| `business_name` | String | required for RETAILER | — | Optional/null for ADMIN |
| `is_active` | Boolean | required | `true` | Admin can disable |
| `created_at` | Date | required | now | |
| `updated_at` | Date | required | now | |
| `last_login_at` | Date | optional | `null` | |

**Example:**
```json
{
  "_id": ObjectId("66ab1c2f3a9e1b2c3d4e5f60"),
  "email": "shree.kirana@example.com",
  "password_hash": "$argon2id$v=19$...",
  "role": "RETAILER",
  "business_name": "Shree Kirana Store",
  "is_active": true,
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-06-20T08:30:00Z",
  "last_login_at": "2026-06-29T18:42:11Z"
}
```

**Future:** Adding `retailers` collection for multi-employee accounts is additive — add `retailer_id` FK to `users`, no schema rewrite.

---

### 3.2 `refresh_tokens`

**Purpose:** Track issued refresh tokens for secure, revocable long-lived sessions with rotation + reuse-detection.  
**Ownership:** Authentication (transactional, high-churn, short-lived)

**Token Policy: Rotation + Reuse-Detection with Family Revocation**
Every refresh exchange issues a new token and invalidates the previous one (same `family_id`). If a superseded token is ever presented again → entire family revoked → forced re-login.

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `_id` | ObjectId | auto | auto | Primary key |
| `user_id` | ObjectId | required | — | References `users._id` |
| `token_hash` | String | required | — | SHA-256 hash of raw token; raw never stored |
| `family_id` | String (UUID) | required | new UUID on first issuance | Shared across rotation chain |
| `issued_at` | Date | required | now | |
| `expires_at` | Date | required | now + 7d | Configurable |
| `revoked` | Boolean | required | `false` | |
| `revoked_reason` | String enum | optional | `null` | `LOGOUT`, `ROTATED`, `REUSE_DETECTED`, `EXPIRED`, `ADMIN_DISABLE` |
| `replaced_by` | ObjectId | optional | `null` | Points to next token in chain |
| `created_ip` / `user_agent` | String | optional | `null` | Forensics |

**Future:** `device_label` field for "manage sessions" UI is additive.

---

### 3.3 `products`

**Purpose:** Master registry of retailer-owned products/SKUs, auto-populated from CSV ingestion.  
**Ownership:** Master Data

**Key rule:** Stable master metadata only. Forecast/pricing eligibility is derived analytical state owned by each pipeline — never stored as permanent product metadata.

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `_id` | ObjectId | auto | auto | Primary key, used as FK everywhere |
| `retailer_id` | ObjectId | required | — | References `users._id` |
| `sku` | String | required | — | Normalized (trimmed, case-folded) for matching |
| `sku_display` | String | required | — | Original as-uploaded casing, for UI |
| `product_name` | String | optional | falls back to `sku_display` at read time | |
| `category` | String | optional | `null` | Display aggregation only |
| `brand` | String | optional | `null` | |
| `is_active` | Boolean | required | `true` | |
| `first_seen_upload_id` | ObjectId | required | — | Provenance |
| `last_seen_upload_id` | ObjectId | required | — | Updated on re-appearance |
| `created_at` / `updated_at` | Date | required | now | |

**Implicit creation rule:** During CSV ingestion, normalize SKU → lookup by `(retailer_id, sku)` → reuse if found, auto-create if not. No Product Management UI (frozen PRD scope).

---

### 3.4 `uploads`

**Purpose:** Track each CSV upload as file/dataset record AND background processing job lifecycle.  
**Ownership:** Transactional (high-write during processing, read-heavy for polling)

**Status state machine:**
```
UPLOADED → VALIDATING → REJECTED (terminal, validation failed)
                      → PROCESSING → COMPLETED (terminal)
                                   → COMPLETED_WITH_WARNINGS (terminal)
                                   → FAILED (terminal)
```

**Two-tier model:** Coarse `status` enum (business-logic branching) + optional `current_stage` string (UI progress display, evolves without breaking API contract).

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `_id` | ObjectId | auto | auto | |
| `upload_id` | String | required | generated (e.g. `UPL-20260630-7f3a`) | Business ID for support/debug |
| `retailer_id` | ObjectId | required | — | |
| `original_filename` | String | required | — | |
| `file_size_bytes` | Number | required | — | Checked against FR-6 |
| `row_count` | Number | optional | `null` | Populated post-parse |
| `schema_mapping_used` | String | required | — | Config-driven mapping identifier |
| `status` | String enum | required | `UPLOADED` | See state machine above |
| `current_stage` | String | optional | `null` | Informational: `validating`, `preprocessing`, `forecasting`, etc. |
| `validation_errors` | Array<String> | optional | `[]` | Populated on REJECTED |
| `row_warnings` | Array<Object> | optional | `[]` | `[{row, reason}]` on COMPLETED_WITH_WARNINGS |
| `error_reason` | String | optional | `null` | Populated on FAILED |
| `rows_ingested` | Number | optional | `null` | |
| `rows_rejected` | Number | optional | `0` | |
| `processing_started_at` | Date | optional | `null` | |
| `processing_completed_at` | Date | optional | `null` | |
| `created_at` | Date | required | now | |

---

### 3.5 `raw_sales`

**Purpose:** Immutable, per-row record of every uploaded sales record as mapped from source CSV. Source of truth for auditing, validation debugging, and reprocessing.  
**Ownership:** Transactional (immutable, append-only, highest volume)

**Schema:** Hybrid — known Section 9.1 fields as typed top-level keys (uniform regardless of source dataset) + `source_row_raw` map preserving verbatim original CSV row (forensic/debugging only, never read by any pipeline).

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | auto | |
| `retailer_id` | ObjectId | required | |
| `upload_id` | ObjectId | required | References `uploads._id` |
| `product_id` | ObjectId | required | References `products._id` |
| `sku` | String | required | Denormalized for debugging without join |
| `date` | Date | required | |
| `quantity_sold` | Number | required | |
| `selling_price` | Number | optional | Required for pricing; forecasting alone can proceed without |
| `category` | String | optional | |
| `unit_cost` | Number | optional | Stored; unused in MVP pricing |
| `discount` | Number | optional | |
| `store_id` | String | optional | |
| `inventory_level` | Number | optional | |
| `promotion_flag` | Boolean | optional | |
| `holiday_flag` | Boolean | optional | Derived from date if absent |
| `row_number_in_file` | Number | required | For error messages |
| `source_row_raw` | Object | required | Verbatim original CSV row, untouched by mapping |
| `ingested_at` | Date | required | |

**Immutability rule:** Never updated post-insert. Corrections require a new upload, not an edit.

---

### 3.6 `processed_sales`

**Purpose:** Cleaned, deduplicated, daily-aggregated, feature-engineered sales records. Single input source for all ML pipelines and dashboard aggregation.  
**Ownership:** Analytical (derived, rebuildable from `raw_sales`)

**Key decision:** Single collection — cleaned data + engineered features together (no separate feature store for MVP).

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | auto | |
| `retailer_id` | ObjectId | required | |
| `product_id` | ObjectId | required | |
| `date` | Date | required | Daily granularity — one doc per (retailer, product, date) |
| `quantity_sold` | Number | required | Aggregated if source was transaction-level |
| `selling_price` | Number | optional | Avg/mode if multiple transactions same day |
| `unit_cost` | Number | optional | |
| `inventory_level` | Number | optional | |
| `promotion_flag` | Boolean | optional | |
| `holiday_flag` | Boolean | optional | |
| `day_of_week` | Number (0–6) | required | Engineered |
| `is_weekend` | Boolean | required | Engineered |
| `rolling_avg_7d` | Number | optional | `null` until 7 days history exist |
| `rolling_avg_30d` | Number | optional | `null` until 30 days history exist |
| `lag_1d_quantity` | Number | optional | `null` if no prior day |
| `price_change_flag` | Boolean | optional | True if price ≠ previous day |
| `source_upload_ids` | Array<ObjectId> | required | Supports overlapping uploads for same day |
| `feature_engineering_version` | String | required | e.g. `v1` — versioning for reprocessing traceability |
| `processed_at` | Date | required | |

**Mutability:** Unlike `raw_sales`, this IS mutable — reprocessing upserts (keyed on unique compound index) rather than appending.

---

### 3.7 `forecast_current`

**Purpose:** Latest forecast result per product, optimized for dashboard reads. Represents the three-tier eligibility model structurally.  
**Ownership:** Analytical (pipeline-owned, overwritten per run)

**Structure:** One document per product, both horizons nested inside (matches dashboard's per-product lookup pattern).

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | auto | |
| `retailer_id` | ObjectId | required | |
| `product_id` | ObjectId | required | |
| `pipeline_type` | String enum | required | `FULL`, `FALLBACK`, `INSUFFICIENT_DATA` |
| `eligibility_reason` | String | conditional | Required when `pipeline_type = INSUFFICIENT_DATA` |
| `history_days_available` | Number | required | |
| `horizon_7d` | Object or `null` | conditional | `null` if `INSUFFICIENT_DATA`; else `{predictions: [{date, predicted_quantity}], confidence}` |
| `horizon_30d` | Object or `null` | conditional | `null` if `INSUFFICIENT_DATA` or `FALLBACK` |
| `confidence_label` | String enum | required | `HIGH` (FULL), `LOW` (FALLBACK), `NONE` (INSUFFICIENT_DATA) |
| `model_version` | String | required | e.g. `prophet-xgb-v1` |
| `run_id` | ObjectId | required | References `forecast_history._id` |
| `upload_id` | ObjectId | required | |
| `run_timestamp` | Date | required | |

**Validation rule:** `INSUFFICIENT_DATA` requires both horizons `null` AND `eligibility_reason` non-empty — enforced structurally, not by convention.

---

### 3.8 `forecast_history`

**Purpose:** Immutable log of every forecasting run per product. Audit trail + future model evaluation (MAE/RMSE/MAPE).  
**Ownership:** Analytical (append-only)

Same shape as `forecast_current` plus:

| Additional Field | Type | Notes |
|---|---|---|
| `superseded_at` | Date | Set when a later run becomes `forecast_current` |
| `triggered_by` | String enum | `UPLOAD` or `SCHEDULED` |

---

### 3.9 `pricing_current`

**Purpose:** Latest pricing recommendation per product, including full evaluated candidate grid for explainability.  
**Ownership:** Analytical (pipeline-owned, overwritten per run)

**Key decision:** Full candidate set persisted (not just winning price) — directly supports Section 10.5's evaluation requirement and Section 3's transparency principle.

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | auto | |
| `retailer_id` | ObjectId | required | |
| `product_id` | ObjectId | required | |
| `eligibility_status` | String enum | required | `ELIGIBLE`, `INSUFFICIENT_HISTORY`, `INSUFFICIENT_PRICE_VARIATION` |
| `eligibility_reason` | String | conditional | Required when not `ELIGIBLE` |
| `current_price` | Number | required | Anchor for bounds |
| `bound_pct` | Number | required | `0.15` (configurable) |
| `bound_range` | Object or `null` | conditional | `{min, max}` — computed from ±bound_pct AND historical range |
| `candidate_grid` | Array<Object> or `null` | conditional | `null` if not ELIGIBLE; else `[{candidate_price, estimated_demand, estimated_revenue}]` |
| `recommended_price` | Number or `null` | conditional | argmax of `candidate_grid` by `estimated_revenue` |
| `expected_revenue` | Number or `null` | conditional | |
| `elasticity_model_type` | String | optional | e.g. `linear_regression` |
| `model_version` | String | required | |
| `run_id` | ObjectId | required | References `pricing_history._id` |
| `upload_id` | ObjectId | required | |
| `run_timestamp` | Date | required | |

**Pluggable objective:** `candidate_grid` already supports future profit optimization — add `estimated_profit` per entry and `objective_used` field without restructuring.

---

### 3.10 `pricing_history`

**Purpose:** Immutable log of every pricing run per product.  
**Ownership:** Analytical (append-only)

Same shape as `pricing_current` plus `superseded_at` and `triggered_by` (same pattern as `forecast_history`).

---

### 3.11 `inventory_current`

**Purpose:** Latest inventory risk assessment per product — true classification OR soft advisory (never both, never neither).  
**Ownership:** Analytical (current-only, no history sibling for MVP)

**Key decision:** Mode-segregated nested objects. `true_risk` and `advisory` are mutually exclusive, structurally distinct — not just flagged by a status enum.

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | auto | |
| `retailer_id` | ObjectId | required | |
| `product_id` | ObjectId | required | |
| `mode` | String enum | required | `TRUE_RISK` or `ADVISORY` |
| `true_risk` | Object or `null` | conditional | Populated only if `mode = TRUE_RISK`: `{days_of_cover, classification: STOCKOUT_RISK|OVERSTOCK_RISK|HEALTHY, current_inventory_level, horizon_used}` |
| `advisory` | Object or `null` | conditional | Populated only if `mode = ADVISORY`: `{demand_trend: RISING|FALLING|STABLE, message}` |
| `forecast_run_id` | ObjectId | required | References `forecast_history._id` |
| `upload_id` | ObjectId | required | |
| `run_timestamp` | Date | required | |

**Invariant:** Exactly one of `true_risk`/`advisory` non-null — enforced at service layer on write.

---

### 3.12 `anomaly_current`

**Purpose:** Currently-flagged anomalies per product, covering both detection stages. Flags only — never triggers exclusion (Section 8.4).  
**Ownership:** Analytical (current-only, no history sibling for MVP)

**Structure:** One document per product, anomalies as embedded array (consistent with other `_current` collections, naturally bounded array size since anomalies are rare by definition).

| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | auto | |
| `retailer_id` | ObjectId | required | |
| `product_id` | ObjectId | required | |
| `flagged_anomalies` | Array<Object> | required | See sub-schema below |
| `total_flagged_count` | Number | required | Denormalized for fast KPI/sort |
| `has_unreviewed_alerts` | Boolean | required | `false` | True if any POST_UPLOAD_ALERT unacknowledged |
| `model_version` | String | required | |
| `upload_id` | ObjectId | required | |
| `run_timestamp` | Date | required | |

**`flagged_anomalies[]` sub-schema:**

| Field | Type | Notes |
|---|---|---|
| `date` | Date | |
| `stage` | String enum | `PRE_FORECAST_HISTORICAL` or `POST_UPLOAD_ALERT` |
| `anomaly_type` | String | `SPIKE`, `DROP`, `UNUSUAL` |
| `severity_score` | Number | Isolation Forest anomaly score |
| `explanation` | String | Required per FR-21 |
| `acknowledged` | Boolean | Default `false` — never removes from history, never excludes from training |

**Critical:** Stage 2 results are appended to Stage 1 results — never overwrite them.

---

## 4. Master Indexing Strategy

### Governing Notes
1. Compound index field order intentionally follows equality-before-range/sort principle
2. Partial indexes deferred until real query patterns justify them (post-deployment profiling)
3. This is the initial design — to be reviewed using `explain()` and Atlas Performance Advisor after deployment

### Index Table

| Collection | Index Name | Field(s) | Type | Purpose | Query Pattern |
|---|---|---|---|---|---|
| `users` | `idx_email_unique` | `email` | Unique | Login lookup | `findOne({email})` |
| `users` | `idx_role` | `role` | Single | Admin retailer list | `find({role: "RETAILER"})` |
| `users` | `idx_is_active` | `is_active` | Single | Enable/disable views | `find({role, is_active})` |
| `refresh_tokens` | `idx_token_hash_unique` | `token_hash` | Unique | Validate on every /refresh | `findOne({token_hash})` |
| `refresh_tokens` | `idx_family_id` | `family_id` | Single | Bulk-revoke on reuse | `updateMany({family_id})` |
| `refresh_tokens` | `idx_user_id` | `user_id` | Single | Logout-all, admin disable | `find({user_id})` |
| `refresh_tokens` | `idx_ttl_expires_at` | `expires_at` | TTL | Auto-purge dead tokens | Background TTL |
| `products` | `idx_retailer_sku_unique` | `(retailer_id, sku)` | Unique Compound | Identity + ingestion lookup | `findOne({retailer_id, sku})` |
| `products` | `idx_retailer_active` | `(retailer_id, is_active)` | Compound | Dashboard product list | `find({retailer_id, is_active:true})` |
| `uploads` | `idx_upload_id_unique` | `upload_id` | Unique | Business-id lookup | `findOne({upload_id})` |
| `uploads` | `idx_retailer_created` | `(retailer_id, created_at: -1)` | Compound | Upload history view | `find({retailer_id}).sort({created_at:-1})` |
| `uploads` | `idx_status` | `status` | Single | Worker polling for queued jobs | `find({status: "UPLOADED"})` |
| `raw_sales` | `idx_retailer_product_date` | `(retailer_id, product_id, date)` | Compound | Pull product history | `find({retailer_id, product_id}).sort({date:1})` |
| `raw_sales` | `idx_upload_id` | `upload_id` | Single | Reprocess/audit upload | `find({upload_id})` |
| `raw_sales` | `idx_retailer_date` | `(retailer_id, date)` | Compound | Date-range queries | `find({retailer_id, date: {$gte,$lte}})` |
| `processed_sales` | `idx_retailer_product_date_unique` | `(retailer_id, product_id, date)` | Unique Compound | Identity + ML pipeline read | Upsert key + `find({retailer_id, product_id})` |
| `processed_sales` | `idx_retailer_date` | `(retailer_id, date)` | Compound | Dashboard date-range | `find({retailer_id, date: {$gte,$lte}})` |
| `forecast_current` | `idx_retailer_product_unique` | `(retailer_id, product_id)` | Unique Compound | Current-state + dashboard | `findOne({retailer_id, product_id})` |
| `forecast_current` | `idx_retailer_pipeline_type` | `(retailer_id, pipeline_type)` | Compound | "Needs attention" KPI | `find({retailer_id, pipeline_type: {$ne:"FULL"}})` |
| `forecast_history` | `idx_retailer_product_run_desc` | `(retailer_id, product_id, run_timestamp: -1)` | Compound | History timeline | `find({retailer_id, product_id}).sort({run_timestamp:-1})` |
| `pricing_current` | `idx_retailer_product_unique` | `(retailer_id, product_id)` | Unique Compound | Current-state + dashboard | `findOne({retailer_id, product_id})` |
| `pricing_current` | `idx_retailer_eligibility` | `(retailer_id, eligibility_status)` | Compound | "Pricing opportunities" KPI | `find({retailer_id, eligibility_status:"ELIGIBLE"})` |
| `pricing_history` | `idx_retailer_product_run_desc` | `(retailer_id, product_id, run_timestamp: -1)` | Compound | Pricing history timeline | `find({retailer_id, product_id}).sort({run_timestamp:-1})` |
| `inventory_current` | `idx_retailer_product_unique` | `(retailer_id, product_id)` | Unique Compound | Current-state + dashboard | `findOne({retailer_id, product_id})` |
| `inventory_current` | `idx_retailer_mode_classification` | `(retailer_id, mode, true_risk.classification)` | Compound | Risk-filtered views | `find({retailer_id, mode:"TRUE_RISK", "true_risk.classification":"STOCKOUT_RISK"})` |
| `anomaly_current` | `idx_retailer_product_unique` | `(retailer_id, product_id)` | Unique Compound | Current-state + dashboard | `findOne({retailer_id, product_id})` |
| `anomaly_current` | `idx_retailer_unreviewed` | `(retailer_id, has_unreviewed_alerts)` | Compound | "Needs attention" view | `find({retailer_id, has_unreviewed_alerts:true})` |

---

## 5. API Design

### Foundational Decisions

| Decision | Choice |
|---|---|
| Style | Hybrid REST + targeted aggregation endpoints (not GraphQL) |
| Versioning | URL path: `/api/v1` globally, uniform across all resources |
| Token transport | Access token in JSON body → `Authorization: Bearer` header; refresh token as `httpOnly; Secure; SameSite=Strict` cookie |
| Async upload | `POST /uploads` returns `202 Accepted` + `Location` header → client polls status endpoint |
| Product writes | `/products` is entirely read-only via API — all writes implicit through `/uploads` |
| Wave 2 dashboard | Not designed yet — additive future endpoints, no impact on Wave 1 contract |

### Endpoint Surface (`/api/v1` prefix on all)

#### Auth (`/auth`)
| Method | Endpoint | Purpose | Auth Required |
|---|---|---|---|
| POST | `/auth/register` | Retailer self-registration | No |
| POST | `/auth/login` | Login | No |
| POST | `/auth/refresh` | Exchange refresh token | Cookie |
| POST | `/auth/logout` | Revoke current session | Access token |
| POST | `/auth/logout-all` | Revoke all sessions | Access token |
| GET | `/auth/me` | Current user profile | Access token |

#### Products (`/products`) — read-only
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/products` | List all active products for retailer |
| GET | `/products/{productId}` | Single product metadata |
| GET | `/products/{productId}/summary` | **Aggregation** — fans out to all `_current` collections |

#### Uploads (`/uploads`)
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/uploads` | Submit CSV (202 + Location header) |
| GET | `/uploads` | Upload history |
| GET | `/uploads/{uploadId}/status` | Poll job status |
| GET | `/uploads/{uploadId}` | Full upload record |

#### Dashboard (`/dashboard`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/dashboard/overview` | **Aggregation** — Wave 1: KPIs + forecast-vs-actual + product table |

#### Admin (`/admin`)
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/admin/retailers` | List all retailer accounts (Admin only) |
| PATCH | `/admin/retailers/{userId}/status` | Enable/disable account |

---

## 6. Backend Folder Structure

**Framework:** FastAPI (Python)  
**Pattern:** Hybrid domain-based — domain folders for business logic + `core/` for cross-cutting infrastructure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py                  # Pydantic Settings, env vars
│   │   ├── middleware/
│   │   │   ├── auth_middleware.py     # JWT verification
│   │   │   ├── tenant_middleware.py   # retailer_id injection + enforcement
│   │   │   ├── role_middleware.py     # RBAC (RETAILER/ADMIN)
│   │   │   └── error_handler.py      # Unified error shape
│   │   ├── db/
│   │   │   └── connection.py
│   │   ├── logger.py                  # JSON structured logger
│   │   └── utils/
│   │
│   ├── domains/
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py             # Pydantic request/response models
│   │   │   ├── models.py              # Beanie/Motor document models
│   │   │   └── user.model.py + refreshToken.model.py
│   │   │
│   │   ├── products/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   │
│   │   ├── uploads/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   ├── models.py
│   │   │   ├── schema_mapping/        # Config-driven mapping layer
│   │   │   │   ├── base_mapping.py
│   │   │   │   ├── walmart_style_v1.py
│   │   │   │   └── rossmann_style_v1.py
│   │   │   └── job_queue/             # Async job dispatch interface
│   │   │
│   │   ├── sales_data/                # raw_sales + processed_sales (internal, no public router)
│   │   │   ├── raw_sales.model.py
│   │   │   ├── processed_sales.model.py
│   │   │   └── preprocessing_service.py
│   │   │
│   │   ├── forecasting/
│   │   │   ├── router.py
│   │   │   ├── service.py             # Orchestrates: fetch processed_sales → call ml/ → persist
│   │   │   ├── models.py
│   │   │   └── pipeline/              # ML orchestration glue (calls into ml/)
│   │   │
│   │   ├── pricing/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── models.py
│   │   │   └── pipeline/
│   │   │
│   │   ├── inventory/
│   │   │   ├── service.py
│   │   │   └── models.py
│   │   │
│   │   ├── anomaly/
│   │   │   ├── service.py
│   │   │   └── models.py
│   │   │
│   │   ├── dashboard/
│   │   │   ├── router.py
│   │   │   └── service.py             # ONLY sanctioned multi-domain aggregator
│   │   │
│   │   └── admin/
│   │       ├── router.py
│   │       └── service.py
│   │
│   ├── worker/
│   │   └── main.py                    # Worker entrypoint + poll loop
│   │
│   └── main.py                        # FastAPI app instantiation
│
├── tests/
├── requirements.txt
└── pyproject.toml
```

**Key rules:**
- `tenant_middleware.py` applied globally in `main.py` — never opt-in per route
- `dashboard/service.py` is the only domain permitted to import from multiple other domains
- `sales_data/` has no public router — internal data layer only
- `domains/` imports from `ml/`; `ml/` never imports from `domains/` (one-directional)

---

## 7. Frontend Folder Structure

**Framework:** React + Vite (plain SPA, no SSR)  
**Pattern:** Feature-based, mirroring backend domain structure

```
frontend/
├── src/
│   ├── shared/
│   │   ├── components/         # Button, Table, Badge, Modal, Spinner
│   │   ├── layouts/            # AppShell, AuthLayout, DashboardLayout
│   │   ├── hooks/              # useDebounce, usePolling, useAuth
│   │   ├── utils/              # formatCurrency, formatDate
│   │   ├── constants/          # API base URL, status enums
│   │   └── apiClient/          # Axios instance, auth interceptors
│   │                           # (401 → silent refresh → retry logic lives here)
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/     # LoginForm, RegisterForm
│   │   │   ├── pages/          # LoginPage, RegisterPage
│   │   │   ├── api/            # auth.api.js → /api/v1/auth/*
│   │   │   ├── hooks/          # useLogin, useCurrentUser
│   │   │   └── schemas/        # Form validation
│   │   │
│   │   ├── uploads/
│   │   │   ├── components/     # FileDropzone, UploadStatusCard, ValidationErrorList
│   │   │   ├── pages/          # UploadPage, UploadHistoryPage
│   │   │   ├── api/
│   │   │   └── hooks/          # useUploadPolling — polls GET /uploads/{id}/status
│   │   │
│   │   ├── products/
│   │   │   ├── components/     # ProductTable, ProductDetailPanel
│   │   │   ├── pages/
│   │   │   └── api/
│   │   │
│   │   ├── forecasting/
│   │   │   ├── components/     # ForecastChart, ConfidenceBadge, InsufficientDataNotice
│   │   │   └── api/
│   │   │
│   │   ├── pricing/
│   │   │   ├── components/     # PriceRecommendationCard, CandidateGridExplainer
│   │   │   └── api/
│   │   │
│   │   ├── inventory/
│   │   │   ├── components/     # RiskBadge (TRUE_RISK), AdvisoryNotice (ADVISORY)
│   │   │   └── api/
│   │   │
│   │   ├── anomaly/
│   │   │   ├── components/     # AnomalyAlertList
│   │   │   └── api/
│   │   │
│   │   ├── dashboard/
│   │   │   ├── components/     # KPICardRow, ForecastVsActualChart
│   │   │   ├── pages/          # DashboardPage — composes from all feature components
│   │   │   └── api/            # dashboard.api.js → /dashboard/overview
│   │   │
│   │   └── admin/
│   │       ├── components/     # RetailerListTable
│   │       ├── pages/          # AdminPage
│   │       └── api/
│   │
│   ├── routes/                 # React Router config, auth/role guards
│   ├── App.jsx
│   └── main.jsx
│
├── public/
├── .env.example
└── package.json
```

**Key rules:**
- `dashboard/` is the only feature permitted to import display components from other features
- `shared/apiClient/` owns the `401 → silent refresh → retry` interceptor
- Each feature's `api/` calls only its own backend domain's endpoints
- ML output translation to plain English happens in frontend feature components, not API layer

---

## 8. ML Folder Structure

**Location:** Separate top-level `ml/` directory (outside `app/domains/`)  
**Dependency rule:** `domains/` imports from `ml/`; `ml/` NEVER imports from `domains/`

```
ml/
├── forecasting/
│   ├── training/
│   │   ├── eligibility_checker.py    # Three-tier: FULL / FALLBACK / INSUFFICIENT_DATA
│   │   ├── prophet_trainer.py
│   │   ├── xgboost_trainer.py        # Trains on Prophet residuals
│   │   └── fallback_trainer.py       # Weighted moving average (stateless)
│   ├── inference/
│   │   ├── prophet_predictor.py
│   │   ├── xgboost_predictor.py
│   │   ├── fallback_predictor.py
│   │   └── forecast_composer.py      # Composes final output matching forecast_current schema
│   ├── evaluation/
│   │   ├── metrics.py                # MAE, RMSE, MAPE
│   │   └── cross_validator.py        # Walk-forward only — NOT random k-fold
│   └── schemas.py
│
├── pricing/
│   ├── training/
│   │   ├── eligibility_checker.py    # History + price variation gates (independent from forecasting)
│   │   └── elasticity_trainer.py     # Regression: Linear/RF/GBR
│   ├── inference/
│   │   ├── candidate_generator.py    # ±15% AND historical range → linspace
│   │   ├── elasticity_predictor.py   # Demand at each candidate price
│   │   └── optimizer.py              # Revenue argmax (pluggable objective: REVENUE for MVP)
│   ├── evaluation/
│   │   └── metrics.py                # R², MAE on held-out price-quantity data
│   └── schemas.py
│
├── anomaly/
│   ├── training/
│   │   └── isolation_forest_trainer.py
│   ├── inference/
│   │   ├── historical_detector.py    # Stage 1: PRE_FORECAST_HISTORICAL (never modifies processed_sales)
│   │   └── realtime_detector.py      # Stage 2: POST_UPLOAD_ALERT (reuses Stage 1 model)
│   ├── evaluation/
│   │   └── metrics.py                # Precision/recall vs manual review
│   └── schemas.py
│
├── shared/
│   ├── feature_engineering.py        # Rolling avgs, lag features, price_change_flag
│   ├── data_validator.py
│   ├── model_registry.py             # Canonical source of model_version strings
│   └── holiday_calendar.py           # Holiday derivation (country_code="IN" default)
│
└── notebooks/                         # Exploration only — not imported by app
    ├── dataset_exploration.ipynb
    ├── prophet_experimentation.ipynb
    ├── pricing_regression_exploration.ipynb
    └── anomaly_threshold_tuning.ipynb
```

**Key rules:**
- Eligibility checkers in `forecasting/training/` and `pricing/training/` are deliberately separate (different business rules: Section 8.1 vs 8.2)
- `ml/shared/feature_engineering.py` is the only sanctioned shared module between pipelines
- `ml/shared/model_registry.py` is the single source of truth for `model_version` strings
- `optimizer.py`'s pluggable objective implements Section 10.2's extensibility requirement
- `notebooks/` excluded from production imports

---

## 9. Complete System Architecture

### Five-Tier Architecture

```
┌─────────────────────────────────────────────────────┐
│  CLIENT LAYER — React + Vite SPA                    │
│  Auth · Uploads · Dashboard · Products · Admin      │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS /api/v1
┌────────────────────▼────────────────────────────────┐
│  API LAYER — FastAPI + Pydantic                     │
│  JWT auth · tenant_id enforcement · RBAC · Pydantic │
│  auth/ · uploads/ · products/ · dashboard/ · admin/ │
└──────┬──────────────────────────────────┬───────────┘
       │ async job                        │ sync read/write
┌──────▼──────────┐            ┌──────────▼────────────┐
│ BACKGROUND      │            │ DOMAIN SERVICES        │
│ WORKER          │            │ forecasting · pricing  │
│ Preprocessing   │            │ inventory · anomaly    │
│ Job status      │            │ dashboard (aggregator) │
└──────┬──────────┘            └──────────┬────────────┘
       │                                  │
┌──────▼──────────────────────────────────▼────────────┐
│  ML LAYER — ml/ (Prophet · XGBoost · scikit-learn)  │
│  ml/forecasting · ml/pricing · ml/anomaly · ml/shared│
│  One-directional: domains/ → ml/ (never reverse)    │
└──────────────────────────────┬────────────────────────┘
                               │ reads + writes
┌──────────────────────────────▼────────────────────────┐
│  DATA LAYER — MongoDB (retailer_id isolation)         │
│  users · refresh_tokens · products · uploads          │
│  raw_sales · processed_sales                          │
│  forecast_current/history · pricing_current/history   │
│  inventory_current · anomaly_current                  │
└───────────────────────────────────────────────────────┘
```

### Two Distinct Request Paths

```
Read/analytics requests:
Client → API → Domain Services → (optionally) ML → _current collections → Response

Upload/ML-trigger requests:
Client → API → 202 Accepted → Background Worker → Full ML Pipeline → MongoDB
Client polls GET /uploads/{id}/status until terminal status
```

### Key Cross-Cutting Properties
- All `_current` collections share identical key shape `(retailer_id, product_id)` → uniform dashboard fan-out
- `dashboard/service.py` is the only code permitted to aggregate across multiple domains
- No cross-tier skipping: frontend never touches MongoDB; ML layer never touches the API layer
- Inventory risk always runs after forecasting (depends on `forecast_current`); pricing runs independently (reads `processed_sales` directly, not `forecast_current`)

---

## 10. Authentication Flow

### Token Model
- Access token: JWT, 15–30 min expiry, returned in JSON body, sent as `Authorization: Bearer` header
- Refresh token: rotating + reuse-detection with family revocation, stored as SHA-256 hash in MongoDB, transmitted as `httpOnly; Secure; SameSite=Strict` cookie scoped to `Path=/api/v1/auth/refresh`
- Access token stored in React state (in-memory only) — lost on page reload, silently re-issued from cookie

### Flow 1: Registration
```
POST /auth/register
  → Validate email uniqueness
  → Hash password (Argon2)
  → Insert users doc (role=RETAILER, is_active=true)
  → Return 201 + user profile (no tokens — explicit login required)
```

### Flow 2: Login
```
POST /auth/login
  → Validate credentials → Argon2 verify
  → If is_active=false → 403
  → Generate access token (JWT) + refresh token (random bytes → SHA-256 stored)
  → Insert refresh_tokens doc (new family_id)
  → Update last_login_at
  → Body: { access_token, user }
  → Set-Cookie: refresh_token; HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth/refresh
```

### Flow 3: Authenticated Request
```
Protected endpoint
  → auth_middleware: verify JWT signature + expiry
  → tenant_middleware: extract retailer_id from claims
  → role_middleware: check role if admin route
  → If JWT expired → 401 (triggers Flow 4 on frontend)
```

### Flow 4: Silent Token Refresh (frontend interceptor)
```
shared/apiClient/ catches 401
  → POST /api/v1/auth/refresh (cookie auto-sent)
  → Backend:
    1. Hash raw cookie token → lookup by token_hash
    2. Not found → 401 → redirect to /login
    3. Found but revoked=true:
         REUSE DETECTED
         updateMany({family_id}, {revoked:true, revoked_reason:"REUSE_DETECTED"})
         401 + clear cookie → redirect to /login
    4. Found, valid, not revoked:
         Mark old: revoked=true, revoked_reason="ROTATED"
         Issue new access token + new refresh token (same family_id)
         Insert new refresh_tokens doc
         Body: { access_token } + Set-Cookie: new refresh token
  → Frontend: store new access_token in memory → retry original request
  → If retry also 401 → redirect /login (no loop)
```

### Flow 5: App Boot / Page Reload
```
React mounts → access_token null (in-memory, lost)
  → Silently POST /auth/refresh (cookie present if session active)
  → Success → set access_token in memory → render app
  → Failure → redirect to /login
```

### Flow 6: Logout (single session)
```
POST /auth/logout
  → refresh_tokens: revoked=true, revoked_reason="LOGOUT"
  → Clear httpOnly cookie (Set-Cookie with past expiry)
  → Frontend clears in-memory access_token → /login
```

### Flow 7: Logout All Sessions
```
POST /auth/logout-all
  → updateMany({user_id}, {revoked:true, revoked_reason:"LOGOUT"})
  → Clear cookie → /login
```

### Flow 8: Admin Disabling Account
```
PATCH /admin/retailers/{userId}/status { is_active: false }
  → users.is_active = false
  → updateMany({user_id}, {revoked:true, revoked_reason:"ADMIN_DISABLE"})
  → Next retailer /refresh → revoked token → re-login → is_active=false → 403
  → Short access token TTL (15–30 min) limits blast radius
```

---

## 11. Request Flow

### Flow 1: Standard Read (GET /dashboard/overview)
```
1. DashboardPage mounts → dashboard.api.js → GET /api/v1/dashboard/overview
   Authorization: Bearer <in-memory access_token>

2. API: auth_middleware → tenant_middleware injects retailer_id

3. dashboard/service.py (parallel async fan-out):
   asyncio.gather(
     forecast_current.find({retailer_id, product_id}),  # per product
     pricing_current.find({retailer_id, product_id}),
     inventory_current.find({retailer_id, product_id}),
     anomaly_current.find({retailer_id, product_id}),
     products.find({retailer_id, is_active:true}),
     processed_sales aggregation for KPIs
   )

4. Response assembled:
   { kpis, forecast_vs_actual, product_table }

5. Frontend: ML enums translated to plain English in feature components
   (FALLBACK → "Lower confidence estimate" in ConfidenceBadge)
   Service layer returns raw enums — never translates for UI
```

### Flow 2: Product Summary (GET /products/{productId}/summary)
```
1. User clicks product row → GET /api/v1/products/{productId}/summary

2. products/service.py:
   Validate productId belongs to retailer_id (security: 404 if mismatch)
   Parallel fan-out to all _current collections + processed_sales (sparkline)

3. Response: { product, forecast, pricing, inventory, anomaly }

4. Frontend: each section rendered by its feature component
   (ForecastChart, CandidateGridExplainer, RiskBadge/AdvisoryNotice, AnomalyAlertList)
```

### Flow 3: Write (PATCH /admin/retailers/{userId}/status)
```
1. admin.api.js → PATCH /api/v1/admin/retailers/{userId}/status
   Body: { is_active: false }

2. role_middleware → asserts role=ADMIN (403 if RETAILER)

3. admin/service.py:
   users.update_one({_id: userId}, {is_active: false})
   refresh_tokens.update_many({user_id: userId, revoked: false},
     {revoked: true, revoked_reason: "ADMIN_DISABLE"})

4. 200 OK + updated user summary
```

### Cross-Cutting Invariants
| Concern | Mechanism |
|---|---|
| Tenant isolation | `tenant_middleware` injects `retailer_id` from JWT; never from query param or body |
| 401 handling | `shared/apiClient/` intercept: silent refresh + retry, transparent to feature code |
| Parallel reads | FastAPI + Motor async: concurrent fan-out, not sequential waterfall |
| ML output translation | Frontend feature components only — service layer returns raw enums |
| Error shape | `error_handler.py`: `{ error: { code, message, detail } }` uniformly |

---

## 12. File Upload Flow

### Phase 1: Submission & Pre-Acceptance Validation
```
POST /api/v1/uploads (multipart: file + schema_mapping)

PRE-ACCEPTANCE (synchronous, before DB write):
  → File extension: .csv only
  → MIME type: actual header bytes verified (not just client claim)
  → File size: ≤ configured limit
  → schema_mapping: must exist in mapping registry

On failure → 400 Bad Request (no uploads doc created)

On success:
  → uploads.insert_one({status: "UPLOADED", ...})
  → Job dispatched to background worker
  → 202 Accepted + Location: /api/v1/uploads/{upload_id}/status
```

### Phase 2: Worker — Validation Stage
```
Worker polls uploads for status="UPLOADED" (atomic claim via update_one condition check)
→ status: VALIDATING

Row-level validation:
  → Apply schema_mapping (rename source cols → internal field names)
  → Validate each row: required fields, date parseable, quantity_sold ≥ 0
  → Collect row_warnings, count rows_valid / rows_rejected

On failure (0 valid rows OR row_count > limit):
  → status: REJECTED, validation_errors populated
  → EXIT

On success:
  → Proceed to Phase 3
```

### Phase 3: Worker — Ingestion Stage
```
current_stage: "ingesting"

FOR EACH VALID ROW:
  normalized_sku = row.sku.strip().lower()
  products.find_one({retailer_id, sku: normalized_sku})
    → Found: reuse _id, update last_seen_upload_id
    → Not found: products.insert_one({...auto-created from CSV metadata...})
  raw_sales.insert_one({...all fields + source_row_raw...})
```

### Phase 4: Worker — Preprocessing Stage
```
current_stage: "preprocessing"

FOR EACH PRODUCT in upload:
  Fetch ALL raw_sales for (retailer_id, product_id)
  (full history — ensures rolling features computed on complete history)
  
  Transaction-level → daily aggregation if needed
  
  Feature engineering (ml/shared/feature_engineering.py):
    day_of_week, is_weekend, rolling_avg_7d, rolling_avg_30d,
    lag_1d_quantity, price_change_flag, holiday_flag
  
  processed_sales.update_one(upsert keyed on unique compound index)
```

### Phase 5: Worker — ML Pipeline Stage
```
Pipeline sequence:

[current_stage: "anomaly_detection"]
  ml/anomaly Stage 1 — historical detection per product
  → anomaly_current.update_one(upsert, stage 1 results)
  INVARIANT: zero writes to raw_sales or processed_sales

[current_stage: "forecasting"]
  ml/forecasting per product:
    eligibility_checker → FULL / FALLBACK / INSUFFICIENT_DATA
    fit + infer (or mark insufficient)
  → forecast_current.update_one(upsert) + forecast_history.insert_one

[current_stage: "pricing"]
  ml/pricing per product:
    eligibility_checker → ELIGIBLE / INSUFFICIENT_*
    fit elasticity → generate candidates → optimize
  → pricing_current.update_one(upsert) + pricing_history.insert_one

[current_stage: "inventory"]
  AFTER forecasting (depends on forecast_current):
    inventory_level present → TRUE_RISK → days_of_cover → classification
    inventory_level absent  → ADVISORY  → demand_trend + message
  → inventory_current.update_one(upsert)

[stage 2 anomaly]
  ml/anomaly Stage 2 — new rows only
  → anomaly_current: $push stage 2 flags (NEVER overwrites stage 1)
  → has_unreviewed_alerts = true if any POST_UPLOAD_ALERT found
```

### Phase 6: Completion & Frontend Update
```
Worker:
  COMPLETED or COMPLETED_WITH_WARNINGS or FAILED
  → uploads.update_one(final status + processing_completed_at)

Frontend useUploadPolling hook:
  Polls every N seconds until terminal status
  → Updates UploadStatusCard with current_stage label
  → On COMPLETED: success + invalidate dashboard cache
  → On REJECTED: show validation_errors (which fields missing)
  → On FAILED: show error_reason
```

---

## 13. ML Pipeline Flow

### Configuration Constants (all in `core/config.py`, never hardcoded in ml/)
```
FORECAST_FULL_PIPELINE_MIN_DAYS = 30
FORECAST_FALLBACK_FLOOR_DAYS = 7
PRICING_PRICE_VARIATION_THRESHOLD = 0.05
PRICING_BOUND_PCT = 0.15
PRICING_N_CANDIDATES = 20
ANOMALY_SPIKE_THRESHOLD = 2.0
ANOMALY_DROP_THRESHOLD = 0.3
```

### Pipeline 1: Demand Forecasting

#### Eligibility Check
```
history_days >= 30       → FULL (Prophet + XGBoost)
history_days >= 7 (floor) → FALLBACK (moving average)
history_days < floor      → INSUFFICIENT_DATA (no model, explicit reason, exit)
```

#### Full Pipeline — Prophet + XGBoost
```
Prophet:
  Input: ds=date, y=quantity_sold + regressors (promotion_flag, holiday_flag)
  Output: fitted Prophet model

XGBoost (on residuals):
  residuals = actual - Prophet in-sample predictions
  Features: [day_of_week, is_weekend, rolling_avg_7d, lag_1d_quantity,
             price_change_flag, promotion_flag, holiday_flag]
  Output: fitted XGBoost model

forecast_composer:
  future_dates 7d + 30d
  final = Prophet.predict + XGBoost.predict (residual correction)
  Clip negatives to 0
  Output: { horizon_7d, horizon_30d, confidence: "high" }
```

#### Fallback Pipeline
```
Weighted moving average (stateless) → flat value for 7 days only
horizon_30d = null (scientifically indefensible from <30 days)
confidence: "low"
```

#### Evaluation (Section 10.5)
```
Walk-forward time-series cross-validation ONLY (NOT random k-fold)
Minimum 3 splits
Metrics per split: MAE, RMSE, MAPE
Assert: no validation date earlier than any training date
```

### Pipeline 2: Dynamic Pricing

#### Eligibility Check
```
CHECK 1: history_days >= 30           → else INSUFFICIENT_HISTORY
CHECK 2: price_cv >= 0.05 threshold   → else INSUFFICIENT_PRICE_VARIATION
Both must pass → ELIGIBLE
```

#### Elasticity Training
```
Feature matrix: [selling_price, promotion_flag, holiday_flag, day_of_week, rolling_avg_7d]
Target: quantity_sold
Model: Linear Regression (baseline, defensible default; RF/GBR noted as alternatives)
```

#### Candidate Generation + Optimization
```
bound_min = current_price × (1 - bound_pct)
bound_max = current_price × (1 + bound_pct)
effective_min = max(bound_min, historical_min)   # both bounds applied
effective_max = min(bound_max, historical_max)
candidates = linspace(effective_min, effective_max, N_CANDIDATES)

FOR EACH candidate:
  estimated_demand = elasticity_model.predict([candidate, context...])
  estimated_demand = max(0, estimated_demand)  # clip negatives
  estimated_revenue = candidate × estimated_demand

recommended_price = argmax(candidates, key=estimated_revenue)

SANITY CHECK: recommended_price MUST be within bound_range
  (if not: pipeline bug, not acceptable edge case)
```

#### Evaluation
```
80/20 chronological split
R² and MAE on held-out quantity predictions
Verify recommended_price within bound_range
```

### Pipeline 3: Anomaly Detection

#### Stage 1 — Historical
```
IsolationForest(contamination="auto") fit on:
  Features: [quantity_sold, selling_price, rolling_avg_7d, day_of_week]

For each anomaly (predict == -1):
  IF quantity_sold > rolling_avg_7d × 2.0  → SPIKE
  ELIF quantity_sold < rolling_avg_7d × 0.3 → DROP
  ELSE → UNUSUAL

  explanation: human-readable with date + magnitude (FR-21)

CRITICAL INVARIANT: zero writes to raw_sales or processed_sales
```

#### Stage 2 — Post-Upload Alert
```
Reuse fitted Stage 1 model (not refitted)
Apply to new rows only
Stage = "POST_UPLOAD_ALERT"
Append to anomaly_current (NEVER overwrite Stage 1)
Set has_unreviewed_alerts = true if any found
```

---

## 14. Deployment Architecture

### Service Map

| Service | Local Dev | Cloud (Prod) |
|---|---|---|
| Frontend | Vite dev server :5173 | Vercel/Netlify (static CDN) |
| Backend | Uvicorn :8000 | Render/Railway |
| Worker | Separate Docker service | Render/Railway (separate service) |
| MongoDB | Docker `mongo:7` container | MongoDB Atlas M0/M2 |

### Docker Compose Structure
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    environment: { VITE_API_BASE_URL: http://localhost:8000 }
    depends_on: [backend]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment: { MONGODB_URL, JWT_SECRET, CORS_ORIGINS, ... }
    depends_on: [mongo]

  worker:
    build: ./backend              # SAME image as backend
    command: python -m app.worker.main   # different entrypoint
    environment: { MONGODB_URL, WORKER_POLL_INTERVAL_SECONDS: 5 }
    depends_on: [mongo]

  mongo:
    image: mongo:7
    volumes: [mongo_data:/data/db]
```

### Worker Job Coordination (no Redis — MongoDB polling)
```python
# Poll loop (every WORKER_POLL_INTERVAL_SECONDS):
job = uploads.find_one({status: "UPLOADED"}, sort=[("created_at", 1)])
if job:
    result = uploads.update_one(
        {_id: job._id, status: "UPLOADED"},   # condition re-checked (atomic claim)
        {$set: {status: "VALIDATING", processing_started_at: now()}}
    )
    if result.matched_count == 1:
        execute_pipeline(job)    # safe for future multi-worker scaling
```

### CORS Configuration
```python
CORSMiddleware(
    allow_origins=["https://<project>.vercel.app", "http://localhost:5173"],
    allow_credentials=True,      # REQUIRED for httpOnly cookie
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Cookie `Secure` Flag
- Local dev: `Secure` flag omitted (no HTTPS on localhost)
- Production: `Secure` + `SameSite=Strict` active
- Driven by `APP_ENV` environment variable in auth service — not hardcoded

### CI/CD (GitHub Actions)
```
test.yml:           PR to main → run full test suite → block merge on failure
deploy-backend.yml: push to main → pytest → Render/Railway deploy hook
deploy-frontend.yml: push to main → npm run build → Vercel/Netlify deploy
```

---

## 15. Testing Strategy

### Tools
- **Backend + ML:** pytest + pytest-asyncio
- **Frontend:** React Testing Library
- **E2E:** Deferred (high maintenance, lower ROI for academic timeline)

### Test Configuration
```ini
# pytest.ini
[pytest]
asyncio_mode = auto
markers =
  unit: fast, no DB required
  integration: requires test MongoDB
  evaluation: ML metrics (run selectively)

# Subsets:
# pytest -m unit          → fast CI on every PR
# pytest -m integration   → CI on main branch merge
# pytest -m evaluation    → ML metrics (manual or nightly)
```

### Coverage Priorities
| Layer | Target | Priority |
|---|---|---|
| ML eligibility + pipeline logic | 90%+ | Highest |
| Tenant isolation + auth security | 100% | Non-negotiable |
| Backend service layer | 80%+ | High |
| API integration | All endpoints covered | High |
| Frontend translation components | 80%+ | Medium |

### Critical Test Cases

#### Auth Security
```python
test_refresh_token_reuse_revokes_family()      # Most critical security test
test_retailer_cannot_access_another_retailers_data()  # Tenant isolation
test_token_not_stored_in_plaintext()
```

#### ML Correctness
```python
# Forecasting
test_insufficient_data_includes_reason_string()
test_negative_predictions_clipped_to_zero()
test_fallback_horizon_30d_is_null()
test_cross_validation_is_walk_forward_not_random_kfold()

# Pricing
test_constant_price_returns_INSUFFICIENT_PRICE_VARIATION()
test_candidates_within_bound_pct()
test_candidates_within_historical_range()
test_recommended_price_is_revenue_argmax()
test_recommended_price_within_bound_range()

# Anomaly
test_stage_1_flags_do_not_modify_processed_sales()
test_all_flags_include_explanation_string()
test_stage_2_appends_to_stage_1_results()
```

#### Upload Validation
```python
test_validation_error_message_names_missing_fields()  # FR-7
test_mapping_preserves_source_row_raw_unchanged()     # Immutability
```

#### Frontend Translation (Transparent Communication principle)
```javascript
// ConfidenceBadge: never renders null for valid pipeline_type
// PriceRecommendationCard: never shows price when ineligible
// RiskBadge/AdvisoryNotice: advisory never uses stockout/overstock language
// useUploadPolling: stops on terminal status (no infinite loop)
```

### Test Data Strategy
```
Synthetic processed_sales factory (configurable trend/seasonality/noise)
→ No dependency on external dataset for test execution
→ Tests pass regardless of which dataset is chosen for production
```

---

## 16. Logging & Monitoring

### Log Format — Structured JSON
Every backend log line (API, worker, ML):
```json
{
  "timestamp": "2026-07-01T09:04:22.431Z",
  "level": "INFO",
  "service": "backend",
  "module": "domains.uploads.service",
  "message": "Upload processing completed",
  "request_id": "req-7f3a1e2b",
  "retailer_id": "66ab1c2f3a9e1b2c3d4e5f60",
  "upload_id": "UPL-20260701-a3f9",
  "duration_ms": 4217,
  "extra": {}
}
```

### Log Level Convention
| Level | Used For |
|---|---|
| DEBUG | Disabled in production |
| INFO | Normal operations: request received, stage started, model fitted |
| WARNING | Expected-but-notable: row rejections, fallback eligibility |
| ERROR | Unexpected failures: pipeline crash, DB write failure |
| CRITICAL | Startup failures: DB unreachable, missing config |

### What Never Gets Logged
- `password` / `password_hash`
- Raw token values
- `source_row_raw` contents (retailer PII)
- `retailer_id` on auth endpoints (avoid identity correlation with failures)

### Monitoring Stack
- **Sentry (free tier):** Error tracking, stack traces with `retailer_id`/`upload_id` scope tags, alerts on new error types
- **Render/Railway native:** CPU, memory, p50/p95 response times, deploy health
- **MongoDB Atlas:** Query execution times, slow query log (>100ms), connection pool, Performance Advisor for index suggestions (post-deployment)

### Debug Playbook
```
Crash during demo:    Render log viewer → filter by upload_id → exact stage at failure
Slow dashboard:       Atlas slow query log → identify missing index
Wrong ML output:      forecast_history / pricing_history → query past runs
False positive anomalies: notebooks/anomaly_threshold_tuning.ipynb → retune contamination
```

---

## 17. Scalability

**Framing (Section 7 NFR):** Schema and pipeline design must not preclude future support for higher data volumes. This audit identifies exact ceiling points and additive upgrade paths — no upgrade requires a schema migration or API contract change.

### MongoDB
| Aspect | MVP Ceiling | First Bottleneck | Upgrade Path |
|---|---|---|---|
| Storage | Atlas M0 (512MB) | `raw_sales` + `processed_sales` growth | M10/M20 tier upgrade (no code change) |
| Time-series scale | One doc per record | Millions of docs per large retailer | MongoDB Time Series Collections (anticipated in Topic 1 — one collection rename + backfill) |
| raw_sales archival | Unbounded growth | Storage cost over years | Cold-storage policy (S3 via Atlas Data Federation) — additive |
| Sharding | Not needed at MVP scale | Retailer count × product count at enterprise scale | Shard key: `{retailer_id: "hashed"}` — aligns naturally with all compound indexes |

### FastAPI Backend
| Aspect | MVP Ceiling | First Bottleneck | Upgrade Path |
|---|---|---|---|
| Concurrent users | Single Uvicorn process | Process saturation | `--workers 4` (stateless design supports this immediately) |
| Horizontal scale | Single instance | Traffic growth | Multiple instances behind load balancer — works without Redis because API is stateless (JWT + DB-backed sessions) |
| Dashboard query speed | N products × 5 collections | Fan-out at 10k+ products | Redis cache on `/dashboard/overview` per `retailer_id` (60s TTL) — additive, no schema change |

### Background Worker
| Aspect | MVP Ceiling | First Bottleneck | Upgrade Path |
|---|---|---|---|
| Concurrency | One job at a time | Multiple simultaneous uploads | Multiple worker instances (atomic MongoDB claim already designed for this) |
| Product processing | Sequential per job | O(products) × Prophet fitting time | Python multiprocessing per job (change in worker main, not ML code) |
| Job coordination | MongoDB polling | Latency at high job frequency | Task queue (Celery + Redis / ARQ) — uploads/jobs split becomes natural; no ML code changes |
| Model refit cost | Refit every upload | Large product catalogs | Serialize models (joblib) to object storage; reuse if training data unchanged (model_registry.py already designed as cache-key mechanism) |

### ML Models
- **Prophet** is the dominant cost: 5–30 seconds per product per fit
- **Step 1:** Parallel product fitting (most immediate win)
- **Step 2:** Serialize fitted models → incremental retraining on new data only
- **Step 3:** Category-level models (Section 11 deferred item — `category` field already on `products` collection, no migration needed)
- **Step 4:** GPU-accelerated compute for XGBoost (ML code extraction to remote service is clean due to one-directional dependency boundary)

### Frontend
- Static CDN delivery → effectively unlimited scale for the frontend itself
- Bottleneck is the API it calls, not the delivery
- Pagination on product table + virtual scrolling → additive frontend change
- React Query / SWR for client-side caching → additive library addition

### Summary Table
| Component | MVP Ceiling | First Bottleneck | Upgrade Complexity |
|---|---|---|---|
| MongoDB | ~50 retailers, millions of docs | raw_sales storage | Low |
| FastAPI backend | ~50 concurrent users | Dashboard fan-out | Low (stateless by design) |
| Background worker | ~5 concurrent uploads | Prophet fitting time | Medium |
| Frontend | Unlimited (CDN) | Dashboard render at 10k+ products | Low |
| Auth layer | Thousands of sessions | Not a realistic bottleneck | Very low |
| ML models | ~100 products per job | Prophet O(products) | Medium |

---

## Appendix: All Locked Decisions (Quick Reference)

| # | Decision | Choice |
|---|---|---|
| 1 | Multi-tenancy model | Shared collections + `retailer_id` enforced via schema validation + middleware |
| 2 | Sales data modeling | Hybrid: `raw_sales` (immutable) + `processed_sales` (analytical) |
| 3 | Feature storage | Single `processed_sales` collection (no separate feature store for MVP) |
| 4 | Forecast/pricing retention | Hybrid current/history per pipeline |
| 5 | Pipeline output collections | Separate collections per pipeline |
| 6 | Inventory output | Current-only (`inventory_current`), no history for MVP |
| 7 | Anomaly output | Current-only (`anomaly_current`), no history for MVP |
| 8 | Product creation | Implicit on upload (no Product Management UI) |
| 9 | Upload + job tracking | Single `uploads` collection |
| 10 | User accounts | Single `users` collection with `role` enum |
| 11 | Refresh token policy | Rotation + reuse-detection with family revocation |
| 12 | ID strategy | ObjectId universal PK; business IDs only where externally meaningful |
| 13 | Forecast horizons | One doc per product, both horizons nested inside |
| 14 | Pricing candidate storage | Full candidate grid persisted (not just winning price) |
| 15 | Inventory mode separation | Mode-segregated nested objects (structurally exclusive) |
| 16 | Anomaly structure | Embedded array in one doc per product |
| 17 | API style | Hybrid REST + targeted aggregation endpoints |
| 18 | API versioning | URL path `/api/v1` global |
| 19 | Token transport | Access token in JSON body; refresh token as `httpOnly` cookie |
| 20 | Async upload | `202 Accepted` + `Location` header; client polls |
| 21 | Backend language | Python / FastAPI |
| 22 | Backend structure | Hybrid domain-based + `core/` |
| 23 | Frontend framework | React + Vite (plain SPA) |
| 24 | Frontend structure | Feature-based mirroring backend domains |
| 25 | ML code location | Separate top-level `ml/` directory |
| 26 | ML dependency direction | `domains/` → `ml/` (one-directional; `ml/` never imports `domains/`) |
| 27 | Worker model | Separate containerized service; MongoDB polling (no Redis) |
| 28 | Deployment | Docker Compose local; Vercel + Render/Railway + Atlas cloud |
| 29 | Testing tools | pytest + pytest-asyncio + React Testing Library (no E2E for MVP) |
| 30 | Logging format | Structured JSON (Python logging + JSON formatter) |
| 31 | Monitoring | Sentry (errors) + Render/Railway native (performance) |
| 32 | Access token storage | In-memory React state only (not localStorage/sessionStorage) |

---

*Document generated from Phase 1 (Product Discovery) + Phase 2 (System Design) architecture sessions.*  
*Phase 2 frozen — do not modify decisions without explicit scope amendment.*  
*Phase 3 (Implementation Blueprint) proceeds from this document.*
