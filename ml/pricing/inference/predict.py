import logging
from datetime import datetime
from typing import Any, List, Optional, Tuple
from beanie import PydanticObjectId

from app.core.config import settings
from app.core.constants import ForecastTriggeredBy, PricingEligibilityStatus
from app.domains.pricing.models import (
    BoundRange,
    CandidateGridEntry,
    PricingCurrentDocument,
    PricingHistoryDocument
)
from ml.forecasting.inference.predict import call_hf_api

logger = logging.getLogger("ml.pricing.inference.predict")


def recommend_price(
    retailer_id: PydanticObjectId,
    product_id: PydanticObjectId,
    history: List[Any],
    current_price: float,
    upload_id: PydanticObjectId,
    run_id: PydanticObjectId,
    trigger_by: ForecastTriggeredBy
) -> Tuple[PricingCurrentDocument, PricingHistoryDocument]:
    # Computes price recommendations via Hugging Face Inference Endpoint or local fallback.
    run_time = datetime.utcnow()
    bound_pct = settings.PRICING_BOUND_PCT

    # Sort history by date to ensure proper timeline ordering
    history_sorted = sorted(history, key=lambda x: x.date)

    historical_prices = set(
        round(item.selling_price, 2) 
        for item in history 
        if item.selling_price is not None and item.selling_price > 0
    )

    # Determine environment fallback
    use_hf = (
        settings.HF_API_URL and 
        "placeholder" not in settings.HF_API_URL and
        settings.HF_API_TOKEN and
        "placeholder" not in settings.HF_API_TOKEN
    )

    if use_hf:
        logger.info(f"Routing pricing request to Hugging Face API: {settings.HF_API_URL}")
        payload = {
            "task": "pricing",
            "history": [
                {
                    "date": item.date.isoformat() if hasattr(item.date, "isoformat") else str(item.date),
                    "quantity_sold": float(item.quantity_sold),
                    "selling_price": float(item.selling_price)
                }
                for item in history_sorted
            ],
            "current_price": float(current_price),
            "bound_pct": float(bound_pct)
        }
        
        res_data = call_hf_api(payload)
        
        eligibility_status = PricingEligibilityStatus(res_data.get("eligibility_status", "ineligible"))
        eligibility_reason = res_data.get("eligibility_reason")
        recommended_price = res_data.get("recommended_price")
        expected_revenue = res_data.get("expected_revenue")
        elasticity_model_type = res_data.get("elasticity_model_type")
        model_version = res_data.get("model_version", "1.0.0-huggingface")
        
        bound_data = res_data.get("bound_range")
        bound_range = (
            BoundRange(min=bound_data["min"], max=bound_data["max"])
            if bound_data else None
        )
        
        candidates = res_data.get("candidate_grid", [])
        candidate_grid = [
            CandidateGridEntry(
                candidate_price=c["candidate_price"],
                estimated_demand=c["estimated_demand"],
                estimated_revenue=c["estimated_revenue"]
            )
            for c in candidates
        ] if candidates else None

    else:
        # Graceful Local Fallback Mock
        model_version = "1.0.0-mock"

        unique_days = len(set(
            item.date.strftime("%Y-%m-%d") if hasattr(item.date, "strftime") else str(item.date)[:10]
            for item in history
        )) if history else 0

        if unique_days < 7:
            eligibility_status = PricingEligibilityStatus.INSUFFICIENT_HISTORY
            eligibility_reason = "Requires at least 7 days of sales history for price elasticity modeling"
            recommended_price = None
            expected_revenue = None
            bound_range = None
            candidate_grid = None
            elasticity_model_type = "Insufficient History"
        elif len(historical_prices) <= 1:
            eligibility_status = PricingEligibilityStatus.INSUFFICIENT_PRICE_VARIATION
            eligibility_reason = "Historical pricing exhibits no variance; elasticity model requires multiple distinct price points"
            recommended_price = None
            expected_revenue = None
            bound_range = None
            candidate_grid = None
            elasticity_model_type = "Insufficient Price Variation"
        else:
            effective_price = current_price if (current_price is not None and current_price > 0) else (
                history_sorted[-1].selling_price if (history_sorted and history_sorted[-1].selling_price > 0) else 100.0
            )

            eligibility_status = PricingEligibilityStatus.ELIGIBLE
            eligibility_reason = None
            elasticity_model_type = "Linear Elasticity Mock"

            min_bound = max(0.01, round(effective_price * (1 - bound_pct), 2))
            max_bound = round(effective_price * (1 + bound_pct), 2)
            bound_range = BoundRange(min=min_bound, max=max_bound)

            n_cand = getattr(settings, "PRICING_N_CANDIDATES", 5)
            step_multipliers = [round(1.0 - bound_pct + (2.0 * bound_pct * i / (n_cand - 1)), 3) for i in range(n_cand)]
            candidates = sorted(list(set(max(min_bound, min(max_bound, round(effective_price * m, 2))) for m in step_multipliers)))
            
            while len(candidates) < n_cand:
                candidates.append(round(candidates[-1] + 0.50, 2))
            candidates = sorted(candidates[:n_cand])

            last_7_sales = history_sorted[-7:] if len(history_sorted) >= 7 else history_sorted
            base_demand = (sum(item.quantity_sold for item in last_7_sales) / len(last_7_sales)) if last_7_sales else 5.0
            if base_demand <= 0:
                base_demand = 5.0
            elasticity = 1.2

            candidate_grid = []
            for P in candidates:
                pct_price_change = (P - effective_price) / effective_price if effective_price > 0 else 0.0
                est_demand = max(1.0, base_demand * (1 - elasticity * pct_price_change))
                est_rev = P * est_demand
                
                candidate_grid.append(
                    CandidateGridEntry(
                        candidate_price=P,
                        estimated_demand=round(est_demand, 2),
                        estimated_revenue=round(est_rev, 2)
                    )
                )

            winning_candidate = max(candidate_grid, key=lambda x: x.estimated_revenue)
            recommended_price = winning_candidate.candidate_price
            expected_revenue = winning_candidate.estimated_revenue

    # Instantiate Beanie documents
    current_doc = PricingCurrentDocument.model_construct(
        retailer_id=retailer_id,
        product_id=product_id,
        eligibility_status=eligibility_status,
        eligibility_reason=eligibility_reason,
        current_price=current_price,
        bound_pct=bound_pct,
        bound_range=bound_range,
        candidate_grid=candidate_grid,
        recommended_price=recommended_price,
        expected_revenue=expected_revenue,
        elasticity_model_type=elasticity_model_type,
        model_version=model_version,
        run_id=run_id,
        upload_id=upload_id,
        run_timestamp=run_time
    )

    history_doc = PricingHistoryDocument.model_construct(
        retailer_id=retailer_id,
        product_id=product_id,
        eligibility_status=eligibility_status,
        eligibility_reason=eligibility_reason,
        current_price=current_price,
        bound_pct=bound_pct,
        bound_range=bound_range,
        candidate_grid=candidate_grid,
        recommended_price=recommended_price,
        expected_revenue=expected_revenue,
        elasticity_model_type=elasticity_model_type,
        model_version=model_version,
        run_id=run_id,
        upload_id=upload_id,
        run_timestamp=run_time,
        triggered_by=trigger_by
    )

    return current_doc, history_doc
