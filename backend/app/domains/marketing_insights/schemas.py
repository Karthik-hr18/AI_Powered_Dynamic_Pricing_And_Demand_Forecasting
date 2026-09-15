from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class GenerationMode(str, Enum):
    LLM_GENERATED = "LLM_GENERATED"
    RULE_BASED_FALLBACK = "RULE_BASED_FALLBACK"


class PricePsychology(BaseModel):
    original_price: float
    current_price: float
    discount_pct: float
    positioning_note: str
    charm_pricing_flag: bool = False
    price_elasticity_score: Optional[float] = None


class DailySalesTrendPoint(BaseModel):
    date: str  # YYYY-MM-DD
    units_sold: int
    revenue: float
    avg_selling_price: float


class WeekdaySalesPoint(BaseModel):
    day_of_week: int  # 0 = Monday, 6 = Sunday (ISO standard)
    day_name: str  # "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
    total_units_sold: int
    avg_units_per_day: float
    revenue_share_pct: float


class PriceBucketPoint(BaseModel):
    bucket_label: str  # e.g. "Under ₹20", "₹20 - ₹40", "₹40+"
    min_price: float
    max_price: float
    units_sold: int
    revenue: float
    percentage_of_total: float


class MarketingRecommendation(BaseModel):
    id: str
    title: str
    impact: str = "HIGH"  # "HIGH" or "MEDIUM"
    category: str  # e.g. "Pricing", "Promotion", "Merchandising", "Cross-sell"
    description: str
    actionable_step: str
    action_summary: Optional[str] = None
    channel: Optional[str] = "Storefront & Digital"
    timing: Optional[str] = "Weekend Peak"
    expected_outcome: Optional[str] = "+15-20% Demand Uplift"


class PromotionTiming(BaseModel):
    best_days: List[str]
    best_time_window: str
    peak_season: str
    promo_velocity_multiplier: float
    timing_rationale: str


class AudienceProfile(BaseModel):
    primary_users: str
    age_group: str
    location_tier: str
    interests: List[str]
    purchase_triggers: List[str]
    persona_summary: str


class CompetitorBenchmarkRow(BaseModel):
    competitor_name: str
    estimated_price: float
    price_difference_pct: float
    positioning: str  # "ABOVE", "PAR", "BELOW"
    is_verified: bool = False
    source_type: str = "ESTIMATED"  # "ESTIMATED" or "MANUAL"


class CompetitorBenchmarkSection(BaseModel):
    overall_position: str  # "PREMIUM", "COMPETITIVE", "VALUE"
    rows: List[CompetitorBenchmarkRow]
    disclaimer: str
    source_type: str = "ESTIMATED"  # "ESTIMATED" or "MANUAL"


class RiskWatchout(BaseModel):
    severity: str = "WARNING"  # "WARNING" or "CRITICAL"
    title: str
    description: str
    mitigation: str


class ExpectedImpact30d(BaseModel):
    revenue_uplift_pct_range: str  # e.g. "+8% - +14%"
    units_sold_range: str  # e.g. "+120 - +180 units"
    conversion_rate_range: str  # e.g. "3.2% - 4.5%"
    roi_range: str  # e.g. "2.4x - 3.8x"
    summary_note: str


class MarketingInsightsResponse(BaseModel):
    product_id: PydanticObjectId
    sku: str
    sku_display: str
    product_name: str
    category: str
    start_date: str
    end_date: str
    generation_mode: GenerationMode
    data_source: str
    cached_at: datetime
    is_cached: bool = False
    
    # 1. Price Psychology (Computed + Positioned)
    price_psychology: PricePsychology
    
    # 2. Sales Trend (Computed Real Data)
    sales_trend_30d: List[DailySalesTrendPoint]
    
    # 3. Sales by Day of Week (Computed Real Data)
    sales_by_day_of_week: List[WeekdaySalesPoint]
    
    # 4. Sales by Price Range (Computed Real Data)
    sales_by_price_range: List[PriceBucketPoint]
    
    # 5. Top Marketing Recommendations (AI or Deterministic Heuristic)
    recommendations: List[MarketingRecommendation]
    
    # 6. Best Time to Promote (AI or Deterministic Heuristic)
    promotion_timing: PromotionTiming
    
    # 7. Inferred Audience Profile (AI or Deterministic Heuristic)
    audience_profile: AudienceProfile
    
    # 8. Competitor Price Benchmark (AI or Deterministic Heuristic with Disclaimer)
    competitor_benchmark: CompetitorBenchmarkSection
    
    # 9. Risks & Watchouts (AI or Deterministic Heuristic)
    risks_watchouts: List[RiskWatchout]
    
    # 10. Expected 30-Day Impact (AI or Deterministic Heuristic)
    expected_impact_30d: ExpectedImpact30d
