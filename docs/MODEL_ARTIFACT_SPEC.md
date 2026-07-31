# Model Artifact Specification

This specification defines the standard structure, metadata schemas, and serialization requirements for every machine learning model artifact consumed by the website.

---

## 1. Directory Layout

All artifacts are organized by domain in the `backend/artifacts/` folder:

```text
backend/
└── artifacts/
    ├── forecasting/
    │   ├── forecast_v1.pkl
    │   └── metadata.json
    │
    ├── pricing/
    │   ├── pricing_v1.pkl
    │   └── metadata.json
    │
    └── anomaly/
        ├── anomaly_v1.pkl
        └── metadata.json
```

---

## 2. Metadata Schema (`metadata.json`)

Every model artifact directory must include a `metadata.json` manifest. Below is the standardized structure:

```json
{
  "model_name": "forecasting",
  "model_version": "1.0.0",
  "algorithm": "Prophet + XGBoost Residual Correction",
  "trained_on": "2026-08-01",
  "dataset": "Retail Ingestion Dataset v2.4",
  "framework_versions": {
    "python": "3.13.7",
    "scikit-learn": "1.6.0",
    "xgboost": "2.0.3",
    "prophet": "1.1.5"
  },
  "required_features": [
    "day_of_week",
    "is_weekend",
    "rolling_avg_7d",
    "lag_1d_quantity",
    "price_change_flag",
    "promotion_flag",
    "holiday_flag"
  ],
  "target": "quantity_sold",
  "metrics": {
    "mae": 1.24,
    "rmse": 1.98,
    "mape": 0.145
  }
}
```

### Metadata Fields Definition
* **`model_name`**: The identifier of the ML pipeline domain (`forecasting`, `pricing`, `anomaly`).
* **`model_version`**: Semantic versioning string (`MAJOR.MINOR.PATCH`).
* **`algorithm`**: Exact description of the model architecture.
* **`trained_on`**: ISO-8601 date string of training completion.
* **`dataset`**: Friendly identifier of the dataset used for model training.
* **`framework_versions`**: Sub-object specifying key dependencies used during training.
* **`required_features`**: Ordered array of feature column names required for model input.
* **`target`**: Target column name the model predicts.
* **`metrics`**: Object containing training/testing evaluation scores.

---

## 3. Individual Artifact Specifications

### 3.1 Demand Forecasting Artifact
* **Filename**: `forecast_v1.pkl`
* **Purpose**: Generates 7-day and 30-day quantity forecasts for SKU sales.
* **Model**: Prophet (baseline time-series) coupled with XGBoost (predicts Prophet residuals).
* **Serialization Format**: `pickle` (version 5 or higher) or `joblib`.
* **Required Features**:
  * `day_of_week` (int)
  * `is_weekend` (bool)
  * `rolling_avg_7d` (float or null)
  * `lag_1d_quantity` (int or null)
  * `price_change_flag` (bool or null)
  * `promotion_flag` (bool)
  * `holiday_flag` (bool)
* **Expected Output**:
  * Continuous prediction vector representing quantity sold per future timestamp.

### 3.2 Dynamic Pricing Artifact
* **Filename**: `pricing_v1.pkl`
* **Purpose**: Predicts demand across a price range candidate grid to select revenue-maximizing prices.
* **Model**: Elasticity Linear Regression.
* **Serialization Format**: `joblib` or `pickle`.
* **Required Features**:
  * `selling_price` (float)
  * `promotion_flag` (bool)
  * `holiday_flag` (bool)
  * `day_of_week` (int)
  * `rolling_avg_7d` (float or null)
* **Expected Output**:
  * Predicted demand quantity (float) at the evaluated price.

### 3.3 Anomaly Detection Artifact
* **Filename**: `anomaly_v1.pkl`
* **Purpose**: Flags historical sales data anomalies and evaluates post-upload transaction rows.
* **Model**: Isolation Forest.
* **Serialization Format**: `joblib` or `pickle`.
* **Required Features**:
  * `quantity_sold` (int)
  * `selling_price` (float)
  * `rolling_avg_7d` (float)
  * `day_of_week` (int)
* **Expected Output**:
  * Vector containing `-1` (anomalous data point) or `1` (normal data point).
