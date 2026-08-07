from datetime import datetime
from typing import Dict, List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field


class KpiMetrics(BaseModel):
    """High-level dashboard KPIs calculated over the trailing 30-day window."""
    total_revenue_30d: float = Field(default=0.0)
    total_units_30d: float = Field(default=0.0)
    avg_price_30d: float = Field(default=0.0)
    active_alerts_count: int = Field(default=0)
    confidence_breakdown: Dict[str, int] = Field(default_factory=dict)
    revenue_growth_pct: float = Field(default=0.0)
    potential_revenue_gain: float = Field(default=0.0)
    potential_revenue_gain_pct: float = Field(default=0.0)


class BusinessHealthMetric(BaseModel):
    score: int = Field(default=92)
    rating: str = Field(default="Excellent")
    trend_delta: int = Field(default=6)


class GoalProgressMetric(BaseModel):
    target_revenue: float = Field(default=50000.0)
    current_revenue: float = Field(default=0.0)
    progress_pct: float = Field(default=0.0)
    baseline_monthly_profit: float = Field(default=0.0)
    projected_monthly_profit: float = Field(default=0.0)
    profit_expansion_pct: float = Field(default=0.0)


class HighestOpportunity(BaseModel):
    sku: Optional[str] = None
    product_name: Optional[str] = None
    action_label: Optional[str] = None
    current_price: Optional[float] = None
    recommended_price: Optional[float] = None
    expected_revenue_gain: float = Field(default=0.0)
    confidence_score: float = Field(default=0.0)


class DataQualityAudit(BaseModel):
    total_rows: int = Field(default=0)
    duplicates_count: int = Field(default=0)
    missing_values_count: int = Field(default=0)
    quality_score_pct: float = Field(default=100.0)


class SystemStatusInfo(BaseModel):
    backend_status: str = Field(default="Running")
    mongo_status: str = Field(default="Connected")
    pipeline_status: str = Field(default="Ready")
    last_run: Optional[str] = None


class CategoryPerformanceItem(BaseModel):
    category: str
    total_revenue: float
    units_sold: float


class ProductRankItem(BaseModel):
    sku: str
    product_name: str
    units_sold: float
    revenue: float


class InventoryHealthDistribution(BaseModel):
    healthy_pct: float = Field(default=80.0)
    risk_pct: float = Field(default=15.0)
    critical_pct: float = Field(default=5.0)


class ForecastVsActualPoint(BaseModel):
    """A daily data point comparing actual sales to past forecasted quantities."""
    date: datetime
    actual_units: float
    forecasted_units: float


class DashboardProductRow(BaseModel):
    """Product list item containing aggregated summary columns for the dashboard grid."""
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    sku: str
    sku_display: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    forecast_7d: Optional[float] = None
    recommended_price: Optional[float] = None
    inventory_status: str
    alert_status: bool


class LastUploadInfo(BaseModel):
    filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    total_rows: Optional[int] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class DashboardOverviewResponse(BaseModel):
    """The master aggregated response structure for the landing overview page."""
    kpis: KpiMetrics
    business_health: BusinessHealthMetric
    goal_progress: GoalProgressMetric
    highest_opportunity: Optional[HighestOpportunity] = None
    data_quality: DataQualityAudit
    system_status: SystemStatusInfo
    inventory_health: InventoryHealthDistribution
    category_performance: List[CategoryPerformanceItem] = Field(default_factory=list)
    top_sellers: List[ProductRankItem] = Field(default_factory=list)
    low_performers: List[ProductRankItem] = Field(default_factory=list)
    top_opportunities: List[HighestOpportunity] = Field(default_factory=list)
    critical_risks: List[Dict[str, str]] = Field(default_factory=list)
    last_upload: Optional[LastUploadInfo] = None
    forecast_vs_actual: List[ForecastVsActualPoint] = Field(default_factory=list)
    product_table: List[DashboardProductRow] = Field(default_factory=list)
