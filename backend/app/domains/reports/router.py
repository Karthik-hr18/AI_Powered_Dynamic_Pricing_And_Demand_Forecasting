from fastapi import APIRouter, Depends, Response, status

from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import UserDocument
from app.domains.reports.service import generate_retailer_pdf_report

router = APIRouter()

@router.get(
    "/pdf",
    status_code=status.HTTP_200_OK,
    summary="Download 10-Page Executive PDF Analytics Report",
)
async def download_pdf_report(
    user: UserDocument = Depends(get_current_user),
):
    """
    Generates and streams a professional 10-page executive PDF report for the authenticated retailer.
    """
    pdf_bytes, filename = await generate_retailer_pdf_report(user)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
