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


class DashboardOverviewResponse(BaseModel):
    """The master aggregated response structure for the landing overview page."""
    kpis: KpiMetrics
    forecast_vs_actual: List[ForecastVsActualPoint]
    product_table: List[DashboardProductRow]
