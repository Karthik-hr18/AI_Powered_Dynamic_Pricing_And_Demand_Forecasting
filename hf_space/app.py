import logging
import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor

try:
    from prophet import Prophet
except Exception:
    from fbprophet import Prophet

try:
    import gradio as gr
except ImportError:
    gr = None

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ProfitSyncML")


# =====================================================================
# TASK 1: HYBRID DEMAND FORECASTING (Prophet + XGBoost)
# =====================================================================

def run_forecasting_task(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(history) < 7:
        return {
            "metrics": {"MAE": 0.0, "RMSE": 0.0, "MAPE": 0.0, "sMAPE": 0.0},
            "forecast_7d": [],
            "forecast_30d": [],
        }

    df = pd.DataFrame(history)
    df["ds"] = pd.to_datetime(df["date"])
    df["y"] = df["quantity_sold"].astype(float)
    df = df.sort_values("ds").reset_index(drop=True)

    n_obs = len(df)
    n_changepoints = min(25, max(1, n_obs - 1))
    
    prophet_model = Prophet(
        growth="linear",
        yearly_seasonality=n_obs >= 365,
        weekly_seasonality=n_obs >= 14,
        daily_seasonality=False,
        seasonality_mode="multiplicative",
        interval_width=0.95,
        changepoint_prior_scale=0.05,
        n_changepoints=n_changepoints,
    )
    prophet_model.fit(df[["ds", "y"]])

    in_sample = prophet_model.predict(df[["ds"]])
    df["prophet_yhat"] = in_sample["yhat"]
    df["residual"] = df["y"] - df["prophet_yhat"]

    df["day_of_week"] = df["ds"].dt.dayofweek
    df["month"] = df["ds"].dt.month
    df["quarter"] = df["ds"].dt.quarter
    df["year"] = df["ds"].dt.year
    df["is_weekend"] = df["ds"].dt.dayofweek.isin([5, 6]).astype(int)

    for lag in (1, 7, 14):
        df[f"lag_{lag}"] = df["y"].shift(lag).bfill().fillna(0)
    for window in (3, 7, 14):
        df[f"rolling_mean_{window}"] = df["y"].shift(1).rolling(window, min_periods=1).mean().fillna(0)
        df[f"rolling_std_{window}"] = df["y"].shift(1).rolling(window, min_periods=1).std().fillna(0)

    feature_cols = [
        "day_of_week", "month", "quarter", "year", "is_weekend",
        "lag_1", "lag_7", "lag_14",
        "rolling_mean_3", "rolling_mean_7", "rolling_mean_14",
        "rolling_std_3", "rolling_std_7", "rolling_std_14",
        "selling_price",
    ]
    feature_cols = [c for c in feature_cols if c in df.columns]

    X_train = df[feature_cols].copy().fillna(0)
    y_train = df["residual"].copy().fillna(0)

    xgb_model = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
    )
    xgb_model.fit(X_train, y_train)

    in_sample_resid_pred = xgb_model.predict(X_train)
    final_in_sample = (df["prophet_yhat"] + in_sample_resid_pred).clip(lower=0)
    
    y_true = df["y"].values
    y_pred = final_in_sample.values
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-6))) * 100)
    
    smape_denom = (np.abs(y_true) + np.abs(y_pred)) / 2.0
    smape = float(np.mean(np.where(smape_denom == 0, 0, np.abs(y_true - y_pred) / smape_denom)) * 100)

    def generate_horizon_forecast(horizon: int) -> List[Dict[str, Any]]:
        future_dates = prophet_model.make_future_dataframe(periods=horizon, freq="D")
        prophet_fut = prophet_model.predict(future_dates).tail(horizon).copy()

        future_rows = []
        last_row = df.iloc[-1].copy()
        
        for i in range(horizon):
            cur_date = prophet_fut["ds"].iloc[i]
            row_dict = last_row.to_dict()
            row_dict["ds"] = cur_date
            row_dict["day_of_week"] = cur_date.dayofweek
            row_dict["month"] = cur_date.month
            row_dict["quarter"] = cur_date.quarter
            row_dict["year"] = cur_date.year
            row_dict["is_weekend"] = int(cur_date.dayofweek in [5, 6])
            
            for lag in (1, 7, 14):
                if len(df) >= lag:
                    row_dict[f"lag_{lag}"] = float(df["y"].iloc[-lag])
            for window in (3, 7, 14):
                vals = df["y"].tail(window)
                row_dict[f"rolling_mean_{window}"] = float(vals.mean()) if len(vals) > 0 else float(df["y"].iloc[-1])
                row_dict[f"rolling_std_{window}"] = float(vals.std()) if len(vals) > 1 else 0.0

            future_rows.append(row_dict)

        fut_df = pd.DataFrame(future_rows)
        X_fut = fut_df[feature_cols].copy().fillna(0)
        xgb_fut_resid = xgb_model.predict(X_fut)

        prophet_yhat = prophet_fut["yhat"].values
        prophet_lower = prophet_fut["yhat_lower"].values
        prophet_upper = prophet_fut["yhat_upper"].values

        hybrid_yhat = np.clip(prophet_yhat + xgb_fut_resid, 0, None)
        yhat_lower = np.clip(prophet_lower, 0, None)
        yhat_upper = np.clip(prophet_upper, 0, None)

        records = []
        for i in range(horizon):
            dt_val = prophet_fut["ds"].iloc[i]
            dt_str = dt_val.isoformat() if hasattr(dt_val, "isoformat") else str(dt_val)
            records.append({
                "ds": dt_str,
                "hybrid_yhat": round(float(hybrid_yhat[i]), 2),
                "yhat_lower": round(float(yhat_lower[i]), 2),
                "yhat_upper": round(float(yhat_upper[i]), 2),
                "horizon_days": horizon,
            })
        return records

    return {
        "metrics": {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE": round(mape, 2),
            "sMAPE": round(smape, 2),
        },
        "forecast_7d": generate_horizon_forecast(7),
        "forecast_30d": generate_horizon_forecast(30),
    }


# =====================================================================
# TASK 2: PRICING OPTIMIZATION & ELASTICITY
# =====================================================================

def run_pricing_task(history: List[Dict[str, Any]], current_price: Optional[float] = None, bound_pct: float = 0.20) -> Dict[str, Any]:
    if len(history) < 7:
        return {
            "eligibility_status": "insufficient_history",
            "eligibility_reason": f"Only {len(history)} data points provided. Minimum 7 required.",
            "recommended_price": None,
            "expected_revenue": None,
            "elasticity_model_type": "Log-Log Ridge Elasticity",
            "model_version": "1.0.0",
            "bound_range": None,
            "candidate_grid": None,
        }

    df = pd.DataFrame(history)
    prices = df["selling_price"].astype(float).values
    quantities = df["quantity_sold"].astype(float).values

    unique_prices = set(np.round(prices, 2))
    if len(unique_prices) <= 1:
        return {
            "eligibility_status": "insufficient_price_variation",
            "eligibility_reason": "Price has not changed in historical data. Elasticity cannot be estimated.",
            "recommended_price": None,
            "expected_revenue": None,
            "elasticity_model_type": "Log-Log Ridge Elasticity",
            "model_version": "1.0.0",
            "bound_range": None,
            "candidate_grid": None,
        }

    curr_p = float(current_price) if current_price and current_price > 0 else float(prices[-1])
    bound_min = round(curr_p * (1.0 - bound_pct), 2)
    bound_max = round(curr_p * (1.0 + bound_pct), 2)

    log_p = np.log(np.maximum(prices, 0.01)).reshape(-1, 1)
    log_q = np.log(np.maximum(quantities, 1.0))

    ridge = Ridge(alpha=1.0)
    ridge.fit(log_p, log_q)
    elasticity = float(ridge.coef_[0])

    price_grid = np.linspace(bound_min, bound_max, 5)
    base_demand = float(np.mean(quantities[-7:])) if len(quantities) >= 7 else float(np.mean(quantities))

    candidate_grid = []
    for p in price_grid:
        p_val = float(p)
        est_demand = max(0.0, base_demand * ((p_val / curr_p) ** elasticity)) if curr_p > 0 else base_demand
        est_rev = round(p_val * est_demand, 2)
        candidate_grid.append({
            "candidate_price": round(p_val, 2),
            "estimated_demand": round(float(est_demand), 2),
            "estimated_revenue": est_rev,
        })

    best_candidate = max(candidate_grid, key=lambda x: x["estimated_revenue"])

    return {
        "eligibility_status": "eligible",
        "eligibility_reason": None,
        "recommended_price": best_candidate["candidate_price"],
        "expected_revenue": best_candidate["estimated_revenue"],
        "elasticity_model_type": "Log-Log Ridge Elasticity",
        "model_version": "1.0.0",
        "bound_range": {"min": bound_min, "max": bound_max},
        "candidate_grid": candidate_grid,
    }


# =====================================================================
# TASK 3: ANOMALY DETECTION (Z-Score & Severity)
# =====================================================================

def run_anomaly_task(history: List[Dict[str, Any]], threshold_std: float = 2.5, recent_days: int = 7) -> Dict[str, Any]:
    if len(history) < 5:
        return {"model_version": "1.0.0", "flagged_anomalies": []}

    df = pd.DataFrame(history)
    df["ds"] = pd.to_datetime(df["date"])
    df = df.sort_values("ds").reset_index(drop=True)

    quantities = df["quantity_sold"].astype(float).values
    mean_qty = float(np.mean(quantities))
    std_qty = float(np.std(quantities)) if np.std(quantities) > 0 else 1.0

    last_date = df["ds"].max()
    cutoff_date = last_date - timedelta(days=recent_days)

    flagged = []
    for _, row in df.iterrows():
        q = float(row["quantity_sold"])
        z = (q - mean_qty) / std_qty

        if abs(z) < threshold_std:
            continue

        anomaly_type = "spike" if z > 0 else "drop"
        dt_val = row["ds"]
        stage = "post_upload_alert" if dt_val >= cutoff_date else "pre_forecast_historical"
        severity = round(min(abs(z), 10.0), 2)

        direction = "above" if anomaly_type == "spike" else "below"
        explanation = (
            f"Sales quantity ({int(q)}) is {severity} standard deviations "
            f"{direction} the historical mean ({round(mean_qty, 1)}). "
            f"{'Possible demand surge or promotion.' if anomaly_type == 'spike' else 'Possible supply disruption or stockout.'}"
        )

        dt_str = dt_val.isoformat() if hasattr(dt_val, "isoformat") else str(dt_val)
        flagged.append({
            'date': dt_str,
            'stage': stage,
            'anomaly_type': anomaly_type,
            'severity_score': severity,
            'explanation': explanation,
            'acknowledged': False,
        })

    return {
        "model_version": "1.0.0",
        "flagged_anomalies": flagged,
    }


# =====================================================================
# GRADIO API ENDPOINT HANDLER
# =====================================================================

def api_predict(payload: dict) -> dict:
    """
    Gradio API wrapper. Accepts JSON payload from FastAPI backend.
    """
    if not isinstance(payload, dict):
        return {"error": "Invalid payload format. Must be JSON dict."}

    task = str(payload.get("task", "")).lower().strip()
    history = payload.get("history", [])
    current_price = payload.get("current_price")
    bound_pct = payload.get("bound_pct", 0.20)

    try:
        if task == "forecasting":
            return run_forecasting_task(history)
        elif task == "pricing":
            return run_pricing_task(history, current_price, bound_pct)
        elif task == "anomaly":
            return run_anomaly_task(history)
        else:
            return {"error": f"Invalid task '{task}'. Allowed: 'forecasting', 'pricing', 'anomaly'."}
    except Exception as e:
        logger.error(f"Error executing task '{task}': {str(e)}", exc_info=True)
        return {"error": f"ML Execution Error: {str(e)}"}


# Gradio Interface configured for API calls
if gr:
    demo = gr.Interface(
        fn=api_predict,
        inputs=gr.JSON(label="Inference Payload (dict with task, history, etc.)"),
        outputs=gr.JSON(label="ML Prediction Output"),
        title="ProfitSync Enterprise ML API Engine",
        description="Live Gradio ML Inference Service for ProfitSync SaaS.",
    )

    if __name__ == "__main__":
        demo.launch()
