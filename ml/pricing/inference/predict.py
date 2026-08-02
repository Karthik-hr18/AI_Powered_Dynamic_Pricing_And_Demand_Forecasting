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
    """
    Computes price recommendations by evaluating 5 candidate prices, calculating
    elasticity curves, and returning eligible or ineligible Pricing current/history documents.
    """
    run_time = datetime.utcnow()
    model_version = "1.0.0-mock"
    bound_pct = settings.PRICING_BOUND_PCT

    # Extract all distinct positive prices from processed sales history
    historical_prices = set(
        round(item.selling_price, 2) 
        for item in history 
        if item.selling_price is not None and item.selling_price > 0
    )

    if len(history) < 7:
        # Tier 1: Ineligible due to insufficient history (<7 days)
        eligibility_status = PricingEligibilityStatus.INSUFFICIENT_HISTORY
        eligibility_reason = f"Insufficient sales history. Only {len(history)} days of processed data available (minimum 7 required)."
        bound_range = None
        candidate_grid = None
        recommended_price = None
        expected_revenue = None
        elasticity_model_type = None

    elif len(historical_prices) <= 1:
        # Tier 2: Ineligible due to flat pricing (no variation to fit elasticity)
        eligibility_status = PricingEligibilityStatus.INSUFFICIENT_PRICE_VARIATION
        eligibility_reason = "No price variation detected in history. Elasticity models cannot estimate consumer responsiveness."
        bound_range = None
        candidate_grid = None
        recommended_price = None
        expected_revenue = None
        elasticity_model_type = None

    else:
        # Tier 3: Eligible
        eligibility_status = PricingEligibilityStatus.ELIGIBLE
        eligibility_reason = None
        elasticity_model_type = "Linear Elasticity Mock"

        # Define bounds: intersection of ±bound_pct around current price
        min_bound = max(0.01, round(current_price * (1 - bound_pct), 2))
        max_bound = round(current_price * (1 + bound_pct), 2)
        bound_range = BoundRange(min=min_bound, max=max_bound)

        # Generate exactly 5 candidate grid entries (centered on current_price)
        multipliers = [0.8, 0.9, 1.0, 1.1, 1.2]
        candidates = sorted(list(set(max(min_bound, min(max_bound, round(current_price * m, 2))) for m in multipliers)))
        
        # In case multipliers created fewer than 5 unique prices due to float rounding on tiny prices:
        while len(candidates) < 5:
            # Shift slightly
            candidates.append(round(candidates[-1] + 0.05, 2))
        candidates = sorted(candidates[:5])

        # Simple linear demand elasticity simulation:
        # E.g. base demand is the mean of the last 7 days
        last_7_sales = history[-7:]
        base_demand = sum(item.quantity_sold for item in last_7_sales) / len(last_7_sales) if last_7_sales else 1.0
        elasticity = 1.5 # 1.5% demand drop for each 1% price increase

        candidate_grid = []
        for P in candidates:
            pct_price_change = (P - current_price) / current_price if current_price > 0 else 0.0
            est_demand = max(0.0, base_demand * (1 - elasticity * pct_price_change))
            est_rev = P * est_demand
            
            candidate_grid.append(
                CandidateGridEntry(
                    candidate_price=P,
                    estimated_demand=round(est_demand, 2),
                    estimated_revenue=round(est_rev, 2)
                )
            )

        # Select the price candidate maximizing expected revenue
        winning_candidate = max(candidate_grid, key=lambda x: x.estimated_revenue)
        recommended_price = winning_candidate.candidate_price
        expected_revenue = winning_candidate.estimated_revenue

    # Instantiate Beanie documents
    current_doc = PricingCurrentDocument(
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

    history_doc = PricingHistoryDocument(
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
