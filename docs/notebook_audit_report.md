# ProfitSync Notebook Audit Report
## `module3_module4_module5_combined_notebook_with_outputs.ipynb`

---

## Summary Verdict

> **The notebook is well-structured and does NOT need to be re-run from scratch.**
> However, **7 targeted fixes** are required before the output can be safely consumed by the backend.
> You do NOT need a new dataset — the existing one is sufficient.

---

## What the Notebook Currently Does (Architecture)

```
CSV Upload (Colab files.upload())
    │
    ▼
Module 3 — Preprocessor
    ├── Cleans & deduplicates (9812 rows from 10100)
    ├── Aggregates to daily per-product (3387 rows)
    ├── Builds forecasting_df (2868 rows, 52 features)
    ├── Builds pricing_df (9812 rows, 44 features)
    └── Builds anomaly_df (9812 rows, 44 features)
    │
    ▼
Module 4 — HybridDemandForecaster
    ├── Fits Prophet per product (weekly + yearly seasonality)
    ├── Computes in-sample residuals
    ├── Trains XGBoost on residuals (300 trees, depth 6)
    ├── Evaluates on 20% test split
    └── Forecasts 7d + 30d per product
    │
    ▼
Module 5 — PriceOptimizationEngine
    ├── Log-Log Ridge regression (elasticity model)
    ├── Simulates price curve (80%–120% range, 100 points)
    └── Outputs best_revenue_price and best_profit_price
    │
    ▼
JSON Output (Saved to Google Drive)
    ├── module4_response.json
    └── module5_response.json
```

---

## Issues Found — Ranked by Priority

### 🔴 CRITICAL — Must Fix (causes backend to misread or crash)

#### Issue 1: `hybrid_yhat` has negative values — 8 of 84 rows (7d), 39 of 360 rows (30d)

**Found in actual output:**
```json
{
  "product_id": "P1025",
  "ds": "2024-12-28T00:00:00",
  "hybrid_yhat": -26.271152408231615,   ← NEGATIVE — invalid for quantity
  "yhat_lower":  -61.73418102588834     ← NEGATIVE — invalid
}
```
Quantity sold can never be negative. The backend now clamps these on its side, but the model should clamp before sending to avoid confusion.

**Fix — add 2 lines in `forecast_horizon_for_product()` before the `return`:**
```python
final['hybrid_yhat'] = final['hybrid_yhat'].clip(lower=0)
final['yhat_lower']  = final['yhat_lower'].clip(lower=0)
final['yhat_upper']  = final['yhat_upper'].clip(lower=0)
```

---

#### Issue 2: Response has `product_id` per row — backend doesn't expect this

The backend calls HF once per product and already knows the product ID. Having `product_id` in each row adds noise and wastes payload size.

**Fix — remove from `forecast_horizon_for_product()` return statement:**
```python
# CHANGE THIS:
return final[[self.config.product_col, 'ds', 'yhat', 'xgb_residual', 'hybrid_yhat', 'yhat_lower', 'yhat_upper']]

# TO THIS:
return final[['ds', 'hybrid_yhat', 'yhat_lower', 'yhat_upper', 'horizon_days']]
```

---

#### Issue 3: `xgb_residual` and raw `yhat` included in response — backend doesn't use them

These are internal model internals. They inflate the JSON and confuse the contract.

**Fix — same as Issue 2, already handled by removing them from the return columns above.**

---

#### Issue 4: `summary` key included in JSON response — not part of backend contract

The `module4_response.json` has a top-level `summary` key (dataset shape info). The backend's `call_hf_api()` reads `res_data["forecast_7d"]` directly — the `summary` key is silently ignored, but it wastes bandwidth on the HF API.

**Fix — in Cell 20, remove `summary` from `module4_response`:**
```python
# REMOVE this from module4_response dict:
# 'summary': [...],      ← not needed by backend
# 'm3_shape': {...},     ← not needed by backend
# 'm4_shape': {...},     ← not needed by backend
```

---

#### Issue 5: Module 5 (Pricing) response is NOT in the format the backend expects

Current `module5_response.json` structure:
```json
{
  "metrics": { "MAE": ..., "RMSE": ..., "R2": ... },
  "elasticity": -1.82,
  "current_price": 615.0,
  "best_revenue": { "price": 490.0, "predicted_quantity": 91.2, "predicted_revenue": 44688 },
  "best_profit": { "price": 520.0, "predicted_quantity": 83.1, "predicted_profit": 12450 }
}
```

Backend expects (`pricing/inference/predict.py`):
```json
{
  "eligibility_status": "eligible",
  "eligibility_reason": null,
  "recommended_price": 490.0,
  "expected_revenue": 44688.0,
  "elasticity_model_type": "Log-Log Ridge Elasticity",
  "model_version": "1.0.0",
  "bound_range": { "min": 492.0, "max": 738.0 },
  "candidate_grid": [
    { "candidate_price": ..., "estimated_demand": ..., "estimated_revenue": ... }
  ]
}
```

**Fix — restructure `module5_response` in Cell 20:**
```python
# Build a properly-shaped pricing response
curve_df = m5['curve']
best_rev = m5['best_revenue']
current_p = float(m5['current_price'])
bound_pct = 0.20
bound_min = round(current_p * (1 - bound_pct), 2)
bound_max = round(current_p * (1 + bound_pct), 2)

# Pick 5 evenly spaced candidates from the price curve
n = len(curve_df)
indices = [0, n//4, n//2, 3*n//4, n-1]
candidate_grid = [
    {
        'candidate_price': round(curve_df.iloc[i]['price'], 2),
        'estimated_demand': round(curve_df.iloc[i]['predicted_quantity'], 2),
        'estimated_revenue': round(curve_df.iloc[i]['predicted_revenue'], 2),
    }
    for i in indices
]

module5_response = {
    'eligibility_status': 'eligible',
    'eligibility_reason': None,
    'recommended_price': round(float(best_rev['price']), 2),
    'expected_revenue': round(float(best_rev['predicted_revenue']), 2),
    'elasticity_model_type': 'Log-Log Ridge Elasticity',
    'model_version': '1.0.0',
    'bound_range': {'min': bound_min, 'max': bound_max},
    'candidate_grid': candidate_grid,
}
```

---

#### Issue 6: No Anomaly Detection output — Module 5 has no anomaly task

The backend sends 3 task types: `forecasting`, `pricing`, `anomaly`.
The notebook only produces forecasting + pricing outputs. **There is no anomaly detection module at all.**

**Fix — Add anomaly detection function to the notebook (paste at end of Cell 16 or in new cell):**
```python
def detect_anomalies_from_df(df, date_col='order_date', qty_col='quantity_sold', recent_days=7):
    """Z-score anomaly detection. Returns backend-ready JSON."""
    df = df.copy().sort_values(date_col).reset_index(drop=True)
    qty = df[qty_col].astype(float)
    mean_qty = float(qty.mean())
    std_qty  = float(qty.std()) if qty.std() > 0 else 1.0
    last_date = df[date_col].max()
    cutoff = last_date - pd.Timedelta(days=recent_days)

    flagged = []
    for _, row in df.iterrows():
        q = float(row[qty_col])
        z = (q - mean_qty) / std_qty
        if abs(z) < 2.5:
            continue
        atype = 'spike' if z > 0 else 'drop'
        stage = 'post_upload_alert' if row[date_col] >= cutoff else 'pre_forecast_historical'
        direction = 'above' if atype == 'spike' else 'below'
        explanation = (
            f"Sales quantity ({int(q)}) is {round(min(abs(z), 10), 2)} standard deviations "
            f"{direction} the historical mean ({round(mean_qty, 1)}). "
            f"{'Possible promotion or demand surge.' if atype == 'spike' else 'Possible supply disruption.'}"
        )
        flagged.append({
            'date': row[date_col].isoformat() if hasattr(row[date_col], 'isoformat') else str(row[date_col]),
            'stage': stage,
            'anomaly_type': atype,
            'severity_score': round(min(abs(z), 10.0), 2),
            'explanation': explanation,
            'acknowledged': False,
        })

    return {'model_version': '1.0.0', 'flagged_anomalies': flagged}

# Run anomaly detection
anomaly_response = detect_anomalies_from_df(
    m3['cleaned_df'],
    date_col='order_date',
    qty_col='quantity_sold'
)
print(f"Flagged {len(anomaly_response['flagged_anomalies'])} anomalies")
```

---

### 🟡 MEDIUM — Should Fix (affects accuracy and confidence)

#### Issue 7: `seasonality_mode='additive'` — should be `'multiplicative'` for retail demand

Current code:
```python
m = Prophet(..., seasonality_mode='additive', ...)
```

For retail products where demand scales with the trend (e.g., seasonal products sell 3× more during Diwali), **multiplicative** seasonality is more accurate. Additive assumes seasonal effect is a fixed number of units, not a percentage.

**Fix:**
```python
m = Prophet(..., seasonality_mode='multiplicative', ...)
```

---

#### Issue 8: MAPE = 188% — caused by zero-demand products in denominator

The current MAPE formula divides by `maximum(|actual|, 1e-6)` which is correct, but products with near-zero historical quantities still dominate the error.

**Fix — use sMAPE instead (already in the improvement guide). Add to `evaluate()`:**
```python
# Add alongside existing MAPE:
smape = float(np.mean(
    np.where(
        (np.abs(y_true) + np.abs(final_pred.values)) == 0,
        0,
        2 * np.abs(y_true - final_pred.values) / (np.abs(y_true) + np.abs(final_pred.values))
    )
) * 100)
self.metrics = {'MAE': float(mae), 'RMSE': float(rmse), 'MAPE': float(mape), 'sMAPE': float(smape)}
```

---

## What Does NOT Need Changing

| Component | Status |
|---|---|
| Module 3 data cleaning | ✅ Good — deduplication, type casting, null removal all correct |
| CSV column mapping (`unit_price_inr`, `quantity_sold`, etc.) | ✅ Correct for the dataset |
| Prophet per-product fitting loop | ✅ Architecture is correct |
| XGBoost hyperparameters (n_estimators=300, lr=0.05) | ✅ Reasonable |
| Feature engineering (lags, rolling means) | ✅ Good feature set |
| `json_safe()` serializer | ✅ Handles all numpy types correctly |
| Google Drive save paths | ✅ Correct |
| `train_test_split` (80/20) | ✅ Standard for time-series |
| Module 5 Ridge regression approach | ✅ Log-Log is correct for retail |
| Price grid simulation (100 points, ±20%) | ✅ Good resolution |

---

## Do You Need to Re-Run the Model?

**No — you do NOT need to re-run the entire notebook.**

You only need to:

1. Apply the 6 code fixes listed above
2. Re-run **Cell 20 only** (the JSON save cell) to regenerate the output JSONs with the correct schema
3. The anomaly detection function can be added and run as a new cell at the end

**You do NOT need:**
- A new dataset — existing one works fine
- To re-train Prophet or XGBoost — models are already trained
- To re-run Module 3 — preprocessing is already done

---

## Summary Fix Checklist

```
Cell 14 — forecast_horizon_for_product():
[ ] Add: final['hybrid_yhat'] = final['hybrid_yhat'].clip(lower=0)
[ ] Add: final['yhat_lower']  = final['yhat_lower'].clip(lower=0)
[ ] Add: final['yhat_upper']  = final['yhat_upper'].clip(lower=0)
[ ] Change return to only include: ds, hybrid_yhat, yhat_lower, yhat_upper, horizon_days

Cell 14 — fit_prophet_per_product():
[ ] Change: seasonality_mode='additive' → seasonality_mode='multiplicative'

Cell 14 — evaluate():
[ ] Add sMAPE calculation alongside MAPE

Cell 16 (new cell) — Anomaly detection:
[ ] Add detect_anomalies_from_df() function
[ ] Run it and save anomaly_response as JSON

Cell 20 — JSON response builder:
[ ] Remove 'summary', 'm3_shape', 'm4_shape' from module4_response
[ ] Restructure module5_response to match backend contract
[ ] Add anomaly JSON save
```

---

## Backend Compatibility After Fixes

| Task | Before Fixes | After Fixes |
|---|---|---|
| Forecasting | ⚠️ Field names OK (backend updated), negatives present | ✅ Clean, clamped, correct schema |
| Pricing | ❌ Wrong schema — backend cannot parse | ✅ Matches backend contract exactly |
| Anomaly | ❌ No output at all | ✅ Implemented with correct schema |
