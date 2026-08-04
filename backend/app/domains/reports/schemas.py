from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ReportMetadataResponse(BaseModel):
    report_id: str
    retailer_name: str
    business_name: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    total_pages: int = 10
    version: str = "v1.0"
