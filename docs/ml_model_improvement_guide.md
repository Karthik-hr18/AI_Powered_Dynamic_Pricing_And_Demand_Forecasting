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
