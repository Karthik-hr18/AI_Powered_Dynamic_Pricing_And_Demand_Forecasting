import csv
import logging
import os
from typing import List

from beanie import PydanticObjectId

from app.core.config import settings
from app.domains.uploads.models import UploadDocument

logger = logging.getLogger("app.domains.uploads.service")


async def create_upload_record(
    retailer_id: PydanticObjectId,
    filename: str,
    file_size: int,
    mapping: str
) -> UploadDocument:
    """
    Creates and persists the initial UploadDocument tracker in MongoDB.
    """
    upload = UploadDocument(
        retailer_id=retailer_id,
        original_filename=filename,
        file_size_bytes=file_size,
        schema_mapping_used=mapping
    )
    await upload.insert()
    logger.info(f"Created uploads record tracker {upload.upload_id} for retailer {retailer_id}")
    return upload


def validate_csv_headers(filepath: str) -> List[str]:
    """
    Reads the header row of the CSV file on disk.
    Enforces the presence of the four mandatory fields: date, sku, quantity_sold, selling_price.
    Uses 'utf-8-sig' to automatically ignore any Byte Order Marks (BOM) in the file.
    """
    errors: List[str] = []
    
    if not os.path.exists(filepath):
        return ["Uploaded file could not be found on storage disk."]

    try:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            
            if not headers:
                return ["The uploaded CSV file is empty."]

            # Case-insensitive, stripped header matching
            headers_norm = [h.strip().lower() for h in headers]
            
            mandatory = ["date", "sku", "quantity_sold", "selling_price"]
            for field in mandatory:
                if field not in headers_norm:
                    errors.append(f"Missing mandatory column header: '{field}'")
                    
    except Exception as e:
        logger.error(f"Error parsing CSV headers for validation: {e}")
        errors.append(f"Invalid CSV structure or parse error: {str(e)}")

    return errors
