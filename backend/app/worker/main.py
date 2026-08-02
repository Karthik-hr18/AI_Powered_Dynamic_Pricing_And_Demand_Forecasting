import asyncio
import csv
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from beanie import init_beanie

from app.core.config import settings
from app.core.constants import UploadStatus, UserRole
from app.core.db.connection import connect_to_mongo, close_mongo_connection, get_database
from app.core.db.init_indexes import create_all_indexes
from app.domains.auth.models import UserDocument
from app.domains.products.models import ProductDocument
from app.domains.uploads.models import RowWarning, UploadDocument
from app.domains.sales_data.models import RawSaleDocument, ProcessedSaleDocument
from app.domains.forecasting.models import ForecastCurrentDocument, ForecastHistoryDocument
from app.domains.pricing.models import PricingCurrentDocument, PricingHistoryDocument
from app.domains.inventory.models import InventoryCurrentDocument
from app.domains.anomaly.models import AnomalyCurrentDocument

# Setup logger configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("app.worker")


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    """Helper to parse varied CSV string representations to Boolean."""
    if value is None or value.strip() == "":
        return None
    val_norm = value.strip().lower()
    if val_norm in ("1", "true", "t", "y", "yes"):
        return True
    if val_norm in ("0", "false", "f", "n", "no"):
        return False
    raise ValueError(f"Value '{value}' cannot be parsed as a boolean.")


def _parse_int(value: Optional[str]) -> Optional[int]:
    """Helper to parse string representations to Integer (handles float string like '1.0')."""
    if value is None or value.strip() == "":
        return None
    try:
        return int(float(value.strip()))
    except ValueError:
        raise ValueError(f"Value '{value}' is not a valid integer.")


def _parse_float(value: Optional[str]) -> Optional[float]:
    """Helper to parse string representations to Float."""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value.strip())
    except ValueError:
        raise ValueError(f"Value '{value}' is not a valid float.")


async def process_single_upload(upload: UploadDocument) -> None:
    """
    Ingests raw CSV rows from storage, creates/updates products on-the-fly,
    registers immutable RawSaleDocument entries, and tracks warning thresholds.
    """
    logger.info(f"Worker starting ingestion for Upload Job: {upload.upload_id}")
    
    filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload.upload_id}.csv")
    if not os.path.exists(filepath):
        upload.status = UploadStatus.FAILED
        upload.error_reason = "Dataset CSV file was deleted or cannot be read on storage disk."
        upload.processing_completed_at = datetime.utcnow()
        await upload.save()
        return

    # Update job state
    upload.status = UploadStatus.PROCESSING
    upload.current_stage = "raw_sales_ingestion"
    upload.processing_started_at = datetime.utcnow()
    await upload.save()

    rows_ingested = 0
    rows_rejected = 0
    warnings_list = []
    
    try:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            # Map case-insensitive CSV headers to standard fields
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV contains no header row or columns.")

            # Create normalized headers mapping lookup (lower-case matches)
            header_map = {h.strip().lower(): h for h in fieldnames}
            
            # Row index starts at 2 (since row 1 is headers)
            row_idx = 1
            for row in reader:
                row_idx += 1
                try:
                    # Retrieve headers case-insensitively
                    date_raw = row.get(header_map.get("date", ""))
                    sku_raw = row.get(header_map.get("sku", ""))
                    qty_raw = row.get(header_map.get("quantity_sold", ""))
                    price_raw = row.get(header_map.get("selling_price", ""))

                    # Mandatory field presence checks
                    if not date_raw or not sku_raw or not qty_raw or not price_raw:
                        missing = []
                        if not date_raw: missing.append("date")
                        if not sku_raw: missing.append("sku")
                        if not qty_raw: missing.append("quantity_sold")
                        if not price_raw: missing.append("selling_price")
                        raise ValueError(f"Missing mandatory row values: {', '.join(missing)}")

                    # Parse values
                    try:
                        date_parsed = datetime.strptime(date_raw.strip(), "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"Date format must be YYYY-MM-DD (got: '{date_raw}')")

                    sku_display = sku_raw.strip()
                    sku_normalized = sku_display.lower()
                    if not sku_normalized:
                        raise ValueError("SKU cannot be empty or whitespace.")

                    qty_parsed = _parse_int(qty_raw)
                    if qty_parsed is None or qty_parsed < 0:
                        raise ValueError(f"quantity_sold must be a non-negative integer (got: '{qty_raw}')")

                    price_parsed = _parse_float(price_raw)
                    if price_parsed is None or price_parsed < 0:
                        raise ValueError(f"selling_price must be a non-negative float (got: '{price_raw}')")

                    # Parse optional fields case-insensitively
                    cat_raw = row.get(header_map.get("category", None))
                    unit_cost_raw = row.get(header_map.get("unit_cost", None))
                    disc_raw = row.get(header_map.get("discount", None))
                    store_raw = row.get(header_map.get("store_id", None))
                    inv_raw = row.get(header_map.get("inventory_level", None))
                    promo_raw = row.get(header_map.get("promotion_flag", None))
                    hol_raw = row.get(header_map.get("holiday_flag", None))

                    cat_parsed = cat_raw.strip() if cat_raw else None
                    unit_cost_parsed = _parse_float(unit_cost_raw)
                    if unit_cost_parsed is not None and unit_cost_parsed < 0:
                        raise ValueError(f"unit_cost must be non-negative (got: '{unit_cost_raw}')")
                        
                    discount_parsed = _parse_float(disc_raw)
                    if discount_parsed is not None and discount_parsed < 0:
                        raise ValueError(f"discount must be non-negative (got: '{disc_raw}')")

                    store_parsed = store_raw.strip() if store_raw else None
                    inv_parsed = _parse_int(inv_raw)
                    if inv_parsed is not None and inv_parsed < 0:
                        raise ValueError(f"inventory_level must be non-negative (got: '{inv_raw}')")

                    promo_parsed = _parse_bool(promo_raw)
                    hol_parsed = _parse_bool(hol_raw)

                    # 1. Product SKU Auto-Population and mapping lookup
                    product = await ProductDocument.find_one(
                        ProductDocument.retailer_id == upload.retailer_id,
                        ProductDocument.sku == sku_normalized
                    )

                    if not product:
                        # Register product SKU on-the-fly
                        product = ProductDocument(
                            retailer_id=upload.retailer_id,
                            sku=sku_normalized,
                            sku_display=sku_display,
                            product_name=sku_display, # Fallback to display name
                            category=cat_parsed,
                            first_seen_upload_id=upload.id,
                            last_seen_upload_id=upload.id
                        )
                        await product.insert()
                    else:
                        # Update product tracking upload link
                        product.last_seen_upload_id = upload.id
                        product.updated_at = datetime.utcnow()
                        if cat_parsed and not product.category:
                            product.category = cat_parsed
                        await product.save()

                    # 2. Save immutable RawSaleDocument
                    raw_sale = RawSaleDocument(
                        retailer_id=upload.retailer_id,
                        upload_id=upload.id,
                        product_id=product.id,
                        sku=sku_normalized,
                        date=date_parsed,
                        quantity_sold=qty_parsed,
                        selling_price=price_parsed,
                        category=cat_parsed,
                        unit_cost=unit_cost_parsed,
                        discount=discount_parsed,
                        store_id=store_parsed,
                        inventory_level=inv_parsed,
                        promotion_flag=promo_parsed,
                        holiday_flag=hol_parsed,
                        row_number_in_file=row_idx,
                        source_row_raw=row
                    )
                    await raw_sale.insert()
                    rows_ingested += 1

                except Exception as row_err:
                    rows_rejected += 1
                    warnings_list.append(RowWarning(row=row_idx, reason=str(row_err)))
                    logger.warning(f"Row validation failed on line {row_idx}: {row_err}")

        # Update final document statistics
        upload.row_count = row_idx - 1 # excluding header row
        upload.rows_ingested = rows_ingested
        upload.rows_rejected = rows_rejected
        upload.row_warnings = warnings_list
        upload.processing_completed_at = datetime.utcnow()

        if rows_ingested == 0:
            upload.status = UploadStatus.FAILED
            upload.error_reason = "All rows in the CSV file failed validation and were rejected."
        elif rows_rejected > 0:
            upload.status = UploadStatus.COMPLETED_WITH_WARNINGS
        else:
            upload.status = UploadStatus.COMPLETED

        await upload.save()
        logger.info(
            f"Successfully processed upload job {upload.upload_id}: "
            f"ingested={rows_ingested}, rejected={rows_rejected}, status={upload.status.value}"
        )

    except Exception as file_err:
        logger.error(f"Failed to process CSV file {upload.upload_id}: {file_err}")
        upload.status = UploadStatus.FAILED
        upload.error_reason = f"Fatal dataset parse error: {str(file_err)}"
        upload.processing_completed_at = datetime.utcnow()
        await upload.save()


async def worker_loop() -> None:
    """Infinite polling loop querying for new UPLOADED dataset entries."""
    logger.info(f"Worker entering polling loop. interval={settings.WORKER_POLL_INTERVAL_SECONDS}s")
    while True:
        try:
            # Query for next available job in UPLOADED state (first-in-first-out)
            upload = await UploadDocument.find_one(
                UploadDocument.status == UploadStatus.UPLOADED
            )

            if upload:
                await process_single_upload(upload)
            
        except Exception as loop_err:
            logger.error(f"Error in background worker main loop: {loop_err}")
        
        await asyncio.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)


async def main() -> None:
    """Bootstraps database, Beanie ODM model registries, and starts worker loop."""
    logger.info("Initializing background worker components...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize Beanie ODM with all project documents
    db = get_database()
    document_models = [
        UserDocument,
        ProductDocument,
        UploadDocument,
        RawSaleDocument,
        ProcessedSaleDocument,
        ForecastCurrentDocument,
        ForecastHistoryDocument,
        PricingCurrentDocument,
        PricingHistoryDocument,
        InventoryCurrentDocument,
        AnomalyCurrentDocument
    ]
    await init_beanie(database=db, document_models=document_models)
    
    # Ensure indexes exist
    await create_all_indexes()
    
    try:
        await worker_loop()
    except asyncio.CancelledError:
        logger.info("Worker loop cancelled.")
    finally:
        await close_mongo_connection()
        logger.info("Worker process cleaned up.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by keyboard interrupt.")
        sys.exit(0)
