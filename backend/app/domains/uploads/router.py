import logging
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.core.config import settings
from app.core.constants import UploadStatus, UserRole
from app.domains.auth.dependencies import get_current_user
from app.domains.auth.models import UserDocument
from app.domains.uploads.schemas import UploadResponse
from app.domains.uploads.models import UploadDocument
from app.domains.uploads.service import create_upload_record, validate_csv_headers

logger = logging.getLogger("app.domains.uploads.router")

router = APIRouter()

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024 # 50 Megabytes


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a new sales CSV file for ingestion"
)
async def upload_sales_csv(
    file: UploadFile = File(...),
    schema_mapping_used: str = Form("standard"),
    current_user: UserDocument = Depends(get_current_user)
):
    """
    Accepts CSV uploads, writes files to local storage, runs header verification checks,
    and returns initial pending state before background worker starts parsing.
    """
    # 1. Enforce file extensions
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only CSV (.csv) files are permitted."
        )

    # 2. Insert PENDING tracking document in MongoDB
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is incomplete.")
    upload_doc = await create_upload_record(
        retailer_id=current_user.id,
        filename=file.filename,
        file_size=0, # Updated below after reading content
        mapping=schema_mapping_used
    )

    # 3. Stream write file contents to disk in chunks to handle memory safely
    os.makedirs(settings.UPLOAD_STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload_doc.upload_id}.csv")
    
    file_size = 0
    try:
        with open(filepath, "wb") as buffer:
            while chunk := await file.read(1024 * 1024): # Read in 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE_BYTES:
                    # Enforce file size bounds
                    buffer.close()
                    os.remove(filepath)
                    await upload_doc.delete()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="File size exceeds the maximum limit of 50MB."
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File system write failure during upload: {e}")
        await upload_doc.delete()
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to local disk: {str(e)}"
        )

    # Update actual saved size
    upload_doc.file_size_bytes = file_size
    await upload_doc.save()

    # 4. Perform immediate CSV header validations (fail-fast checks)
    validation_errors = validate_csv_headers(filepath)
    if validation_errors:
        upload_doc.status = UploadStatus.REJECTED
        upload_doc.validation_errors = validation_errors
        await upload_doc.save()
        
        # Keep rejected file on disk for forensics/auditing, but fail the request
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "msg": "CSV headers validation checks failed.",
                "errors": validation_errors,
                "upload_id": upload_doc.upload_id
            }
        )

    # Header check passed successfully; worker process can consume this file
    upload_doc.status = UploadStatus.UPLOADED
    await upload_doc.save()
    logger.info(f"File upload {upload_doc.upload_id} accepted and queued for worker ingestion.")
    return upload_doc


@router.get(
    "/",
    response_model=List[UploadResponse],
    status_code=status.HTTP_200_OK,
    summary="Get upload logs history"
)
async def list_uploads(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserDocument = Depends(get_current_user)
):
    """Retrieves paginated logs history of uploaded datasets for the logged-in retailer."""
    # Admins can view all history; Retailers can only view their own uploads
    query = {}
    if current_user.role != UserRole.ADMIN:
        query["retailer_id"] = current_user.id

    uploads = await UploadDocument.find(
        query
    ).sort(
        "-created_at"
    ).skip(
        offset
    ).limit(
        limit
    ).to_list()

    return uploads


@router.get(
    "/{upload_id}",
    response_model=UploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single upload details and status"
)
async def get_upload_status(
    upload_id: str,
    current_user: UserDocument = Depends(get_current_user)
):
    """Retrieves current processing stage, warnings, and record statistics of a single upload."""
    upload = await UploadDocument.find_one(UploadDocument.upload_id == upload_id)
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload job {upload_id} could not be found."
        )

    # Restrict read permissions to data owner or system admins
    if current_user.role != UserRole.ADMIN and upload.retailer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not own this upload record."
        )

    return upload
