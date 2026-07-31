# Google Colab ML Training Workflow & Export Guide

This guide is for the Machine Learning (ML) engineering team. It describes the offline training procedure in Google Colab, artifact serialization conventions, and how to safely integrate pre-trained models into the FastAPI application.

---

## 1. Dataset Acquisition & Location

1. **Source Data**: The training dataset must consist of historical sales transactions (`raw_sales` structure) and product lists (`products` structure).
2. **Ingestion Format**: Store training dataset CSV files inside a Google Drive directory (e.g. `/content/drive/MyDrive/RetailML/data/`) or load directly from the MongoDB Atlas connection in Colab.
3. **Data Sparesness Guidelines**:
   - Ensure products have $\ge 30$ days of historical data for the **FULL (Prophet + XGBoost)** pipeline.
   - Fallback weighted moving averages are calculated on $\ge 7$ days of data.

---

## 2. Model Training Order

For a successful compose run, train the models in the following sequence:

1. **Anomaly Detection (Isolation Forest)**:
   - Fit on historical features `[quantity_sold, selling_price, rolling_avg_7d, day_of_week]`.
   - Outliers must be labeled and flagged but *never* removed automatically from the training datasets of the subsequent steps (anomalies could represent authentic business events like holidays or promotions).
2. **Demand Forecasting (Prophet & XGBoost Residual Composer)**:
   - **Step A**: Fit a Prophet model on the baseline historical time-series (`ds` and `y`) including regressors (`promotion_flag`, `holiday_flag`).
   - **Step B**: Generate in-sample Prophet predictions and compute residuals: $\text{residuals} = \text{actual} - \text{predicted}$.
   - **Step C**: Fit an XGBoost model on these residuals using features `[day_of_week, is_weekend, rolling_avg_7d, lag_1d_quantity, price_change_flag, promotion_flag, holiday_flag]`.
3. **Price Elasticity (Linear/Regression Elasticity)**:
   - Fit on historical sales records mapping `quantity_sold` against `[selling_price, promotion_flag, holiday_flag, day_of_week, rolling_avg_7d]`.

---

## 3. Export Command & Serialization

Serialize the final fitted estimators using `pickle` (version 5) or `joblib`. 

### Python Code Example (Google Colab)
```python
import joblib

# Export pricing elasticity regressor
joblib.dump(elasticity_model, 'pricing_v1.pkl')

# Export Isolation Forest
joblib.dump(iso_forest_model, 'anomaly_v1.pkl')

# Export Forecasting ensemble (can be packaged as a dictionary or tuple)
forecasting_package = {
    'prophet_model': prophet_instance,
    'xgboost_model': xgboost_instance
}
joblib.dump(forecasting_package, 'forecast_v1.pkl')
```

---

## 4. Expected Backend Folder Structure

After exporting, copy the `.pkl` / `.joblib` files and update their accompanying `metadata.json` manifests inside the `backend/artifacts/` folder:

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

*Note: Trained `.pkl` binary files are excluded from Git via `.gitignore` to prevent repository bloat. Only templates (`metadata.example.json` and `.gitkeep`) are checked into source control.*

---

## 5. Metadata Specification

For every model artifact you export, you must create/update its matching `metadata.json` manifest. Below is the required JSON structure:

```json
{
  "model_name": "<forecasting | pricing | anomaly>",
  "model_version": "1.0.0",
  "algorithm": "Example Algorithm Name",
  "trained_on": "YYYY-MM-DD",
  "dataset": "Dataset Name/Version",
  "framework_versions": {
    "python": "3.13.7",
    "scikit-learn": "1.6.0",
    "xgboost": "2.0.3",
    "prophet": "1.1.5"
  },
  "required_features": [
    "feature_1",
    "feature_2"
  ],
  "target": "target_variable_name",
  "metrics": {
    "mae": 0.0,
    "rmse": 0.0,
    "mape": 0.0
  }
}
```

---

## 6. Checklist Before Delivery

Before turning over the artifacts, ensure you have:
1. **Google Colab Notebook**: Clean, documented notebook containing all training steps, cell outputs, and evaluation splits.
2. **Metadata Verification**: Ensure the `framework_versions` in `metadata.json` match the production backend dependencies to prevent binary incompatibility during unpickling.
3. **Accuracy Benchmarks**: Ensure all validation metrics (`mae`, `rmse`, `mape`, `r2`) are calculated and populated in the manifest.
