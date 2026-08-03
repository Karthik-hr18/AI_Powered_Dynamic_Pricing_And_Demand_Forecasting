import logging
from datetime import datetime, timedelta
from typing import Any, List, Tuple
from beanie import PydanticObjectId

from app.core.config import settings
from app.core.constants import AnomalyStage, AnomalyType
from app.domains.anomaly.models import AnomalyCurrentDocument, FlaggedAnomaly
from ml.forecasting.inference.predict import call_hf_api

logger = logging.getLogger("ml.anomaly.inference.predict")


def detect_anomalies(
    retailer_id: PydanticObjectId,
    product_id: PydanticObjectId,
    history: List[Any],
    upload_id: PydanticObjectId
) -> AnomalyCurrentDocument:
    """
    Computes statistical outlier detection via Hugging Face Inference Endpoint or local fallback.
    """
    run_time = datetime.utcnow()
    flagged_list = []

    # Sort history by date to ensure proper timeline ordering
    history_sorted = sorted(history, key=lambda x: x.date)

    # Determine environment fallback
    use_hf = (
        settings.HF_API_URL and 
        "placeholder" not in settings.HF_API_URL and
        settings.HF_API_TOKEN and
        "placeholder" not in settings.HF_API_TOKEN
    )

    if use_hf:
        logger.info(f"Routing anomaly request to Hugging Face API: {settings.HF_API_URL}")
        payload = {
            "task": "anomaly",
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
        
        anoms = res_data.get("flagged_anomalies", [])
        for a in anoms:
            flagged_list.append(
                FlaggedAnomaly(
                    date=datetime.fromisoformat(a["date"]),
                    stage=AnomalyStage(a["stage"]),
                    anomaly_type=AnomalyType(a["anomaly_type"]),
                    severity_score=a["severity_score"],
                    explanation=a["explanation"],
                    acknowledged=a.get("acknowledged", False)
                )
            )
        model_version = res_data.get("model_version", "1.0.0-huggingface")

    else:
        # Graceful Local Fallback Mock
        model_version = "1.0.0-mock"

        if len(history) >= 5:
            quantities = [float(item.quantity_sold) for item in history_sorted]
            mean_sales = sum(quantities) / len(quantities)
            variance = sum((q - mean_sales) ** 2 for q in quantities) / len(quantities)
            std_sales = variance ** 0.5
            
            if std_sales < 1.0:
                std_sales = 1.0

            threshold_recent_date = run_time - timedelta(days=7)
            if history_sorted:
                max_date = history_sorted[-1].date
                threshold_recent_date = max_date - timedelta(days=7)

            for item in history_sorted:
                qty = float(item.quantity_sold)
                diff = qty - mean_sales
                z_score = diff / std_sales

                if abs(z_score) >= 2.0:
                    if z_score > 0:
                        anomaly_type = AnomalyType.SPIKE
                        explanation = (
                            f"Sales quantity ({int(qty)}) is {round(z_score, 1)} standard deviations "
                            f"above the historical mean ({round(mean_sales, 1)})."
                        )
                    else:
                        anomaly_type = AnomalyType.DROP
                        explanation = (
                            f"Sales quantity ({int(qty)}) is {round(abs(z_score), 1)} standard deviations "
                            f"below the historical mean ({round(mean_sales, 1)})."
                        )

                    stage = (
                        AnomalyStage.POST_UPLOAD_ALERT 
                        if item.date >= threshold_recent_date 
                        else AnomalyStage.PRE_FORECAST_HISTORICAL
                    )

                    flagged_list.append(
                        FlaggedAnomaly(
                            date=item.date,
                            stage=stage,
                            anomaly_type=anomaly_type,
                            severity_score=round(abs(z_score), 2),
                            explanation=explanation,
                            acknowledged=False
                        )
                    )

    has_unreviewed = any(not a.acknowledged for a in flagged_list)

    doc = AnomalyCurrentDocument(
        retailer_id=retailer_id,
        product_id=product_id,
        flagged_anomalies=flagged_list,
        total_flagged_count=len(flagged_list),
        has_unreviewed_alerts=has_unreviewed,
        model_version=model_version,
        upload_id=upload_id,
        run_timestamp=run_time
    )

    return doc
