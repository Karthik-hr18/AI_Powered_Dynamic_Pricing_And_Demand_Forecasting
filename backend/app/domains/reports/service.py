from datetime import datetime
from beanie import PydanticObjectId

from app.domains.dashboard.service import get_dashboard_overview_data
from app.domains.reports.pdf_generator import build_analytics_pdf
from app.domains.auth.models import UserDocument

async def generate_retailer_pdf_report(user: UserDocument) -> tuple[bytes, str]:
    """
    Fetches retailer dashboard data and compiles a 10-page executive PDF report.
    Returns (pdf_bytes, filename).
    """
    # Reuse dashboard aggregation logic without duplicating code!
    dashboard_data = await get_dashboard_overview_data(retailer_id=user.id)
    data_dict = dashboard_data.model_dump()

    retailer_name = user.email
    business_name = user.business_name or "Demo Mart Premium Retailers"

    pdf_bytes = build_analytics_pdf(
        dashboard_data=data_dict,
        retailer_name=retailer_name,
        business_name=business_name,
    )

    date_str = datetime.utcnow().strftime("%Y_%m_%d")
    filename = f"Retail_Analytics_Report_{date_str}.pdf"

    return pdf_bytes, filename
