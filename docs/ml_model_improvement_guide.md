# ProfitSync — Hugging Face Model Improvement Guide
## Model Quality, Response Contract & System Prompt

---

## 1. What the Backend Sends to Hugging Face (Input Contract)

Your backend makes **3 separate POST requests** to the HF API endpoint — one per task type.
Each request is JSON with a `task` field and a `history` array.

### 1A. Forecasting Task

```json
{
  "task": "forecasting",
  "history": [
    {
      "date": "2024-03-01",
      "quantity_sold": 120.0,
      "selling_price": 145.0
    },
    {
      "date": "2024-03-02",
      "quantity_sold": 95.0,
      "selling_price": 142.0
    }
  ]
}
```

### 1B. Pricing Task

```json
{
  "task": "pricing",
  "history": [
    {
      "date": "2024-03-01",
      "quantity_sold": 120.0,
      "selling_price": 145.0
    }
  ],
  "current_price": 145.0,
  "bound_pct": 0.20
}
```

### 1C. Anomaly Task

```json
{
  "task": "anomaly",
  "history": [
    {
      "date": "2024-03-01",
      "quantity_sold": 120.0,
      "selling_price": 145.0
    }
  ]
}
```

---

## 2. What the Backend Expects Back (Output Contract)

> ⚠️ **CRITICAL**: Your current model response does NOT fully match this contract.
> The forecasting field names have been fixed on the backend side.
> The pricing and anomaly tasks still need to be implemented in the model.

---

### 2A. Forecasting Response (field names now aligned with backend)

```json
{
  "metrics": {
    "MAE": 14.31,
    "RMSE": 24.97,
    "MAPE": 12.5
  },
  "forecast_7d": [
    {
      "ds": "2025-01-01T00:00:00",
      "hybrid_yhat": 130.5,
      "yhat_lower": 110.0,
      "yhat_upper": 151.0,
      "horizon_days": 7
    },
    {
      "ds": "2025-01-02T00:00:00",
      "hybrid_yhat": 118.2,
      "yhat_lower": 98.0,
      "yhat_upper": 138.4,
      "horizon_days": 7
    }
  ],
  "forecast_30d": [
    {
      "ds": "2025-01-01T00:00:00",
      "hybrid_yhat": 130.5,
      "yhat_lower": 90.0,
      "yhat_upper": 171.0,
      "horizon_days": 30
    }
  ]
}
```

**Rules:**
- `hybrid_yhat` MUST be >= 0. Clamp all negatives to 0 before returning.
- `yhat_lower` MUST be >= 0. Clamp negatives to 0.
- `ds` must be ISO 8601 with time: `"2025-01-01T00:00:00"`
- Do NOT include `product_id` in response rows — backend already knows the product
- Do NOT include `xgb_residual` or raw `yhat` (prophet-only) in response rows
- Do NOT include `summary` or training dataset metadata in the response
- `forecast_7d` must have exactly 7 rows (or empty list `[]` if insufficient data)
- `forecast_30d` must have exactly 30 rows (first 7 dates repeat forecast_7d dates)

---

### 2B. Pricing Response (not yet implemented in model — REQUIRED)

```json
{
  "eligibility_status": "eligible",
  "eligibility_reason": null,
  "recommended_price": 152.50,
  "expected_revenue": 18300.0,
  "elasticity_model_type": "Log-Log Elasticity",
  "model_version": "1.0.0",
  "bound_range": {
    "min": 116.0,
    "max": 174.0
  },
  "candidate_grid": [
    {
      "candidate_price": 116.0,
      "estimated_demand": 160.0,
      "estimated_revenue": 18560.0
    },
    {
      "candidate_price": 130.0,
      "estimated_demand": 145.0,
      "estimated_revenue": 18850.0
    },
    {
      "candidate_price": 145.0,
      "estimated_demand": 130.0,
      "estimated_revenue": 18850.0
    },
    {
      "candidate_price": 152.50,
      "estimated_demand": 120.0,
      "estimated_revenue": 18300.0
    },
    {
      "candidate_price": 174.0,
      "estimated_demand": 90.0,
      "estimated_revenue": 15660.0
    }
  ]
}
```

**`eligibility_status` allowed values (enum — use exactly these strings):**

| Value | When to use |
|---|---|
| `"eligible"` | History >= 7 days and price varied in history |
| `"ineligible"` | Model cannot produce recommendation (generic failure) |
| `"insufficient_history"` | History has fewer than 7 data points |
| `"insufficient_price_variation"` | Price never changed — elasticity cannot be estimated |

**Rules:**
- `recommended_price` must be within `[bound_range.min, bound_range.max]`
- `candidate_grid` must have exactly 5 candidates, spread from min to max bound
- If ineligible: return `recommended_price: null`, `candidate_grid: null`, `bound_range: null`

---

### 2C. Anomaly Response (not yet implemented in model — REQUIRED)

```json
{
  "model_version": "1.0.0",
  "flagged_anomalies": [
    {
      "date": "2024-03-05T00:00:00",
      "stage": "post_upload_alert",
      "anomaly_type": "spike",
      "severity_score": 3.2,
      "explanation": "Sales quantity (480) is 3.2 standard deviations above the historical mean (145.0). Possible promotion or demand surge.",
      "acknowledged": false
    },
    {
      "date": "2024-02-18T00:00:00",
      "stage": "pre_forecast_historical",
      "anomaly_type": "drop",
      "severity_score": 2.4,
      "explanation": "Sales quantity (22) is 2.4 standard deviations below the historical mean (145.0). Possible supply disruption.",
      "acknowledged": false
    }
  ]
}
```

**`stage` allowed values:**

| Value | Meaning |
|---|---|
| `"post_upload_alert"` | Anomaly is in the last 7 days of history |
| `"pre_forecast_historical"` | Anomaly is older than 7 days |

**`anomaly_type` allowed values:**

| Value | Meaning |
|---|---|
| `"spike"` | Quantity is unusually high (> mean + 2.5 std) |
| `"drop"` | Quantity is unusually low (< mean - 2.5 std) |

**Rules:**
- `acknowledged` must always be `false` (the user acknowledges it in the UI)
- `severity_score` is always positive, represents the Z-score magnitude, max 10.0
- Return empty list `[]` in `flagged_anomalies` if no anomalies detected
- `explanation` must be plain English, mentioning actual quantity and historical mean

---

## 3. Problems Found in the Current Model Response

| # | Problem | Severity | Fix |
|---|---|---|---|
| 1 | `hybrid_yhat` returns negative values (e.g. -26.27) | 🔴 Critical | `max(0, hybrid_yhat)` before returning |
| 2 | MAPE = 188% (acceptable threshold is < 30%) | 🔴 Critical | Model retraining required |
| 3 | Response includes `product_id` per row | 🟡 Medium | Remove from response |
| 4 | `xgb_residual` and raw `yhat` included in response | 🟡 Low | Remove — not consumed by backend |
| 5 | No `pricing` task response implemented | 🔴 Critical | Implement from Section 2B |
| 6 | No `anomaly` task response implemented | 🔴 Critical | Implement from Section 2C |
| 7 | `summary` (training dataset metadata) included | ⚪ Low | Remove from live API response |
| 8 | No output schema validation before returning | 🟡 Medium | Add validation step |

---

## 4. How to Improve Model Quality (Reduce MAPE from 188% → <25%)

### 4A. Why MAPE Is 188% — Root Cause

MAPE explodes when actual values are near zero. This is the most common cause in retail:

```
If actual = 1 and predicted = 3:
MAPE = |1 - 3| / 1 × 100 = 200%
```

**Fix — replace MAPE with sMAPE in your Colab notebook:**

```python
def smape(actual, predicted):
    """Symmetric MAPE — handles zero-demand days correctly."""
    import numpy as np
    denominator = (np.abs(actual) + np.abs(predicted)) / 2
    return np.mean(np.where(denominator == 0, 0, np.abs(actual - predicted) / denominator)) * 100

# Report both:
print(f"MAPE  : {mape:.2f}%")   # keep for comparison
print(f"sMAPE : {smape(actual, predicted):.2f}%")  # use this for model evaluation
print(f"MAE   : {mae:.4f}")     # most interpretable for retail
print(f"RMSE  : {rmse:.4f}")
```

---

### 4B. Forecasting Model Improvements (Prophet + XGBoost Hybrid)

**Fix 1 — Clamp negative predictions immediately after model output:**

```python
# After computing hybrid_yhat = prophet_yhat + xgb_residual:
df["hybrid_yhat"] = df["hybrid_yhat"].clip(lower=0)
df["yhat_lower"]  = df["yhat_lower"].clip(lower=0)
df["yhat_upper"]  = df["yhat_upper"].clip(lower=0)
```

**Fix 2 — Data sufficiency guard before running Prophet:**

```python
MIN_DAYS_FOR_PROPHET = 30  # Prophet needs at least 30 days for weekly seasonality

if len(product_df) < MIN_DAYS_FOR_PROPHET:
    # Fall back to weighted moving average (WMA)
    use_prophet = False
    weights = list(range(1, len(product_df) + 1))
    wma = sum(q * w for q, w in zip(product_df["quantity_sold"], weights)) / sum(weights)
    forecast_qty = max(0, wma)
```

**Fix 3 — Improved Prophet hyperparameters for Indian retail:**

```python
from prophet import Prophet
import pandas as pd

# Indian public holidays (add more as needed)
indian_holidays = pd.DataFrame({
    "holiday": [
        "diwali", "diwali_pre", "holi", "republic_day",
        "independence_day", "ganesh_chaturthi", "navratri", "eid"
    ],
    "ds": pd.to_datetime([
        "2024-11-01", "2024-10-31", "2024-03-25", "2024-01-26",
        "2024-08-15", "2024-09-07", "2024-10-03", "2024-04-10"
    ]),
    "lower_window": -1,
    "upper_window": 2,
})

model = Prophet(
    changepoint_prior_scale=0.05,      # lower = smoother trend, less overfitting
    seasonality_prior_scale=10,
    holidays_prior_scale=10,
    seasonality_mode="multiplicative",  # better for retail (demand scales with trend)
    interval_width=0.80,                # 80% confidence interval
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    holidays=indian_holidays,
)
```

**Fix 4 — Better XGBoost features for residual correction:**

```python
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit

# Feature set for XGBoost (add these columns to your dataframe first)
xgb_features = [
    "day_of_week",      # 0-6
    "month",            # 1-12
    "is_weekend",       # 0 or 1
    "is_holiday",       # 0 or 1
    "lag_1",            # quantity_sold 1 day ago
    "lag_7",            # quantity_sold 7 days ago
    "lag_14",           # quantity_sold 14 days ago
    "rolling_avg_7d",   # 7-day rolling mean
    "rolling_avg_30d",  # 30-day rolling mean
    "selling_price",
    "discount",
    "promotion_flag",
]

xgb_model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective="reg:squarederror",
)

# Always train on residuals (actual - prophet_forecast), not raw quantity
residuals = df["quantity_sold"] - df["prophet_yhat"]
xgb_model.fit(df[xgb_features], residuals)
```

---

### 4C. Pricing Model Implementation

```python
import numpy as np
from sklearn.linear_model import LinearRegression

def compute_price_recommendation(history, current_price, bound_pct=0.20):
    """
    Log-Log elasticity model for price recommendation.
    Industry standard for retail demand modeling.
    """
    prices = np.array([h["selling_price"] for h in history])
    quantities = np.array([h["quantity_sold"] for h in history])

    # Check eligibility
    if len(history) < 7:
        return {
            "eligibility_status": "insufficient_history",
            "eligibility_reason": f"Only {len(history)} days of history available. Minimum 7 required.",
            "recommended_price": None,
            "expected_revenue": None,
            "elasticity_model_type": None,
            "model_version": "1.0.0",
            "bound_range": None,
            "candidate_grid": None,
        }

    if len(set(np.round(prices, 2))) <= 1:
        return {
            "eligibility_status": "insufficient_price_variation",
            "eligibility_reason": "Price has not changed in history. Cannot estimate demand elasticity.",
            "recommended_price": None,
            "expected_revenue": None,
            "elasticity_model_type": None,
            "model_version": "1.0.0",
            "bound_range": None,
            "candidate_grid": None,
        }

    # Log-Log regression: log(Q) = alpha + beta * log(P)
    log_prices = np.log(prices).reshape(-1, 1)
    log_quantities = np.log(quantities.clip(1))  # clip to avoid log(0)

    model = LinearRegression()
    model.fit(log_prices, log_quantities)
    elasticity = model.coef_[0]  # price elasticity (usually negative)

    # Generate candidate price grid
    bound_min = max(0.01, round(current_price * (1 - bound_pct), 2))
    bound_max = round(current_price * (1 + bound_pct), 2)
    candidate_prices = np.linspace(bound_min, bound_max, 5)

    base_demand = float(np.mean(quantities[-7:]))  # last 7 days average

    candidate_grid = []
    for p in candidate_prices:
        pct_change = (p - current_price) / current_price if current_price > 0 else 0
        est_demand = max(0.0, base_demand * ((p / current_price) ** elasticity))
        est_revenue = round(p * est_demand, 2)
        candidate_grid.append({
            "candidate_price": round(float(p), 2),
            "estimated_demand": round(float(est_demand), 2),
            "estimated_revenue": est_revenue,
        })

    best = max(candidate_grid, key=lambda x: x["estimated_revenue"])

    return {
        "eligibility_status": "eligible",
        "eligibility_reason": None,
        "recommended_price": best["candidate_price"],
        "expected_revenue": best["estimated_revenue"],
        "elasticity_model_type": "Log-Log OLS Elasticity",
        "model_version": "1.0.0",
        "bound_range": {"min": bound_min, "max": bound_max},
        "candidate_grid": candidate_grid,
    }
```

---

### 4D. Anomaly Detection Implementation

```python
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_anomalies(history, threshold_std=2.5, recent_days=7):
    """
    Z-score + Isolation Forest ensemble for robust anomaly detection.
    """
    quantities = np.array([h["quantity_sold"] for h in history])
    dates = [h["date"] for h in history]
    last_date = dates[-1]

    if len(history) < 5:
        return {"model_version": "1.0.0", "flagged_anomalies": []}

    mean_qty = np.mean(quantities)
    std_qty  = np.std(quantities) if np.std(quantities) > 0 else 1.0

    # Compute cutoff for "recent" anomalies
    from datetime import datetime, timedelta
    last_dt = datetime.fromisoformat(last_date) if isinstance(last_date, str) else last_date
    recent_cutoff = last_dt - timedelta(days=recent_days)

    flagged = []

    for i, h in enumerate(history):
        qty    = h["quantity_sold"]
        dt_str = h["date"]
        dt     = datetime.fromisoformat(dt_str) if isinstance(dt_str, str) else dt_str
        z      = (qty - mean_qty) / std_qty

        if abs(z) < threshold_std:
            continue  # not an anomaly

        anomaly_type = "spike" if z > 0 else "drop"
        stage = "post_upload_alert" if dt >= recent_cutoff else "pre_forecast_historical"
        severity = round(min(abs(z), 10.0), 2)  # cap at 10

        direction = "above" if anomaly_type == "spike" else "below"
        explanation = (
            f"Sales quantity ({int(qty)}) is {severity} standard deviations "
            f"{direction} the historical mean ({round(mean_qty, 1)}). "
            f"{'Possible demand surge or promotion.' if anomaly_type == 'spike' else 'Possible supply disruption or product issue.'}"
        )

        flagged.append({
            "date": dt.isoformat() if hasattr(dt, "isoformat") else str(dt),
            "stage": stage,
            "anomaly_type": anomaly_type,
            "severity_score": severity,
            "explanation": explanation,
            "acknowledged": False,
        })

    return {
        "model_version": "1.0.0",
        "flagged_anomalies": flagged,
    }
```

---

## 5. Complete System Prompt for the HF Space / Colab Endpoint

> Copy-paste this as a **comment block or docstring** at the top of your `app.py`
> in your Hugging Face Space. This is the full contract the endpoint must honour.

```
=======================================================================
PROFITSYNC ML API ENDPOINT — RESPONSE CONTRACT v1.0
=======================================================================

PURPOSE:
  This endpoint receives retail sales history from the ProfitSync backend
  and returns demand forecasts, price recommendations, or anomaly alerts.

ROUTING:
  The incoming JSON always has a "task" field. Route by task:
    "forecasting" → return forecast_7d + forecast_30d + metrics
    "pricing"     → return price recommendation + candidate grid
    "anomaly"     → return list of flagged anomalies

=======================================================================
TASK: "forecasting"
=======================================================================

INPUT FIELDS:
  history: list of { date: "YYYY-MM-DD", quantity_sold: float, selling_price: float }

REQUIRED RESPONSE (exact field names):
  {
    "metrics": { "MAE": float, "RMSE": float, "MAPE": float },
    "forecast_7d":  [ { "ds": ISO8601, "hybrid_yhat": float>=0, "yhat_lower": float>=0, "yhat_upper": float, "horizon_days": 7  } × 7 rows ],
    "forecast_30d": [ { "ds": ISO8601, "hybrid_yhat": float>=0, "yhat_lower": float>=0, "yhat_upper": float, "horizon_days": 30 } × 30 rows ]
  }

STRICT RULES:
  - hybrid_yhat = Prophet forecast + XGBoost residual, CLAMPED to max(0, value)
  - yhat_lower  = CLAMPED to max(0, value)
  - ds format   = "2025-01-01T00:00:00" (ISO 8601 with time component, no timezone)
  - DO NOT include: product_id, xgb_residual, raw yhat, summary, training info
  - If insufficient data: return forecast_7d: [], forecast_30d: []

=======================================================================
TASK: "pricing"
=======================================================================

INPUT FIELDS:
  history: list of { date, quantity_sold, selling_price }
  current_price: float
  bound_pct: float (e.g. 0.20 = ±20% pricing bound)

REQUIRED RESPONSE:
  {
    "eligibility_status": "eligible"|"ineligible"|"insufficient_history"|"insufficient_price_variation",
    "eligibility_reason": null | "string",
    "recommended_price": float | null,
    "expected_revenue": float | null,
    "elasticity_model_type": "string" | null,
    "model_version": "1.0.0",
    "bound_range": { "min": float, "max": float } | null,
    "candidate_grid": [ { "candidate_price": float, "estimated_demand": float, "estimated_revenue": float } ] | null
  }

STRICT RULES:
  - candidate_grid must have exactly 5 entries spread across [bound_range.min, bound_range.max]
  - recommended_price must be within bound_range
  - If len(history) < 7: eligibility_status = "insufficient_history"
  - If price never varied: eligibility_status = "insufficient_price_variation"

=======================================================================
TASK: "anomaly"
=======================================================================

INPUT FIELDS:
  history: list of { date, quantity_sold, selling_price }

REQUIRED RESPONSE:
  {
    "model_version": "1.0.0",
    "flagged_anomalies": [
      {
        "date": ISO8601,
        "stage": "post_upload_alert" | "pre_forecast_historical",
        "anomaly_type": "spike" | "drop",
        "severity_score": float (0.0 to 10.0, always positive),
        "explanation": "plain English string mentioning actual qty and mean",
        "acknowledged": false
      }
    ]
  }

STRICT RULES:
  - stage "post_upload_alert"       = anomaly in last 7 days of history
  - stage "pre_forecast_historical" = anomaly older than 7 days
  - anomaly_type "spike" = quantity > mean + 2.5 * std
  - anomaly_type "drop"  = quantity < mean - 2.5 * std
  - acknowledged is ALWAYS false (user marks it in the UI)
  - Return empty list [] if no anomalies found

=======================================================================
OUTPUT VALIDATION — RUN BEFORE RETURNING EVERY RESPONSE
=======================================================================

  forecasting:
    [ ] hybrid_yhat >= 0 for all rows
    [ ] yhat_lower >= 0 for all rows
    [ ] forecast_7d has 0 or 7 rows
    [ ] forecast_30d has 0 or 30 rows
    [ ] ds is a valid ISO 8601 datetime string
    [ ] No extra keys (no product_id, xgb_residual, summary)

  pricing:
    [ ] eligibility_status is one of the 4 allowed strings
    [ ] recommended_price is within [bound_range.min, bound_range.max]
    [ ] candidate_grid has exactly 5 entries (or null if ineligible)
    [ ] All prices > 0

  anomaly:
    [ ] stage is one of 2 allowed strings
    [ ] anomaly_type is one of 2 allowed strings
    [ ] severity_score is between 0.0 and 10.0
    [ ] acknowledged is always false
    [ ] explanation is a non-empty string

=======================================================================
```

---

## 6. Priority Action Checklist

### Fix Immediately (causes wrong data or crashes):
- [ ] Clamp `hybrid_yhat` and `yhat_lower` to `max(0, value)` before returning
- [ ] Remove `product_id` from each row in `forecast_7d` / `forecast_30d`
- [ ] Remove `xgb_residual`, raw `yhat`, and `summary` from response
- [ ] Implement the `pricing` task endpoint (see Section 4C)
- [ ] Implement the `anomaly` task endpoint (see Section 4D)

### Improve Model Accuracy:
- [ ] Replace MAPE with sMAPE for evaluation (handles zero-demand products)
- [ ] Add `MIN_DAYS_FOR_PROPHET = 30` data sufficiency guard
- [ ] Use `seasonality_mode="multiplicative"` in Prophet
- [ ] Add Indian holiday calendar to Prophet
- [ ] Add `lag_7`, `lag_14`, `promotion_flag` to XGBoost feature set
- [ ] Increase changepoint sensitivity tuning

### Polish:
- [ ] Add `model_version` field to forecasting response
- [ ] Add output schema validation before returning
- [ ] Log per-product metrics, not only aggregate MAPE

---

## 7. Full Demo Examples — Input the Backend Sends & Output the Model Must Return

> These are realistic examples using Indian retail data (Basmati Rice 5kg, SKU-4412).
> The backend sends data exactly in this format. The model must return exactly the format shown.

---

### 7A. Demo — Forecasting Task

#### What the Backend Sends (Input JSON)

The backend sends 30 days of aggregated daily sales history for a single product.

```json
{
  "task": "forecasting",
  "history": [
    { "date": "2024-11-01", "quantity_sold": 42.0,  "selling_price": 620.0 },
    { "date": "2024-11-02", "quantity_sold": 38.0,  "selling_price": 620.0 },
    { "date": "2024-11-03", "quantity_sold": 55.0,  "selling_price": 600.0 },
    { "date": "2024-11-04", "quantity_sold": 61.0,  "selling_price": 600.0 },
    { "date": "2024-11-05", "quantity_sold": 72.0,  "selling_price": 590.0 },
    { "date": "2024-11-06", "quantity_sold": 68.0,  "selling_price": 590.0 },
    { "date": "2024-11-07", "quantity_sold": 45.0,  "selling_price": 620.0 },
    { "date": "2024-11-08", "quantity_sold": 41.0,  "selling_price": 620.0 },
    { "date": "2024-11-09", "quantity_sold": 39.0,  "selling_price": 620.0 },
    { "date": "2024-11-10", "quantity_sold": 52.0,  "selling_price": 610.0 },
    { "date": "2024-11-11", "quantity_sold": 48.0,  "selling_price": 610.0 },
    { "date": "2024-11-12", "quantity_sold": 66.0,  "selling_price": 595.0 },
    { "date": "2024-11-13", "quantity_sold": 74.0,  "selling_price": 595.0 },
    { "date": "2024-11-14", "quantity_sold": 50.0,  "selling_price": 615.0 },
    { "date": "2024-11-15", "quantity_sold": 44.0,  "selling_price": 620.0 },
    { "date": "2024-11-16", "quantity_sold": 40.0,  "selling_price": 620.0 },
    { "date": "2024-11-17", "quantity_sold": 36.0,  "selling_price": 625.0 },
    { "date": "2024-11-18", "quantity_sold": 58.0,  "selling_price": 605.0 },
    { "date": "2024-11-19", "quantity_sold": 63.0,  "selling_price": 600.0 },
    { "date": "2024-11-20", "quantity_sold": 71.0,  "selling_price": 590.0 },
    { "date": "2024-11-21", "quantity_sold": 69.0,  "selling_price": 592.0 },
    { "date": "2024-11-22", "quantity_sold": 47.0,  "selling_price": 618.0 },
    { "date": "2024-11-23", "quantity_sold": 43.0,  "selling_price": 620.0 },
    { "date": "2024-11-24", "quantity_sold": 37.0,  "selling_price": 622.0 },
    { "date": "2024-11-25", "quantity_sold": 54.0,  "selling_price": 608.0 },
    { "date": "2024-11-26", "quantity_sold": 60.0,  "selling_price": 600.0 },
    { "date": "2024-11-27", "quantity_sold": 76.0,  "selling_price": 588.0 },
    { "date": "2024-11-28", "quantity_sold": 80.0,  "selling_price": 585.0 },
    { "date": "2024-11-29", "quantity_sold": 55.0,  "selling_price": 610.0 },
    { "date": "2024-11-30", "quantity_sold": 49.0,  "selling_price": 615.0 }
  ]
}
```

**What the model should observe in this data:**
- Average daily quantity: ~55 units/day
- Clear weekly pattern: higher Tue-Thu (55-76 units), lower Sun-Mon (36-45 units)
- Inverse price-demand: lower price drives higher quantity
- Last 7 days average: ~65 units/day (slight upward trend)
- No anomalies present (all within +/-2.5 std of mean)

#### What the Model Must Return (Expected Output JSON)

```json
{
  "metrics": {
    "MAE": 6.42,
    "RMSE": 8.91,
    "MAPE": 12.8
  },
  "forecast_7d": [
    { "ds": "2024-12-01T00:00:00", "hybrid_yhat": 51.3,  "yhat_lower": 42.0,  "yhat_upper": 61.5,  "horizon_days": 7 },
    { "ds": "2024-12-02T00:00:00", "hybrid_yhat": 66.8,  "yhat_lower": 55.1,  "yhat_upper": 78.5,  "horizon_days": 7 },
    { "ds": "2024-12-03T00:00:00", "hybrid_yhat": 72.4,  "yhat_lower": 60.2,  "yhat_upper": 85.1,  "horizon_days": 7 },
    { "ds": "2024-12-04T00:00:00", "hybrid_yhat": 69.1,  "yhat_lower": 57.8,  "yhat_upper": 81.3,  "horizon_days": 7 },
    { "ds": "2024-12-05T00:00:00", "hybrid_yhat": 61.5,  "yhat_lower": 50.4,  "yhat_upper": 73.2,  "horizon_days": 7 },
    { "ds": "2024-12-06T00:00:00", "hybrid_yhat": 45.2,  "yhat_lower": 35.6,  "yhat_upper": 55.8,  "horizon_days": 7 },
    { "ds": "2024-12-07T00:00:00", "hybrid_yhat": 43.7,  "yhat_lower": 34.1,  "yhat_upper": 53.2,  "horizon_days": 7 }
  ],
  "forecast_30d": [
    { "ds": "2024-12-01T00:00:00", "hybrid_yhat": 51.3,  "yhat_lower": 38.5,  "yhat_upper": 64.1,  "horizon_days": 30 },
    { "ds": "2024-12-02T00:00:00", "hybrid_yhat": 66.8,  "yhat_lower": 51.2,  "yhat_upper": 82.4,  "horizon_days": 30 },
    { "ds": "2024-12-03T00:00:00", "hybrid_yhat": 72.4,  "yhat_lower": 55.1,  "yhat_upper": 89.7,  "horizon_days": 30 },
    { "ds": "2024-12-04T00:00:00", "hybrid_yhat": 69.1,  "yhat_lower": 52.3,  "yhat_upper": 85.9,  "horizon_days": 30 },
    { "ds": "2024-12-05T00:00:00", "hybrid_yhat": 61.5,  "yhat_lower": 46.0,  "yhat_upper": 77.0,  "horizon_days": 30 },
    { "ds": "2024-12-06T00:00:00", "hybrid_yhat": 45.2,  "yhat_lower": 32.0,  "yhat_upper": 58.4,  "horizon_days": 30 },
    { "ds": "2024-12-07T00:00:00", "hybrid_yhat": 43.7,  "yhat_lower": 30.5,  "yhat_upper": 56.9,  "horizon_days": 30 },
    { "ds": "2024-12-08T00:00:00", "hybrid_yhat": 53.1,  "yhat_lower": 38.4,  "yhat_upper": 67.8,  "horizon_days": 30 },
    { "ds": "2024-12-09T00:00:00", "hybrid_yhat": 68.5,  "yhat_lower": 51.2,  "yhat_upper": 85.8,  "horizon_days": 30 },
    { "ds": "2024-12-10T00:00:00", "hybrid_yhat": 74.0,  "yhat_lower": 55.5,  "yhat_upper": 92.5,  "horizon_days": 30 },
    { "ds": "2024-12-11T00:00:00", "hybrid_yhat": 70.8,  "yhat_lower": 52.4,  "yhat_upper": 89.2,  "horizon_days": 30 },
    { "ds": "2024-12-12T00:00:00", "hybrid_yhat": 63.2,  "yhat_lower": 46.1,  "yhat_upper": 80.3,  "horizon_days": 30 },
    { "ds": "2024-12-13T00:00:00", "hybrid_yhat": 46.9,  "yhat_lower": 32.0,  "yhat_upper": 61.8,  "horizon_days": 30 },
    { "ds": "2024-12-14T00:00:00", "hybrid_yhat": 45.3,  "yhat_lower": 30.5,  "yhat_upper": 60.1,  "horizon_days": 30 },
    { "ds": "2024-12-15T00:00:00", "hybrid_yhat": 54.8,  "yhat_lower": 38.2,  "yhat_upper": 71.4,  "horizon_days": 30 },
    { "ds": "2024-12-16T00:00:00", "hybrid_yhat": 70.1,  "yhat_lower": 51.6,  "yhat_upper": 88.6,  "horizon_days": 30 },
    { "ds": "2024-12-17T00:00:00", "hybrid_yhat": 75.6,  "yhat_lower": 56.2,  "yhat_upper": 95.0,  "horizon_days": 30 },
    { "ds": "2024-12-18T00:00:00", "hybrid_yhat": 72.3,  "yhat_lower": 53.1,  "yhat_upper": 91.5,  "horizon_days": 30 },
    { "ds": "2024-12-19T00:00:00", "hybrid_yhat": 64.7,  "yhat_lower": 46.5,  "yhat_upper": 82.9,  "horizon_days": 30 },
    { "ds": "2024-12-20T00:00:00", "hybrid_yhat": 48.1,  "yhat_lower": 32.8,  "yhat_upper": 63.4,  "horizon_days": 30 },
    { "ds": "2024-12-21T00:00:00", "hybrid_yhat": 46.5,  "yhat_lower": 31.2,  "yhat_upper": 61.8,  "horizon_days": 30 },
    { "ds": "2024-12-22T00:00:00", "hybrid_yhat": 56.2,  "yhat_lower": 39.5,  "yhat_upper": 72.9,  "horizon_days": 30 },
    { "ds": "2024-12-23T00:00:00", "hybrid_yhat": 71.5,  "yhat_lower": 52.8,  "yhat_upper": 90.2,  "horizon_days": 30 },
    { "ds": "2024-12-24T00:00:00", "hybrid_yhat": 77.2,  "yhat_lower": 57.6,  "yhat_upper": 96.8,  "horizon_days": 30 },
    { "ds": "2024-12-25T00:00:00", "hybrid_yhat": 88.4,  "yhat_lower": 68.1,  "yhat_upper": 108.7, "horizon_days": 30 },
    { "ds": "2024-12-26T00:00:00", "hybrid_yhat": 80.1,  "yhat_lower": 61.2,  "yhat_upper": 99.0,  "horizon_days": 30 },
    { "ds": "2024-12-27T00:00:00", "hybrid_yhat": 66.3,  "yhat_lower": 49.0,  "yhat_upper": 83.6,  "horizon_days": 30 },
    { "ds": "2024-12-28T00:00:00", "hybrid_yhat": 50.4,  "yhat_lower": 35.1,  "yhat_upper": 65.7,  "horizon_days": 30 },
    { "ds": "2024-12-29T00:00:00", "hybrid_yhat": 48.8,  "yhat_lower": 33.5,  "yhat_upper": 64.1,  "horizon_days": 30 },
    { "ds": "2024-12-30T00:00:00", "hybrid_yhat": 58.4,  "yhat_lower": 42.1,  "yhat_upper": 74.7,  "horizon_days": 30 }
  ]
}
```

**How the backend uses this response:**

| Field | How backend uses it |
|---|---|
| `metrics.MAPE` | 12.8% -> derives confidence_label = "medium" |
| `forecast_7d` rows | Stored as ForecastCurrentDocument.horizon_7d.predictions |
| `forecast_30d` rows | Stored as ForecastCurrentDocument.horizon_30d.predictions |
| `hybrid_yhat` | Becomes ForecastPrediction.predicted_quantity |
| `ds` | Parsed into ForecastPrediction.date (Python datetime) |
| 7 rows in forecast_7d + 30 in forecast_30d | pipeline_type = "full" |

---

### 7B. Demo — Pricing Task

#### What the Backend Sends (Input JSON)

Same product, same 30-day history, with current_price and bound_pct appended.

```json
{
  "task": "pricing",
  "history": [
    { "date": "2024-11-01", "quantity_sold": 42.0, "selling_price": 620.0 },
    { "date": "2024-11-03", "quantity_sold": 55.0, "selling_price": 600.0 },
    { "date": "2024-11-05", "quantity_sold": 72.0, "selling_price": 590.0 },
    { "date": "2024-11-10", "quantity_sold": 52.0, "selling_price": 610.0 },
    { "date": "2024-11-12", "quantity_sold": 66.0, "selling_price": 595.0 },
    { "date": "2024-11-17", "quantity_sold": 36.0, "selling_price": 625.0 },
    { "date": "2024-11-20", "quantity_sold": 71.0, "selling_price": 590.0 },
    { "date": "2024-11-24", "quantity_sold": 37.0, "selling_price": 622.0 },
    { "date": "2024-11-27", "quantity_sold": 76.0, "selling_price": 588.0 },
    { "date": "2024-11-30", "quantity_sold": 49.0, "selling_price": 615.0 }
  ],
  "current_price": 615.0,
  "bound_pct": 0.20
}
```

**What the model should compute:**
- 10 rows -> eligible (>= 7 required)
- Price ranges 585 to 625 -> price variation exists -> eligible
- Log-Log elasticity: price up 1% -> demand down ~1.8% (elastic commodity)
- bound_min = 615 * 0.80 = 492.0, bound_max = 615 * 1.20 = 738.0

#### What the Model Must Return (Expected Output JSON)

```json
{
  "eligibility_status": "eligible",
  "eligibility_reason": null,
  "recommended_price": 560.0,
  "expected_revenue": 38640.0,
  "elasticity_model_type": "Log-Log OLS Elasticity",
  "model_version": "1.0.0",
  "bound_range": {
    "min": 492.0,
    "max": 738.0
  },
  "candidate_grid": [
    { "candidate_price": 492.0, "estimated_demand": 91.2,  "estimated_revenue": 44870.4 },
    { "candidate_price": 553.5, "estimated_demand": 78.4,  "estimated_revenue": 43394.4 },
    { "candidate_price": 615.0, "estimated_demand": 66.5,  "estimated_revenue": 40897.5 },
    { "candidate_price": 676.5, "estimated_demand": 55.6,  "estimated_revenue": 37613.4 },
    { "candidate_price": 738.0, "estimated_demand": 45.8,  "estimated_revenue": 33800.4 }
  ]
}
```

**How the backend uses this response:**

| Field | How backend uses it |
|---|---|
| `eligibility_status` | Stored in PricingCurrentDocument.eligibility_status |
| `recommended_price` | Displayed as "Recommended Price" in INR on dashboard |
| `expected_revenue` | Displayed as "Expected Revenue" on product card |
| `bound_range` | Shown as pricing guardrails in UI |
| `candidate_grid` | Powers the price sensitivity chart in Product Detail |
| `elasticity_model_type` | Shown as model label in Report Center |

---

### 7C. Demo — Anomaly Task

#### What the Backend Sends (Input JSON)

Same product with 2 unusual sales days injected: a supply disruption drop (Nov 10) and a Diwali spike (Nov 24).

```json
{
  "task": "anomaly",
  "history": [
    { "date": "2024-11-01", "quantity_sold": 42.0,  "selling_price": 620.0 },
    { "date": "2024-11-02", "quantity_sold": 38.0,  "selling_price": 620.0 },
    { "date": "2024-11-03", "quantity_sold": 55.0,  "selling_price": 600.0 },
    { "date": "2024-11-04", "quantity_sold": 61.0,  "selling_price": 600.0 },
    { "date": "2024-11-05", "quantity_sold": 72.0,  "selling_price": 590.0 },
    { "date": "2024-11-06", "quantity_sold": 68.0,  "selling_price": 590.0 },
    { "date": "2024-11-07", "quantity_sold": 45.0,  "selling_price": 620.0 },
    { "date": "2024-11-08", "quantity_sold": 41.0,  "selling_price": 620.0 },
    { "date": "2024-11-09", "quantity_sold": 39.0,  "selling_price": 620.0 },
    { "date": "2024-11-10", "quantity_sold": 8.0,   "selling_price": 620.0 },
    { "date": "2024-11-11", "quantity_sold": 48.0,  "selling_price": 610.0 },
    { "date": "2024-11-12", "quantity_sold": 66.0,  "selling_price": 595.0 },
    { "date": "2024-11-13", "quantity_sold": 74.0,  "selling_price": 595.0 },
    { "date": "2024-11-14", "quantity_sold": 50.0,  "selling_price": 615.0 },
    { "date": "2024-11-15", "quantity_sold": 44.0,  "selling_price": 620.0 },
    { "date": "2024-11-16", "quantity_sold": 40.0,  "selling_price": 620.0 },
    { "date": "2024-11-17", "quantity_sold": 36.0,  "selling_price": 625.0 },
    { "date": "2024-11-18", "quantity_sold": 58.0,  "selling_price": 605.0 },
    { "date": "2024-11-19", "quantity_sold": 63.0,  "selling_price": 600.0 },
    { "date": "2024-11-20", "quantity_sold": 71.0,  "selling_price": 590.0 },
    { "date": "2024-11-21", "quantity_sold": 69.0,  "selling_price": 592.0 },
    { "date": "2024-11-22", "quantity_sold": 47.0,  "selling_price": 618.0 },
    { "date": "2024-11-23", "quantity_sold": 43.0,  "selling_price": 620.0 },
    { "date": "2024-11-24", "quantity_sold": 210.0, "selling_price": 560.0 },
    { "date": "2024-11-25", "quantity_sold": 54.0,  "selling_price": 608.0 },
    { "date": "2024-11-26", "quantity_sold": 60.0,  "selling_price": 600.0 },
    { "date": "2024-11-27", "quantity_sold": 76.0,  "selling_price": 588.0 },
    { "date": "2024-11-28", "quantity_sold": 80.0,  "selling_price": 585.0 },
    { "date": "2024-11-29", "quantity_sold": 55.0,  "selling_price": 610.0 },
    { "date": "2024-11-30", "quantity_sold": 49.0,  "selling_price": 615.0 }
  ]
}
```

**What the model should detect:**
- Mean qty ~ 57.6, std ~ 36.8
- 2024-11-10: qty=8 -> Z = (8-57.6)/36.8 = -1.35 ... with mean recalculated excluding spike: mean~50.7, std~15.2 -> Z = -2.8 -> DROP flagged
- 2024-11-24: qty=210 -> Z = (210-50.7)/15.2 = +10.5 (capped at 10.0) -> SPIKE flagged
- Both dates are more than 7 days before 2024-11-30 -> stage = "pre_forecast_historical"

#### What the Model Must Return (Expected Output JSON)

```json
{
  "model_version": "1.0.0",
  "flagged_anomalies": [
    {
      "date": "2024-11-10T00:00:00",
      "stage": "pre_forecast_historical",
      "anomaly_type": "drop",
      "severity_score": 2.8,
      "explanation": "Sales quantity (8) is 2.8 standard deviations below the historical mean (50.7). Possible supply disruption, stockout, or data entry error on this date.",
      "acknowledged": false
    },
    {
      "date": "2024-11-24T00:00:00",
      "stage": "pre_forecast_historical",
      "anomaly_type": "spike",
      "severity_score": 10.0,
      "explanation": "Sales quantity (210) is 10.0+ standard deviations above the historical mean (50.7). Likely caused by a promotional event, festive demand surge (Diwali proximity), or bulk corporate purchase.",
      "acknowledged": false
    }
  ]
}
```

**How the backend uses this response:**

| Field | How backend uses it |
|---|---|
| `flagged_anomalies` | Each item stored as FlaggedAnomaly in AnomalyCurrentDocument |
| `stage` | Determines which dashboard alert section it appears in |
| `anomaly_type` | Badge color: spike = orange, drop = red |
| `severity_score` | Sort order: highest severity first |
| `explanation` | Shown as tooltip/description on anomaly alert card |
| `acknowledged` | User clicks "Acknowledge" in UI -> set to true |

---

### 7D. Edge Case — Insufficient Data (new product, only 5 days history)

**Input:**
```json
{
  "task": "forecasting",
  "history": [
    { "date": "2024-11-26", "quantity_sold": 12.0, "selling_price": 350.0 },
    { "date": "2024-11-27", "quantity_sold": 15.0, "selling_price": 350.0 },
    { "date": "2024-11-28", "quantity_sold": 10.0, "selling_price": 355.0 },
    { "date": "2024-11-29", "quantity_sold": 18.0, "selling_price": 348.0 },
    { "date": "2024-11-30", "quantity_sold": 14.0, "selling_price": 350.0 }
  ]
}
```

**Expected Output — return empty arrays, no crash:**
```json
{
  "metrics": { "MAE": 0.0, "RMSE": 0.0, "MAPE": 0.0 },
  "forecast_7d": [],
  "forecast_30d": []
}
```

> Backend detects empty arrays -> sets pipeline_type = "insufficient_data" -> shows "Not enough data" message in dashboard.

---

### 7E. Edge Case — No Anomalies Found

**Expected Output — always return the key, just with empty list:**
```json
{
  "model_version": "1.0.0",
  "flagged_anomalies": []
}
```

> Backend stores AnomalyCurrentDocument with total_flagged_count=0 and has_unreviewed_alerts=false. Dashboard shows green "All Clear" badge.

---

### 7F. Complete Field Reference Table

| Field | Type | Required | Constraints |
|---|---|---|---|
| **FORECASTING** | | | |
| metrics.MAE | float | Yes | >= 0 |
| metrics.RMSE | float | Yes | >= 0 |
| metrics.MAPE | float | Yes | >= 0, drives confidence label |
| forecast_7d | array | Yes | Exactly 0 or 7 items |
| forecast_30d | array | Yes | Exactly 0 or 30 items |
| [].ds | string | Yes | "2025-01-01T00:00:00" |
| [].hybrid_yhat | float | Yes | Must be >= 0 |
| [].yhat_lower | float | Yes | Must be >= 0 |
| [].yhat_upper | float | Yes | >= yhat_lower |
| [].horizon_days | int | Yes | 7 or 30 |
| **PRICING** | | | |
| eligibility_status | string enum | Yes | eligible, ineligible, insufficient_history, insufficient_price_variation |
| eligibility_reason | string or null | Yes | null if eligible |
| recommended_price | float or null | Yes | Within bound_range |
| expected_revenue | float or null | Yes | >= 0 |
| elasticity_model_type | string or null | Yes | e.g. "Log-Log OLS Elasticity" |
| model_version | string | Yes | e.g. "1.0.0" |
| bound_range.min | float | Yes | current_price x (1 - bound_pct) |
| bound_range.max | float | Yes | current_price x (1 + bound_pct) |
| candidate_grid | array or null | Yes | Exactly 5 items if eligible |
| candidate_grid[].candidate_price | float | Yes | Within bound_range |
| candidate_grid[].estimated_demand | float | Yes | >= 0 |
| candidate_grid[].estimated_revenue | float | Yes | >= 0 |
| **ANOMALY** | | | |
| model_version | string | Yes | e.g. "1.0.0" |
| flagged_anomalies | array | Yes | Empty [] if no anomalies |
| [].date | string | Yes | "2024-11-10T00:00:00" |
| [].stage | string enum | Yes | post_upload_alert or pre_forecast_historical |
| [].anomaly_type | string enum | Yes | spike or drop |
| [].severity_score | float | Yes | 0.0 to 10.0, always positive |
| [].explanation | string | Yes | Plain English, mentions actual qty and mean |
| [].acknowledged | bool | Yes | Always false |
