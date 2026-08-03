from datetime import datetime
from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

from app.domains.forecasting.models import ForecastCurrentDocument
from app.domains.pricing.models import PricingCurrentDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument


class ProductResponse(BaseModel):
    """API response schema for Product metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: PydanticObjectId
    retailer_id: PydanticObjectId
    sku: str
    sku_display: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SparklinePoint(BaseModel):
    """Daily sales aggregation data point for historical trends."""
    date: datetime
    quantity_sold: float
    selling_price: float


class ProductSummaryResponse(BaseModel):
    """Fanned-out detailed summary endpoint response containing all pipeline current statuses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    product: ProductResponse
    forecast: Optional[ForecastCurrentDocument] = None
    pricing: Optional[PricingCurrentDocument] = None
    inventory: Optional[InventoryCurrentDocument] = None
    anomaly: Optional[AnomalyCurrentDocument] = None
    sparkline: List[SparklinePoint] = Field(default_factory=list)


class PaginatedProductsResponse(BaseModel):
    """Response payload for paginated product lists."""
    items: List[ProductResponse]
    total_count: int
    page: int
    limit: int
    pages_count: int
