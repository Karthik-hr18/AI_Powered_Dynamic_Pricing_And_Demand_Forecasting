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
    Flexible validation checking for date, product/sku, quantity, and price aliases.
    Handles real-world SME retail dataset formats seamlessly.
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
            
            # Flexible column alias sets
            date_found = any(alias in headers_norm for alias in ["date", "order_date", "transaction_date", "timestamp"])
            product_found = any(alias in headers_norm for alias in ["sku", "product_id", "item_id", "product_name", "item_name", "product"])
            qty_found = any(alias in headers_norm for alias in ["quantity_sold", "quantity", "qty", "units_sold", "units"])
            price_found = any(alias in headers_norm for alias in ["selling_price", "unit_price_inr", "unit_price", "price", "total_sales_inr", "sales"])

            if not date_found:
                errors.append("Missing date column (expected: 'order_date', 'date', or 'transaction_date')")
            if not product_found:
                errors.append("Missing product/SKU column (expected: 'product_id', 'sku', or 'product_name')")
            if not qty_found:
                errors.append("Missing quantity column (expected: 'quantity_sold', 'quantity', or 'qty')")
            if not price_found:
                errors.append("Missing price/sales column (expected: 'unit_price_inr', 'selling_price', or 'price')")

    except Exception as e:
        logger.error(f"Error parsing CSV headers for validation: {e}")
        errors.append(f"Invalid CSV structure or parse error: {str(e)}")

    return errors

