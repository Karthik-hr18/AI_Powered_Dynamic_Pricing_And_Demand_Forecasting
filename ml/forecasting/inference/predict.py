import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple
import httpx
from beanie import PydanticObjectId

from app.core.config import settings
from app.core.constants import ForecastConfidenceLabel, ForecastPipelineType, ForecastTriggeredBy
from app.domains.forecasting.models import (
    ForecastCurrentDocument,
    ForecastHistoryDocument,
    ForecastHorizon,
    ForecastPrediction
)

logger = logging.getLogger("ml.forecasting.inference.predict")


def call_hf_api(payload: dict) -> dict:
    # Helper to perform requests to Hugging Face Inference API.
    if not settings.HF_API_URL or not settings.HF_API_TOKEN:
        raise ValueError("Hugging Face API URL or Token is not configured.")
    
    headers = {"Authorization": f"Bearer {settings.HF_API_TOKEN}"}
    try:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(settings.HF_API_URL, json=payload, headers=headers)
            
            if res.status_code == 503:
                data = res.json()
                est_time = data.get("estimated_time", 20.0)
                raise ValueError(
                    f"Hugging Face Model is currently loading (503). Estimated startup: {est_time}s. Please retry in a moment."
                )
            elif res.status_code == 429:
                raise ValueError("Hugging Face API rate-limited (429). Please try again later.")
            elif res.status_code != 200:
                raise ValueError(f"Hugging Face API error ({res.status_code}): {res.text}")
                
            return res.json()
    except httpx.RequestError as e:
        raise ValueError(f"Failed to connect to Hugging Face API: {e}")


def predict_demand(
    retailer_id: PydanticObjectId,
    product_id: PydanticObjectId,
    history: List[Any],
    upload_id: PydanticObjectId,
    run_id: PydanticObjectId,
    trigger_by: ForecastTriggeredBy
) -> Tuple[ForecastCurrentDocument, ForecastHistoryDocument]:
    # Executes demand forecasting via either Hugging Face Inference Endpoint or local fallback.
    history_days = len(history)
    run_time = datetime.utcnow()
    
    # Sort history by date to ensure proper timeline ordering
    history_sorted = sorted(history, key=lambda x: x.date)
    max_date = history_sorted[-1].date if history_sorted else run_time

    # Determine environment fallback
    use_hf = (
        settings.HF_API_URL and 
        "placeholder" not in settings.HF_API_URL and
        settings.HF_API_TOKEN and
        "placeholder" not in settings.HF_API_TOKEN
    )

    if use_hf:
        logger.info(f"Routing forecasting request to Hugging Face API: {settings.HF_API_URL}")
        payload = {
            "task": "forecasting",
            "history": [
                {
                    "date": item.date.isoformat() if hasattr(item.date, "isoformat") else str(item.date),
                    "quantity_sold": float(item.quantity_sold),
                    "selling_price": float(item.selling_price)
                }
                for item in history_sorted
            ]
        }
        
        res_data = call_hf_api(payload)
        
        # ── Derive model metadata ──────────────────────────────────────────────
        # The HF model does NOT return pipeline_type / confidence_label /
        # model_version directly. Derive them from the "metrics" block instead.
        metrics      = res_data.get("metrics", {})
        mape         = float(metrics.get("MAPE", 999.0))
        model_version = "1.0.0-huggingface-hybrid"
        eligibility_reason = None

        if mape < 20.0:
            confidence_label = ForecastConfidenceLabel.HIGH
        elif mape < 50.0:
            confidence_label = ForecastConfidenceLabel.MEDIUM
        else:
            # MAPE > 50 (e.g. 188%) → model is low confidence
            confidence_label = ForecastConfidenceLabel.LOW

        # ── Parse horizon arrays ───────────────────────────────────────────────
        # Actual format: flat list of dicts with keys:
        #   product_id, ds (ISO datetime string), yhat, xgb_residual,
        #   hybrid_yhat, yhat_lower, yhat_upper, horizon_days
        #
        # We use "hybrid_yhat" (Prophet + XGBoost combined prediction) as the
        # canonical predicted quantity, clamped to 0 since quantities can't
        # be negative (model can produce negative yhat for low-demand products).

        def parse_forecast_array(rows: list) -> Optional["ForecastHorizon"]:
            """Convert a flat forecast row array into a ForecastHorizon document."""
            if not rows:
                return None
            preds = []
            for row in rows:
                raw_qty = row.get("hybrid_yhat", row.get("yhat", 0.0))
                clamped_qty = max(0.0, round(float(raw_qty), 4))
                date_str = row.get("ds", "")
                try:
                    pred_date = datetime.fromisoformat(date_str)
                except (ValueError, TypeError):
                    logger.warning(f"Skipping row with invalid ds value: {date_str!r}")
                    continue
                preds.append(
                    ForecastPrediction(
                        date=pred_date,
                        predicted_quantity=clamped_qty
                    )
                )
            if not preds:
                return None
            return ForecastHorizon(predictions=preds, confidence=confidence_label.value)

        raw_7d  = res_data.get("forecast_7d",  [])
        raw_30d = res_data.get("forecast_30d", [])

        horizon_7d  = parse_forecast_array(raw_7d)
        horizon_30d = parse_forecast_array(raw_30d)

        # Derive pipeline type from actual prediction availability
        if horizon_7d and horizon_7d.predictions:
            pipeline_type = ForecastPipelineType.FULL if horizon_30d else ForecastPipelineType.FALLBACK
        else:
            pipeline_type = ForecastPipelineType.INSUFFICIENT_DATA
            eligibility_reason = "Hugging Face model returned no forecast rows for this product."

        logger.info(
            f"HF forecasting parsed: 7d_rows={len(raw_7d)}, 30d_rows={len(raw_30d)}, "
            f"MAPE={mape:.1f}%, confidence={confidence_label.value}, pipeline={pipeline_type.value}"
        )

    else:
        # Graceful Local Fallback Mock
        model_version = "1.0.0-mock"

        if history_days < 14:
            pipeline_type = ForecastPipelineType.INSUFFICIENT_DATA
            confidence_label = ForecastConfidenceLabel.LOW
            eligibility_reason = f"Insufficient historical sales data. Only {history_days} days available (minimum 14 required)."
            horizon_7d = None
            horizon_30d = None
            
        elif history_days < 30:
            pipeline_type = ForecastPipelineType.FALLBACK
            confidence_label = ForecastConfidenceLabel.LOW
            eligibility_reason = None
            
            last_7 = history_sorted[-7:]
            weights = [1, 2, 3, 4, 5, 6, 7]
            weighted_sum = sum(last_7[i].quantity_sold * weights[i] for i in range(len(last_7)))
            flat_wma = weighted_sum / sum(weights[:len(last_7)])
            flat_prediction = max(0.0, round(flat_wma, 2))

            preds_7d = []
            for i in range(1, 8):
                proj_date = max_date + timedelta(days=i)
                preds_7d.append(
                    ForecastPrediction(
                        date=proj_date,
                        predicted_quantity=flat_prediction
                    )
                )
            horizon_7d = ForecastHorizon(predictions=preds_7d, confidence="low")
            horizon_30d = None
            
        else:
            pipeline_type = ForecastPipelineType.FULL
            confidence_label = ForecastConfidenceLabel.HIGH
            eligibility_reason = None
            
            last_14 = history_sorted[-14:]
            mean_qty = sum(item.quantity_sold for item in last_14) / 14.0

            preds_7d = []
            preds_30d = []
            for d in range(1, 31):
                proj_date = max_date + timedelta(days=d)
                seasonality = 1.3 if proj_date.weekday() in (5, 6) else 0.85
                pred_qty = max(0.0, round(mean_qty * seasonality, 2))
                
                prediction_item = ForecastPrediction(
                    date=proj_date,
                    predicted_quantity=pred_qty
                )
                preds_30d.append(prediction_item)
                if d <= 7:
                    preds_7d.append(prediction_item)

            horizon_7d = ForecastHorizon(predictions=preds_7d, confidence="high")
            horizon_30d = ForecastHorizon(predictions=preds_30d, confidence="medium")

    # Construct the final Beanie documents
    current_doc = ForecastCurrentDocument(
        retailer_id=retailer_id,
        product_id=product_id,
        pipeline_type=pipeline_type,
        eligibility_reason=eligibility_reason,
        history_days_available=history_days,
        horizon_7d=horizon_7d,
        horizon_30d=horizon_30d,
        confidence_label=confidence_label,
        model_version=model_version,
        run_id=run_id,
        upload_id=upload_id,
        run_timestamp=run_time
    )

    history_doc = ForecastHistoryDocument(
        retailer_id=retailer_id,
        product_id=product_id,
        pipeline_type=pipeline_type,
        eligibility_reason=eligibility_reason,
        history_days_available=history_days,
        horizon_7d=horizon_7d,
        horizon_30d=horizon_30d,
        confidence_label=confidence_label,
        model_version=model_version,
        run_id=run_id,
        upload_id=upload_id,
        run_timestamp=run_time,
        triggered_by=trigger_by
    )

    return current_doc, history_doc
