import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple
from beanie import PydanticObjectId

from app.core.constants import ForecastConfidenceLabel, ForecastPipelineType, ForecastTriggeredBy
from app.domains.forecasting.models import (
    ForecastCurrentDocument,
    ForecastHistoryDocument,
    ForecastHorizon,
    ForecastPrediction
)

logger = logging.getLogger("ml.forecasting.inference.predict")


def predict_demand(
    retailer_id: PydanticObjectId,
    product_id: PydanticObjectId,
    history: List[Any],
    upload_id: PydanticObjectId,
    run_id: PydanticObjectId,
    trigger_by: ForecastTriggeredBy
) -> Tuple[ForecastCurrentDocument, ForecastHistoryDocument]:
    """
    Evaluates product sales history length, executes the corresponding forecasting tier
    (Insufficient, Fallback, or Full), and returns matching Current and History Beanie documents.
    """
    history_days = len(history)
    run_time = datetime.utcnow()
    
    # Sort history by date to ensure proper timeline ordering
    history_sorted = sorted(history, key=lambda x: x.date)
    max_date = history_sorted[-1].date if history_sorted else run_time

    # Default model variables
    model_version = "1.0.0-mock"

    if history_days < 14:
        # Tier 1: Insufficient History (<14 days)
        pipeline_type = ForecastPipelineType.INSUFFICIENT_DATA
        confidence_label = ForecastConfidenceLabel.LOW
        eligibility_reason = f"Insufficient historical sales data. Only {history_days} days available (minimum 14 required)."
        horizon_7d = None
        horizon_30d = None
        
    elif history_days < 30:
        # Tier 2: Fallback Flat WMA Projection (14 - 29 days)
        pipeline_type = ForecastPipelineType.FALLBACK
        confidence_label = ForecastConfidenceLabel.LOW
        eligibility_reason = None
        
        # Calculate flat weighted moving average over the last 7 days
        last_7 = history_sorted[-7:]
        weights = [1, 2, 3, 4, 5, 6, 7]
        weighted_sum = sum(last_7[i].quantity_sold * weights[i] for i in range(len(last_7)))
        flat_wma = weighted_sum / sum(weights[:len(last_7)])
        flat_prediction = max(0.0, round(flat_wma, 2))

        # Project 7 days forward
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
        # Tier 3: Full Pipeline (30+ days of history)
        pipeline_type = ForecastPipelineType.FULL
        confidence_label = ForecastConfidenceLabel.HIGH
        eligibility_reason = None
        
        # Calculate mean daily quantity over the last 14 days
        last_14 = history_sorted[-14:]
        mean_qty = sum(item.quantity_sold for item in last_14) / 14.0

        # Project 7-day and 30-day horizons with mock day-of-week seasonality (weekend bump)
        preds_7d = []
        preds_30d = []
        for d in range(1, 31):
            proj_date = max_date + timedelta(days=d)
            # Weekend sales are typically 1.3x mean; weekday sales are 0.85x
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
