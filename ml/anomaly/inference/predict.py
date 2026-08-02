import logging
from datetime import datetime, timedelta
from typing import Any, List, Tuple
from beanie import PydanticObjectId

from app.core.constants import AnomalyStage, AnomalyType
from app.domains.anomaly.models import AnomalyCurrentDocument, FlaggedAnomaly

logger = logging.getLogger("ml.anomaly.inference.predict")


def detect_anomalies(
    retailer_id: PydanticObjectId,
    product_id: PydanticObjectId,
    history: List[Any],
    upload_id: PydanticObjectId
) -> AnomalyCurrentDocument:
    """
    Computes statistical Z-score outlier detection over the product's sales timeline.
    Flags sales quantities deviating past 2.0 standard deviations as SPIKE or DROP anomalies.
    """
    run_time = datetime.utcnow()
    model_version = "1.0.0-mock"
    flagged_list = []

    if len(history) >= 5:
        # Calculate mean and standard deviation of daily quantity_sold
        quantities = [float(item.quantity_sold) for item in history]
        mean_sales = sum(quantities) / len(quantities)
        variance = sum((q - mean_sales) ** 2 for q in quantities) / len(quantities)
        std_sales = variance ** 0.5
        
        # Enforce safety minimum standard deviation bounds to avoid division by zero
        if std_sales < 1.0:
            std_sales = 1.0

        # Determine threshold boundaries for recently uploaded days vs historic days
        # E.g. classify anomalies in the last 7 days of history as POST_UPLOAD_ALERT stage
        history_sorted = sorted(history, key=lambda x: x.date)
        max_date = history_sorted[-1].date if history_sorted else run_time
        threshold_recent_date = max_date - timedelta(days=7)

        for item in history_sorted:
            qty = float(item.quantity_sold)
            diff = qty - mean_sales
            z_score = diff / std_sales

            # Identify if Z-score is an outlier (beyond absolute value of 2.0)
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

                # Classify stage: recent uploads trigger alerts; older rows are historical
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
