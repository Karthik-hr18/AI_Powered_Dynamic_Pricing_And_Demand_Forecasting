# Machine Learning Interface Boundary Spec

This document establishes the official architectural boundary between the offline Machine Learning development cycle (performed in Google Colab) and the online production FastAPI application (serving inference-only).

---

## 1. Division of Responsibilities

To avoid model drift and ensure separation of concerns, the project limits responsibilities as follows:

| Stage / Task | Google Colab (Offline ML) | FastAPI Backend (Production App) |
|---|---|---|
| **Exploratory Data Analysis (EDA)** | **Yes** (Analyze data sparsity and distributions) | No |
| **Data Cleaning** | **Yes** (Determine outlier bounds, missing values rules) | No |
| **Feature Engineering** | **Yes** (Develop rolling avgs/lags formulas, window spans) | **Yes** (Verbatim replication for live inference feature matrix) |
| **Model Training & Tuning** | **Yes** (Fit models, search hyperparameters) | No (Never calls `fit` or changes weights) |
| **Model Evaluation** | **Yes** (Calculate MAE, RMSE, MAPE, R² metrics) | No |
| **Artifact Export** | **Yes** (Serialize `.pkl`/`.joblib` models and generate `metadata.json`) | No |
| **Model Loading & Caching** | No | **Yes** (Load pre-trained artifacts on startup, cache in memory) |
| **Production Inference** | No | **Yes** (Predict forecasting, elasticity demand, anomalies) |
| **Persistence & Serving** | No | **Yes** (Write results to MongoDB, return through dashboard APIs) |

---

## 2. Directory & Path Specification

All ML models must be exported and copied into the `backend/artifacts/` folder matching the directory layout:

```text
backend/artifacts/
├── forecasting/
│   ├── forecast_v1.pkl       # Serialized composite/ensemble model
│   └── metadata.json         # Manifest schema details
├── pricing/
│   ├── pricing_v1.pkl        # Elasticity regressor
│   └── metadata.json
└── anomaly/
    ├── anomaly_v1.pkl        # Isolation Forest outlier detector
    └── metadata.json
```

---

## 3. Input Features & Expected Outputs

The input vectors fed to models by the backend must exactly match the feature matrix generated during training in Google Colab.

### 3.1 Demand Forecasting
- **Required Features**:
  - `day_of_week` (int, 0–6)
  - `is_weekend` (bool)
  - `rolling_avg_7d` (float or null)
  - `lag_1d_quantity` (int or null)
  - `price_change_flag` (bool or null)
  - `promotion_flag` (bool)
  - `holiday_flag` (bool)
- **Expected Output**:
  - Predicted quantity sold (float, clipped to >= 0) for future horizon dates.

### 3.2 Dynamic Pricing (Price Elasticity)
- **Required Features**:
  - `selling_price` (float)
  - `promotion_flag` (bool)
  - `holiday_flag` (bool)
  - `day_of_week` (int, 0–6)
  - `rolling_avg_7d` (float or null)
- **Expected Output**:
  - Estimated demand (float, clipped to >= 0) at candidate price.

### 3.3 Anomaly Detection (Outliers)
- **Required Features**:
  - `quantity_sold` (int)
  - `selling_price` (float)
  - `rolling_avg_7d` (float or null)
  - `day_of_week` (int, 0–6)
- **Expected Output**:
  - Decision label (-1 for anomaly, 1 for normal).

---

## 4. Versioning & Compatibility

Every model folder must contain a `metadata.json` manifest specifying:
1. **`model_version`**: Semantic version string (e.g. `1.0.0`).
2. **`framework_versions`**: Python, `scikit-learn`, `xgboost`, and `prophet` versions. The backend validates compatibility upon loading; mismatching patch versions generate warnings, while mismatching major/minor versions cause startup exceptions to avoid binary parsing faults.

---

## 5. Artifact Loading & Cache Lifecycle

1. **Startup Loading**: When the worker process initializes, it instantiates the `ArtifactLoader`.
2. **Parsing & Validation**: The loader scans directories, reads `metadata.json`, checks file structures, and loads binary `.pkl` / `.joblib` instances.
3. **Memory Caching**: Loaded models are cached in memory as singleton objects.
4. **Getters**: Domain inference services obtain the active model instances from the loader using generic domain keys.
5. **Errors & Failures**:
   - If files are missing: Raises `FileNotFoundError` during backend/worker startup, blocking ready status.
   - If validation fails (NaNs or schema errors): The pipeline logs critical structured JSON warnings and flags the current pipeline stage status as `FAILED`, preserving database transactions.

---

## 6. Future-Proofing Abstract Layer

The loader is designed using the **Abstract Provider Pattern**. 
The core implementation defines a file system loader. In the future, this can be swapped out to retrieve artifacts from Cloud Object Stores (S3, GCS, Azure Blob) by implementing a new reader class, with zero changes required to the domain-level services (`forecasting/service.py`, `pricing/service.py`, etc.).
