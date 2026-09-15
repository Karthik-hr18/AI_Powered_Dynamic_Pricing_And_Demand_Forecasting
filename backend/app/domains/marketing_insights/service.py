import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from beanie import PydanticObjectId

from app.core.config import settings
from app.domains.marketing_insights.schemas import (
    AudienceProfile,
    CompetitorBenchmarkRow,
    CompetitorBenchmarkSection,
    DailySalesTrendPoint,
    ExpectedImpact30d,
    GenerationMode,
    MarketingInsightsResponse,
    MarketingRecommendation,
    PriceBucketPoint,
    PricePsychology,
    PromotionTiming,
    RiskWatchout,
    WeekdaySalesPoint,
)
from app.domains.pricing.models import PricingCurrentDocument
from app.domains.products.models import ProductDocument
from app.domains.sales_data.models import ProcessedSaleDocument, RawSaleDocument
from app.domains.uploads.models import UploadDocument

logger = logging.getLogger("app.domains.marketing_insights.service")

# In-memory insights cache: {cache_key: (MarketingInsightsResponse, cached_at)}
_INSIGHTS_CACHE: Dict[str, Tuple[MarketingInsightsResponse, datetime]] = {}
_CACHE_TTL_HOURS = 24

WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


async def get_product_marketing_insights(
    retailer_id: PydanticObjectId,
    product_id: PydanticObjectId,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> MarketingInsightsResponse:
    """
    Computes real transactional telemetry for a SKU and generates structured marketing
    insights via LLM (or deterministic rule-based heuristic engine with truthful badges).
    """
    # 1. Fetch Product metadata
    product = await ProductDocument.find_one(
        ProductDocument.id == product_id,
        ProductDocument.retailer_id == retailer_id,
    )
    if not product:
        raise ValueError(f"Product with ID {product_id} not found or not owned by retailer.")

    sku = product.sku
    sku_display = product.sku_display or sku.upper()
    product_name = product.product_name or sku_display
    category = product.category or "General Merchandise"

    # 2. Check latest upload ID to form cache key (upload-driven invalidation)
    latest_upload = await UploadDocument.find(
        UploadDocument.retailer_id == retailer_id
    ).sort("-created_at").first_or_none()
    latest_upload_id = str(latest_upload.id) if latest_upload else "no_upload"

    # 3. Determine Date Window
    now = datetime.now(timezone.utc)
    
    # Check latest sale date in DB to anchor default window
    latest_sale = await RawSaleDocument.find(
        RawSaleDocument.retailer_id == retailer_id,
        RawSaleDocument.product_id == product_id,
    ).sort("-date").first_or_none()
    
    if not latest_sale:
        latest_sale = await ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == retailer_id,
            ProcessedSaleDocument.product_id == product_id,
        ).sort("-date").first_or_none()

    anchor_dt = latest_sale.date if latest_sale else now
    
    if end_date:
        try:
            parsed_end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            if parsed_end.tzinfo is None:
                parsed_end = parsed_end.replace(tzinfo=timezone.utc)
            end_dt = parsed_end
        except Exception:
            end_dt = anchor_dt
    else:
        end_dt = anchor_dt

    if start_date:
        try:
            parsed_start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if parsed_start.tzinfo is None:
                parsed_start = parsed_start.replace(tzinfo=timezone.utc)
            start_dt = parsed_start
        except Exception:
            start_dt = end_dt - timedelta(days=29)
    else:
        start_dt = end_dt - timedelta(days=29)

    # Normalize to start-of-day and end-of-day (both naive and timezone-aware friendly)
    start_datetime = datetime(start_dt.year, start_dt.month, start_dt.day, 0, 0, 0)
    end_datetime = datetime(end_dt.year, end_dt.month, end_dt.day, 23, 59, 59, 999999)

    start_date_str = start_datetime.strftime("%Y-%m-%d")
    end_date_str = end_datetime.strftime("%Y-%m-%d")

    cache_key = f"{retailer_id}_{product_id}_{start_date_str}_{end_date_str}_{latest_upload_id}"

    # Check cache
    if cache_key in _INSIGHTS_CACHE:
        cached_resp, cached_time = _INSIGHTS_CACHE[cache_key]
        if (now - cached_time).total_seconds() < _CACHE_TTL_HOURS * 3600:
            cached_resp.is_cached = True
            return cached_resp

    # 4. Fetch Real Transactional Sales for Date Range (prioritize RawSaleDocument)
    raw_records = await RawSaleDocument.find(
        RawSaleDocument.retailer_id == retailer_id,
        RawSaleDocument.product_id == product_id,
        RawSaleDocument.date >= start_datetime,
        RawSaleDocument.date <= end_datetime,
    ).sort("date").to_list()

    if not raw_records or sum(r.quantity_sold for r in raw_records) == 0:
        sales_records = await ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == retailer_id,
            ProcessedSaleDocument.product_id == product_id,
            ProcessedSaleDocument.date >= start_datetime,
            ProcessedSaleDocument.date <= end_datetime,
        ).sort("date").to_list()
    else:
        sales_records = []

    # 5. Fetch Pricing Current state for Elasticity & Recommended Price
    pricing_current = await PricingCurrentDocument.find_one(
        PricingCurrentDocument.retailer_id == retailer_id,
        PricingCurrentDocument.product_id == product_id,
    )

    # --------------------------------------------------------------------------
    # 6. Compute Real Data Aggregates
    # --------------------------------------------------------------------------
    
    # 6.1 Daily Sales Trend (30-day timeline)
    daily_map: Dict[str, Dict[str, Any]] = {}
    active_records = raw_records if (raw_records and sum(r.quantity_sold for r in raw_records) > 0) else sales_records
    
    for r in active_records:
        d_str = r.date.strftime("%Y-%m-%d")
        price = float(r.selling_price) if r.selling_price is not None else 0.0
        qty = int(r.quantity_sold) if r.quantity_sold is not None else 0
        if d_str not in daily_map:
            daily_map[d_str] = {"units": 0, "revenue": 0.0, "prices": []}
        daily_map[d_str]["units"] += qty
        daily_map[d_str]["revenue"] += float(qty * price)
        if price > 0:
            daily_map[d_str]["prices"].append(price)

    sales_trend_30d: List[DailySalesTrendPoint] = []
    num_days = max(1, (end_datetime.date() - start_datetime.date()).days + 1)
    
    for i in range(num_days):
        cur_date = start_datetime.date() + timedelta(days=i)
        cur_str = cur_date.strftime("%Y-%m-%d")
        agg = daily_map.get(cur_str, {"units": 0, "revenue": 0.0, "prices": []})
        avg_p = (sum(agg["prices"]) / len(agg["prices"])) if agg["prices"] else (pricing_current.current_price if pricing_current and pricing_current.current_price else getattr(product, "current_price", 100.0) or 100.0)
        
        sales_trend_30d.append(
            DailySalesTrendPoint(
                date=cur_str,
                units_sold=agg["units"],
                revenue=round(agg["revenue"], 2),
                avg_selling_price=round(avg_p, 2),
            )
        )

    # 6.2 Day of Week Breakdown (Normalized strictly to 0=Mon .. 6=Sun)
    # Weekday array initialized for Mon (0) through Sun (6)
    weekday_units = [0] * 7
    weekday_rev = [0.0] * 7
    weekday_counts = [0] * 7

    for pt in sales_trend_30d:
        dt = datetime.strptime(pt.date, "%Y-%m-%d")
        # Python dt.weekday() returns 0 for Monday and 6 for Sunday
        dow = dt.weekday()
        weekday_units[dow] += pt.units_sold
        weekday_rev[dow] += pt.revenue
        weekday_counts[dow] += 1

    total_units_period = sum(weekday_units)
    total_rev_period = sum(weekday_rev)

    sales_by_day_of_week: List[WeekdaySalesPoint] = []
    for dow in range(7):
        cnt = max(1, weekday_counts[dow])
        u = weekday_units[dow]
        r = weekday_rev[dow]
        sales_by_day_of_week.append(
            WeekdaySalesPoint(
                day_of_week=dow,
                day_name=WEEKDAY_NAMES[dow],
                total_units_sold=u,
                avg_units_per_day=round(u / cnt, 1),
                revenue_share_pct=round((r / total_rev_period * 100), 1) if total_rev_period > 0 else round(100.0 / 7, 1),
            )
        )

    # 6.3 Sales by Price Range Buckets
    # Gather all transaction price points from active records
    price_points: List[Tuple[float, int]] = []
    for r in active_records:
        if r.selling_price and r.selling_price > 0 and r.quantity_sold and r.quantity_sold > 0:
            price_points.append((float(r.selling_price), int(r.quantity_sold)))

    current_price = (
        (pricing_current.current_price if pricing_current and pricing_current.current_price else None)
        or (getattr(product, "current_price", None))
        or (price_points[-1][0] if price_points else None)
        or 100.0
    )

    if not price_points:
        price_points = [(current_price, max(1, total_units_period))]

    all_prices = [p for p, _ in price_points]
    min_p = min(all_prices)
    max_p = max(all_prices)

    sales_by_price_range: List[PriceBucketPoint] = []
    if min_p == max_p or (max_p - min_p) < 1.0:
        # Flat price history: create relative promotional/discount bands
        p_base = min_p
        b1_max = round(p_base * 0.90, 2)
        b2_max = round(p_base * 1.02, 2)
        
        sales_by_price_range = [
            PriceBucketPoint(
                bucket_label=f"Promotional (< ₹{int(b1_max)})",
                min_price=0.0,
                max_price=b1_max,
                units_sold=0,
                revenue=0.0,
                percentage_of_total=0.0,
            ),
            PriceBucketPoint(
                bucket_label=f"Standard (₹{int(b1_max)} - ₹{int(b2_max)})",
                min_price=b1_max,
                max_price=b2_max,
                units_sold=total_units_period,
                revenue=round(total_rev_period, 2),
                percentage_of_total=100.0 if total_units_period > 0 else 100.0,
            ),
            PriceBucketPoint(
                bucket_label=f"Premium (> ₹{int(b2_max)})",
                min_price=b2_max,
                max_price=round(b2_max * 1.5, 2),
                units_sold=0,
                revenue=0.0,
                percentage_of_total=0.0,
            ),
        ]
    else:
        # Dynamic 3-tier histogram based on actual variance
        spread = max_p - min_p
        t1 = round(min_p + spread / 3, 2)
        t2 = round(min_p + (2 * spread) / 3, 2)
        
        b1_units = sum(qty for p, qty in price_points if p <= t1)
        b2_units = sum(qty for p, qty in price_points if t1 < p <= t2)
        b3_units = sum(qty for p, qty in price_points if p > t2)
        
        b1_rev = sum(p * qty for p, qty in price_points if p <= t1)
        b2_rev = sum(p * qty for p, qty in price_points if t1 < p <= t2)
        b3_rev = sum(p * qty for p, qty in price_points if p > t2)
        
        tot_u = max(1, b1_units + b2_units + b3_units)
        
        sales_by_price_range = [
            PriceBucketPoint(
                bucket_label=f"Discount (₹{int(min_p)} - ₹{int(t1)})",
                min_price=min_p,
                max_price=t1,
                units_sold=b1_units,
                revenue=round(b1_rev, 2),
                percentage_of_total=round((b1_units / tot_u) * 100, 1),
            ),
            PriceBucketPoint(
                bucket_label=f"Regular (₹{int(t1)} - ₹{int(t2)})",
                min_price=t1,
                max_price=t2,
                units_sold=b2_units,
                revenue=round(b2_rev, 2),
                percentage_of_total=round((b2_units / tot_u) * 100, 1),
            ),
            PriceBucketPoint(
                bucket_label=f"Peak (₹{int(t2)} - ₹{int(max_p)})",
                min_price=t2,
                max_price=max_p,
                units_sold=b3_units,
                revenue=round(b3_rev, 2),
                percentage_of_total=round((b3_units / tot_u) * 100, 1),
            ),
        ]

    # 6.4 Price Psychology
    original_price = getattr(product, "original_price", None) or max_p
    if original_price < current_price:
        original_price = round(current_price * 1.15, 2)
    
    discount_pct = round(((original_price - current_price) / original_price) * 100, 1) if original_price > 0 else 0.0
    charm_pricing_flag = str(round(current_price, 2)).endswith(".99") or str(round(current_price, 2)).endswith(".95") or str(int(current_price)).endswith("9")
    
    recommended_price = pricing_current.recommended_price if pricing_current else None
    
    if discount_pct >= 15:
        positioning_note = f"High promotional discount of {discount_pct}%. Drives strong conversion velocity but watch gross margins."
    elif charm_pricing_flag:
        positioning_note = "Leverages psychological charm pricing threshold. Reduces purchase hesitation among value shoppers."
    elif recommended_price and recommended_price > current_price:
        positioning_note = f"Priced below AI optimal ceiling (₹{recommended_price:.2f}). Inelastic demand allows for +{round(((recommended_price-current_price)/current_price)*100,1)}% margin gain."
    else:
        positioning_note = "Standard competitive pricing baseline aligned with category willingness-to-pay."

    price_psychology = PricePsychology(
        original_price=round(original_price, 2),
        current_price=round(current_price, 2),
        discount_pct=discount_pct,
        positioning_note=positioning_note,
        charm_pricing_flag=charm_pricing_flag,
        price_elasticity_score=1.2,
    )

    # --------------------------------------------------------------------------
    # 7. Generate Strategic Sections (Single Structured LLM Pass or Deterministic Rule Engine)
    # --------------------------------------------------------------------------
    
    # Check if LLM endpoint is configured
    use_llm = bool(
        settings.HF_API_URL
        and "placeholder" not in settings.HF_API_URL
        and settings.HF_API_TOKEN
        and "placeholder" not in settings.HF_API_TOKEN
    )

    gen_mode = GenerationMode.RULE_BASED_FALLBACK
    data_source = "Deterministic Rule-based Heuristic"

    recommendations: List[MarketingRecommendation] = []
    promotion_timing: Optional[PromotionTiming] = None
    audience_profile: Optional[AudienceProfile] = None
    competitor_benchmark: Optional[CompetitorBenchmarkSection] = None
    risks_watchouts: List[RiskWatchout] = []
    expected_impact_30d: Optional[ExpectedImpact30d] = None

    # Summary payload passed to LLM if enabled
    context_summary = {
        "product_name": product_name,
        "sku": sku_display,
        "category": category,
        "current_price": current_price,
        "original_price": original_price,
        "discount_pct": discount_pct,
        "total_units_30d": total_units_period,
        "total_revenue_30d": total_rev_period,
        "recommended_price": recommended_price,
        "weekday_distribution": {w.day_name: w.total_units_sold for w in sales_by_day_of_week},
    }

    if use_llm:
        try:
            logger.info(f"Issuing structured Marketing Insights prompt to HuggingFace / LLM: {settings.HF_API_URL}")
            llm_res = _call_llm_structured_insights(context_summary)
            if llm_res:
                recommendations = [MarketingRecommendation(**r) for r in llm_res.get("recommendations", [])]
                promotion_timing = PromotionTiming(**llm_res.get("promotion_timing", {}))
                audience_profile = AudienceProfile(**llm_res.get("audience_profile", {}))
                
                comp_data = llm_res.get("competitor_benchmark", {})
                competitor_benchmark = CompetitorBenchmarkSection(
                    overall_position=comp_data.get("overall_position", "COMPETITIVE"),
                    rows=[CompetitorBenchmarkRow(**row) for row in comp_data.get("rows", [])],
                    disclaimer="AI-Estimated Reference Range. Figures are indicative market simulations and not verified live supplier feeds.",
                    source_type="ESTIMATED",
                )
                
                risks_watchouts = [RiskWatchout(**rw) for rw in llm_res.get("risks_watchouts", [])]
                expected_impact_30d = ExpectedImpact30d(**llm_res.get("expected_impact_30d", {}))
                
                gen_mode = GenerationMode.LLM_GENERATED
                data_source = "AI Model (LLM Inference)"
        except Exception as llm_err:
            logger.warning(f"LLM generation failed, falling back to deterministic rule engine: {llm_err}")
            use_llm = False

    if not use_llm or not recommendations:
        # ----------------------------------------------------------------------
        # Deterministic Rule-Based Semantic Inference Engine
        # ----------------------------------------------------------------------
        gen_mode = GenerationMode.RULE_BASED_FALLBACK
        data_source = "Deterministic Rule-based Heuristic"
        
        # Calculate Weekend vs Weekday velocity
        weekend_units = sales_by_day_of_week[5].total_units_sold + sales_by_day_of_week[6].total_units_sold
        weekday_units_sum = sum(sales_by_day_of_week[i].total_units_sold for i in range(5))
        
        avg_weekend_daily = weekend_units / 2.0
        avg_weekday_daily = weekday_units_sum / 5.0

        # Peak weekdays detection
        sorted_weekdays = sorted(sales_by_day_of_week, key=lambda w: w.total_units_sold, reverse=True)
        top_days = [w.day_name for w in sorted_weekdays[:2]]

        # 1. Recommendations Engine
        recommendations = []
        if avg_weekend_daily >= (avg_weekday_daily * 1.20):
            recommendations.append(
                MarketingRecommendation(
                    id="rec-1",
                    title="Weekend Surge Visibility Campaign",
                    impact="HIGH",
                    category="Promotion",
                    description=f"Weekend sales velocity ({avg_weekend_daily:.1f} units/day) outpaces weekdays by {round(((avg_weekend_daily-avg_weekday_daily)/max(1,avg_weekday_daily))*100)}%.",
                    actionable_step="Schedule app push notifications and prime storefront placement on Friday evenings.",
                    action_summary=f"Weekend sales ({avg_weekend_daily:.1f} units/day) surge above weekdays. Maximize customer footfall with prominent display placement.",
                    channel="Storefront & App Push",
                    timing="Friday Eve - Sunday",
                    expected_outcome="+18-25% Weekend Volume",
                )
            )
        elif avg_weekday_daily >= (avg_weekend_daily * 1.20):
            recommendations.append(
                MarketingRecommendation(
                    id="rec-1",
                    title="Mid-Week Staples Bundle Promotion",
                    impact="HIGH",
                    category="Promotion",
                    description=f"Weekday purchasing ({avg_weekday_daily:.1f} units/day) dominates this SKU's demand curve.",
                    actionable_step="Introduce Tuesday-Thursday combo discounts to capture planned pantry restocking.",
                    action_summary=f"Weekday purchasing ({avg_weekday_daily:.1f} units/day) dominates demand. Drive mid-week ticket size with pantry restocking bundles.",
                    channel="WhatsApp & In-Store Aisle",
                    timing="Tuesday - Thursday",
                    expected_outcome="+12-18% Basket Size",
                )
            )
        else:
            recommendations.append(
                MarketingRecommendation(
                    id="rec-1",
                    title="Consistent Multi-Day Retargeting",
                    impact="HIGH",
                    category="Promotion",
                    description="Demand is evenly distributed across all 7 days of the week.",
                    actionable_step="Maintain always-on baseline visibility without concentrating ad spend on single days.",
                    action_summary="Demand is steady across all 7 days. Maintain continuous visibility and prominent shelf space.",
                    channel="Digital Shelf & POS Display",
                    timing="All Week (Mon-Sun)",
                    expected_outcome="+10-15% Steady Velocity",
                )
            )

        if recommended_price and recommended_price > current_price:
            diff_pct = round(((recommended_price - current_price) / current_price) * 100, 1)
            recommendations.append(
                MarketingRecommendation(
                    id="rec-2",
                    title="Margin Expansion Opportunity",
                    impact="HIGH",
                    category="Pricing",
                    description=f"Low price elasticity indicates room to adjust price from ₹{current_price:.2f} to ₹{recommended_price:.2f} (+{diff_pct}%).",
                    actionable_step="Increase price in gradual 2-3% weekly steps while monitoring weekly unit velocity.",
                    action_summary=f"Low consumer price sensitivity permits adjusting price to ₹{recommended_price:.2f} to expand gross margins.",
                    channel="Catalog Price Update",
                    timing="Next Weekly Cycle",
                    expected_outcome=f"+{diff_pct}% Gross Margin",
                )
            )
        elif recommended_price and recommended_price < current_price:
            diff_pct = round(((current_price - recommended_price) / current_price) * 100, 1)
            recommendations.append(
                MarketingRecommendation(
                    id="rec-2",
                    title="Volume Acceleration Discount",
                    impact="HIGH",
                    category="Pricing",
                    description=f"Model elasticity shows unit volume will expand significantly at the target price point of ₹{recommended_price:.2f}.",
                    actionable_step="Launch a 14-day promotional flash sale at recommended price to accelerate inventory turns.",
                    action_summary=f"Reposition price to optimal ₹{recommended_price:.2f} (-{diff_pct}%) to unlock elastic demand expansion.",
                    channel="Flash Discount & Shelf Tag",
                    timing="Next 14 Days",
                    expected_outcome="+22-30% Volume Uptake",
                )
            )
        else:
            recommendations.append(
                MarketingRecommendation(
                    id="rec-2",
                    title="Cross-Sell & Product Kitting",
                    impact="MEDIUM",
                    category="Merchandising",
                    description=f"Bundle this {category} item with complementary fast-moving products.",
                    actionable_step="Display 'Frequently Bought Together' bundles at checkout with a 5% bundle discount.",
                    action_summary=f"Bundle this item with high-frequency staples to increase multi-item order rates.",
                    channel="Checkout & Digital Cart",
                    timing="Continuous",
                    expected_outcome="+14% Cross-Sell Conversion",
                )
            )

        recommendations.append(
            MarketingRecommendation(
                id="rec-3",
                title="Loyalty Tier Early-Access Special",
                impact="MEDIUM",
                category="Retention",
                description="Reward high-frequency buyers with exclusive member pricing or bonus reward points.",
                actionable_step="Activate 2x loyalty points for repeat purchasers of this product SKU.",
                action_summary="Reward frequent buyers with exclusive points multiplier to build brand lock-in.",
                channel="SMS & Loyalty Program",
                timing="Month-End (25th - 5th)",
                expected_outcome="+20% Repeat Purchase Rate",
            )
        )

        # 2. Promotion Timing
        promotion_timing = PromotionTiming(
            best_days=top_days if top_days else ["Friday", "Saturday"],
            best_time_window="10:00 AM - 1:00 PM & 6:00 PM - 9:00 PM",
            peak_season="Festival Months & Month-End Paydays (28th - 5th)",
            promo_velocity_multiplier=1.35 if avg_weekend_daily > avg_weekday_daily else 1.20,
            timing_rationale=f"Peak purchasing clusters heavily around {', '.join(top_days)}. Aligning ad budget with these windows yields 30%+ higher ROAS.",
        )

        # 3. Audience Profile (Category Demographic Matrix)
        cat_lower = category.lower()
        if any(k in cat_lower for k in ["snack", "beverage", "soft drink", "biscuit", "instant"]):
            audience_profile = AudienceProfile(
                primary_users="Young Adults, Students & Working Professionals",
                age_group="18 - 34 years",
                location_tier="Metro & Tier 1/2 Urban Centres",
                interests=["Quick snacks", "Impulse refreshments", "On-the-go snacking", "Convenience foods"],
                purchase_triggers=["Evening cravings", "Social gatherings", "Instant gratification", "Bundle offers"],
                persona_summary="High-velocity impulse buyers who prioritize instant availability, brand familiarity, and value pack sizes.",
            )
        elif any(k in cat_lower for k in ["staple", "flour", "rice", "oil", "dal", "grocery", "provision"]):
            audience_profile = AudienceProfile(
                primary_users="Household Decision Makers & Families",
                age_group="28 - 55 years",
                location_tier="All Tiers (Urban & Semi-Urban)",
                interests=["Home cooking", "Pantry staples", "Bulk savings", "Nutritional value"],
                purchase_triggers=["Monthly pantry restocking", "Payday grocery runs", "Bulk volume discounts"],
                persona_summary="Planned value-focused shoppers seeking consistent quality, trusted purity, and bulk quantity savings.",
            )
        elif any(k in cat_lower for k in ["personal", "care", "beauty", "cosmetic", "soap", "shampoo"]):
            audience_profile = AudienceProfile(
                primary_users="Health & Grooming Conscious Individuals",
                age_group="20 - 45 years",
                location_tier="Tier 1 & Tier 2 Cities",
                interests=["Personal wellness", "Skin & hair care", "Premium grooming", "Organic products"],
                purchase_triggers=["Self-care routines", "Influencer recommendations", "Brand loyalty discounts"],
                persona_summary="Discerning consumers sensitive to product ingredients, brand reputation, and hygiene efficacy.",
            )
        else:
            audience_profile = AudienceProfile(
                primary_users="General Retail Consumers & Regular Shoppers",
                age_group="22 - 50 years",
                location_tier="Urban & Suburban Markets",
                interests=["Daily essentials", "Value for money", "Household utility"],
                purchase_triggers=["Need-based replenishment", "Store promotions", "Seasonal deals"],
                persona_summary="Practical retail buyers balancing price sensitivity with quality consistency.",
            )

        # 4. Competitor Price Benchmark (Explicitly labeled AI/Rule-based Estimate)
        c_price = current_price
        competitor_benchmark = CompetitorBenchmarkSection(
            overall_position="COMPETITIVE" if discount_pct > 5 else "PREMIUM",
            rows=[
                CompetitorBenchmarkRow(
                    competitor_name="Local Supermart Express",
                    estimated_price=round(c_price * 1.05, 2),
                    price_difference_pct=5.0,
                    positioning="ABOVE",
                    is_verified=False,
                    source_type="ESTIMATED",
                ),
                CompetitorBenchmarkRow(
                    competitor_name="QuickCommerce Instant Hub",
                    estimated_price=round(c_price * 1.08, 2),
                    price_difference_pct=8.0,
                    positioning="ABOVE",
                    is_verified=False,
                    source_type="ESTIMATED",
                ),
                CompetitorBenchmarkRow(
                    competitor_name="Regional Wholesale Mart",
                    estimated_price=round(c_price * 0.94, 2),
                    price_difference_pct=-6.0,
                    positioning="BELOW",
                    is_verified=False,
                    source_type="ESTIMATED",
                ),
            ],
            disclaimer="Rule-Based Market Simulation. Benchmark estimates are generated for strategic guidance and do not represent verified live competitor feeds.",
            source_type="ESTIMATED",
        )

        # 5. Risks & Watchouts
        risks_watchouts = []
        if discount_pct >= 20:
            risks_watchouts.append(
                RiskWatchout(
                    severity="WARNING",
                    title="Deep Discount Margin Dilution",
                    description=f"Current {discount_pct}% discount creates consumer price-anchor dependency.",
                    mitigation="Gradually shift from percentage markdowns to value-add gift bundles.",
                )
            )
        if total_units_period < 15:
            risks_watchouts.append(
                RiskWatchout(
                    severity="WARNING",
                    title="Low Sample Size & Velocity",
                    description="Limited 30-day transactional velocity reduces forecast confidence score.",
                    mitigation="Run a targeted weekend sampling campaign to collect velocity baseline.",
                )
            )
        risks_watchouts.append(
            RiskWatchout(
                severity="WARNING",
                title="Competitor Price Under-cutting",
                description="Nearby discount formats may match promotional prices within 48-72 hours.",
                mitigation="Focus marketing messaging on freshness, instant availability, and local trust.",
            )
        )
        risks_watchouts.append(
            RiskWatchout(
                severity="INFO",
                title="Inventory Buffer & Stockout Exposure",
                description="Promotional surges can exhaust safety stock if replenishment lead time exceeds 4 days.",
                mitigation="Review inventory health drawer and set auto-reorder triggers prior to ad launch.",
            )
        )

        # 6. Expected 30-Day Impact
        expected_impact_30d = ExpectedImpact30d(
            revenue_uplift_pct_range="+6.5% to +12.0%",
            units_sold_range=f"+{max(10, int(total_units_period * 0.15))} to +{max(25, int(total_units_period * 0.28))} units",
            conversion_rate_range="3.8% → 4.9%",
            roi_range="2.8x - 3.6x ROAS",
            summary_note="Executing recommended weekend promotions and dynamic price points projected to drive incremental margin.",
        )

    response = MarketingInsightsResponse(
        product_id=product_id,
        sku=sku,
        sku_display=sku_display,
        product_name=product_name,
        category=category,
        start_date=start_date_str,
        end_date=end_date_str,
        generation_mode=gen_mode,
        data_source=data_source,
        cached_at=now,
        is_cached=False,
        price_psychology=price_psychology,
        sales_trend_30d=sales_trend_30d,
        sales_by_day_of_week=sales_by_day_of_week,
        sales_by_price_range=sales_by_price_range,
        recommendations=recommendations,
        promotion_timing=promotion_timing,
        audience_profile=audience_profile,
        competitor_benchmark=competitor_benchmark,
        risks_watchouts=risks_watchouts,
        expected_impact_30d=expected_impact_30d,
    )

    # Store in cache
    _INSIGHTS_CACHE[cache_key] = (response, now)
    return response


def _call_llm_structured_insights(context: dict) -> Optional[dict]:
    """
    Calls configured Hugging Face Inference Endpoint or structured LLM API
    with a single structured prompt requesting schema-compliant JSON.
    """
    if not settings.HF_API_URL or not settings.HF_API_TOKEN:
        return None

    prompt = (
        "You are an expert retail marketing strategist and pricing analyst. "
        "Analyze the following real product sales metrics and return a structured JSON response:\n\n"
        f"{json.dumps(context, indent=2)}\n\n"
        "Return a JSON object strictly matching this schema with no conversational markdown or extra text:\n"
        "{\n"
        '  "recommendations": [{"id": "rec-1", "title": "...", "impact": "HIGH", "category": "Promotion", "description": "...", "actionable_step": "..."}],\n'
        '  "promotion_timing": {"best_days": ["Fri", "Sat"], "best_time_window": "...", "peak_season": "...", "promo_velocity_multiplier": 1.3, "timing_rationale": "..."},\n'
        '  "audience_profile": {"primary_users": "...", "age_group": "...", "location_tier": "...", "interests": ["..."], "purchase_triggers": ["..."], "persona_summary": "..."},\n'
        '  "competitor_benchmark": {"overall_position": "COMPETITIVE", "rows": [{"competitor_name": "...", "estimated_price": 100.0, "price_difference_pct": 5.0, "positioning": "ABOVE", "is_verified": false}]},\n'
        '  "risks_watchouts": [{"severity": "WARNING", "title": "...", "description": "...", "mitigation": "..."}],\n'
        '  "expected_impact_30d": {"revenue_uplift_pct_range": "+8% - +14%", "units_sold_range": "+100 - +150 units", "conversion_rate_range": "3.5% - 4.8%", "roi_range": "3.0x - 4.2x", "summary_note": "..."}\n'
        "}"
    )

    headers = {
        "Authorization": f"Bearer {settings.HF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "task": "marketing_insights",
        "prompt": prompt,
        "context": context,
    }

    with httpx.Client(timeout=15.0) as client:
        res = client.post(settings.HF_API_URL, json=payload, headers=headers)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, dict) and "recommendations" in data:
                return data
            elif isinstance(data, dict) and "generated_text" in data:
                # Parse embedded JSON string
                raw_txt = data["generated_text"]
                start_idx = raw_txt.find("{")
                end_idx = raw_txt.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    return json.loads(raw_txt[start_idx : end_idx + 1])
    return None
