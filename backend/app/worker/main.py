import asyncio
import csv
import logging
import os
import sys
from datetime import datetime, timezone

# Add parent directory containing 'ml' to sys.path
curr = os.path.abspath(__file__)
parent_dir = None
for _ in range(10):
    curr = os.path.dirname(curr)
    if os.path.isdir(os.path.join(curr, "ml")):
        parent_dir = curr
        break

if parent_dir and parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from typing import Any, Dict, Optional, Tuple

from beanie import init_beanie, PydanticObjectId

from app.core.config import settings
from app.core.constants import UploadStatus, UserRole, ForecastTriggeredBy
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


async def run_downstream_pipeline(upload: UploadDocument) -> None:
    """
    Executes feature engineering and predictive inference pipelines for all products
    modified in this upload.
    """
    # 1. Fetch raw rows uploaded in this job
    raw_sales = await RawSaleDocument.find(RawSaleDocument.upload_id == upload.id).to_list()
    if not raw_sales:
        logger.warning(f"No raw sales records found for upload {upload.upload_id}")
        return

    # 2. Daily sales aggregation
    from ml.shared.feature_engineering import aggregate_raw_sales_daily, compute_rolling_features
    from ml.forecasting.inference.predict import predict_demand
    from ml.pricing.inference.predict import recommend_price
    from ml.anomaly.inference.predict import detect_anomalies

    df_agg = aggregate_raw_sales_daily(raw_sales)
    if df_agg.empty:
        logger.warning(f"Daily aggregation resulted in empty dataframe for upload {upload.upload_id}")
        return

    product_ids = {PydanticObjectId(pid) for pid in df_agg["product_id"]}
    run_time = datetime.now(timezone.utc)
    run_id = PydanticObjectId()

    logger.info(f"Triggering downstream pipelines for {len(product_ids)} products. Run ID: {run_id}")

    for pid in product_ids:
        # A. Preprocessing: query prior context to compute rolling windows correctly
        history_processed = await ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == upload.retailer_id,
            ProcessedSaleDocument.product_id == pid
        ).sort("+date").to_list()

        df_prod = df_agg[df_agg["product_id"] == str(pid)]
        feature_records = compute_rolling_features(df_prod, history_processed)

        # Bulk fetch existing feature records for product
        existing_processed = await ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == upload.retailer_id,
            ProcessedSaleDocument.product_id == pid
        ).to_list()
        existing_map = {p.date: p for p in existing_processed}

        new_feats = []
        for feat in feature_records:
            feat_date = feat["date"]
            if feat_date in existing_map:
                ex = existing_map[feat_date]
                ex.quantity_sold = feat["quantity_sold"]
                ex.selling_price = feat["selling_price"]
                ex.lag_1d_quantity = feat["lag_1d_quantity"]
                ex.rolling_avg_7d = feat["rolling_avg_7d"]
                ex.rolling_avg_30d = feat["rolling_avg_30d"]
                await ex.save()
            else:
                new_feats.append(ProcessedSaleDocument(
                    retailer_id=upload.retailer_id,
                    product_id=pid,
                    date=feat_date,
                    quantity_sold=feat["quantity_sold"],
                    selling_price=feat["selling_price"],
                    unit_cost=feat["unit_cost"],
                    discount=feat["discount"],
                    store_id=feat["store_id"],
                    inventory_level=feat["inventory_level"],
                    promotion_flag=feat["promotion_flag"],
                    holiday_flag=feat["holiday_flag"],
                    category=feat["category"],
                    lag_1d_quantity=feat["lag_1d_quantity"],
                    rolling_avg_7d=feat["rolling_avg_7d"],
                    rolling_avg_30d=feat["rolling_avg_30d"],
                    price_change_flag=feat["price_change_flag"],
                    day_of_week=feat["day_of_week"],
                    is_weekend=feat["is_weekend"],
                    feature_engineering_version=feat["feature_engineering_version"]
                ))
        if new_feats:
            await ProcessedSaleDocument.insert_many(new_feats)

        # B. Reload fully updated history timeline (for lag/prediction context)
        full_history = await ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == upload.retailer_id,
            ProcessedSaleDocument.product_id == pid
        ).sort("+date").to_list()

        current_price = full_history[-1].selling_price if full_history else 0.0

        # C. ML Inference: Forecasting
        forecast_curr, forecast_hist = predict_demand(
            retailer_id=upload.retailer_id,
            product_id=pid,
            history=full_history,
            upload_id=upload.id,
            run_id=run_id,
            trigger_by=ForecastTriggeredBy.UPLOAD
        )
        existing_f = await ForecastCurrentDocument.find_one(
            ForecastCurrentDocument.retailer_id == upload.retailer_id,
            ForecastCurrentDocument.product_id == pid
        )
        if existing_f:
            forecast_curr.id = existing_f.id
            await forecast_curr.replace()
        else:
            await forecast_curr.insert()
            
        await ForecastHistoryDocument.find(
            ForecastHistoryDocument.retailer_id == upload.retailer_id,
            ForecastHistoryDocument.product_id == pid,
            ForecastHistoryDocument.superseded_at == None
        ).set({"superseded_at": run_time})
        await forecast_hist.insert()

        # D. ML Inference: Pricing Recommendations
        pricing_curr, pricing_hist = recommend_price(
            retailer_id=upload.retailer_id,
            product_id=pid,
            history=full_history,
            current_price=current_price,
            upload_id=upload.id,
            run_id=run_id,
            trigger_by=ForecastTriggeredBy.UPLOAD
        )
        existing_p = await PricingCurrentDocument.find_one(
            PricingCurrentDocument.retailer_id == upload.retailer_id,
            PricingCurrentDocument.product_id == pid
        )
        if existing_p:
            pricing_curr.id = existing_p.id
            await pricing_curr.replace()
        else:
            await pricing_curr.insert()
            
        await PricingHistoryDocument.find(
            PricingHistoryDocument.retailer_id == upload.retailer_id,
            PricingHistoryDocument.product_id == pid,
            PricingHistoryDocument.superseded_at == None
        ).set({"superseded_at": run_time})
        await pricing_hist.insert()

        # E. ML Inference: Anomaly Detection
        anomaly_curr = detect_anomalies(
            retailer_id=upload.retailer_id,
            product_id=pid,
            history=full_history,
            upload_id=upload.id
        )
        existing_a = await AnomalyCurrentDocument.find_one(
            AnomalyCurrentDocument.retailer_id == upload.retailer_id,
            AnomalyCurrentDocument.product_id == pid
        )
        if existing_a:
            # Stage 2 results are appended; Stage 1 are preserved (Section 8.4)
            existing_dates = set(a.date for a in existing_a.flagged_anomalies)
            new_anoms = [a for a in anomaly_curr.flagged_anomalies if a.date not in existing_dates]
            if new_anoms:
                existing_a.flagged_anomalies.extend(new_anoms)
                existing_a.total_flagged_count = len(existing_a.flagged_anomalies)
                existing_a.has_unreviewed_alerts = any(not a.acknowledged for a in existing_a.flagged_anomalies)
                if upload.id is not None:
                    existing_a.upload_id = upload.id
                existing_a.run_timestamp = run_time
                await existing_a.save()
        else:
            await anomaly_curr.insert()

    logger.info(f"Downstream pipeline executed successfully for upload {upload.upload_id}")


async def process_single_upload(upload: UploadDocument) -> None:
    """
    Ingests raw CSV rows from storage, creates/updates products on-the-fly,
    registers immutable RawSaleDocument entries, and triggers the downstream pipeline.
    """
    logger.info(f"Worker starting ingestion for Upload Job: {upload.upload_id}")
    
    filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload.upload_id}.csv")
    if not os.path.exists(filepath):
        upload.status = UploadStatus.FAILED
        upload.error_reason = "Dataset CSV file was deleted or cannot be read on storage disk."
        upload.processing_completed_at = datetime.now(timezone.utc)
        await upload.save()
        return

    # Update job state
    upload.status = UploadStatus.PROCESSING
    upload.current_stage = "raw_sales_ingestion"
    upload.processing_started_at = datetime.now(timezone.utc)
    await upload.save()

    rows_ingested = 0
    rows_rejected = 0
    warnings_list = []
    raw_sale_dicts = []
    
    try:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            # Map case-insensitive CSV headers to standard fields
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV contains no header row or columns.")

            # Create normalized headers mapping lookup (lower-case matches)
            header_map = {h.strip().lower(): h for h in fieldnames}

            # Flexible column alias lookups matching real SME dataset formats
            def _find_header(aliases: list) -> str:
                for alias in aliases:
                    if alias in header_map:
                        return header_map[alias]
                return ""

            h_date  = _find_header(["date", "order_date", "transaction_date", "timestamp"])
            h_sku   = _find_header(["sku", "product_id", "item_id", "product_name", "item_name", "product"])
            h_qty   = _find_header(["quantity_sold", "quantity", "qty", "units_sold", "units"])
            h_price = _find_header(["selling_price", "unit_price_inr", "unit_price", "price", "total_sales_inr", "sales"])

            # Row index starts at 2 (since row 1 is headers)
            row_idx = 1
            for row in reader:
                row_idx += 1
                try:
                    # Retrieve headers case-insensitively using alias lookups
                    date_raw  = row.get(h_date) if h_date else None
                    sku_raw   = row.get(h_sku) if h_sku else None
                    qty_raw   = row.get(h_qty) if h_qty else None
                    price_raw = row.get(h_price) if h_price else None

                    # Mandatory field presence checks
                    if not date_raw or not sku_raw or not qty_raw or not price_raw:
                        missing = []
                        if not date_raw: missing.append("date/order_date")
                        if not sku_raw: missing.append("sku/product_id")
                        if not qty_raw: missing.append("quantity_sold/qty")
                        if not price_raw: missing.append("selling_price/unit_price_inr")
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

                    # 1. Collect row data for bulk insertion
                    raw_sale_dicts.append({
                        "retailer_id": upload.retailer_id,
                        "upload_id": upload.id,
                        "sku": sku_normalized,
                        "sku_display": sku_display,
                        "date": date_parsed,
                        "quantity_sold": qty_parsed,
                        "selling_price": price_parsed,
                        "category": cat_parsed,
                        "unit_cost": unit_cost_parsed,
                        "discount": discount_parsed,
                        "store_id": store_parsed,
                        "inventory_level": inv_parsed,
                        "promotion_flag": promo_parsed,
                        "holiday_flag": hol_parsed,
                        "row_number_in_file": row_idx,
                        "source_row_raw": row
                    })
                    rows_ingested += 1

                except Exception as row_err:
                    rows_rejected += 1
                    warnings_list.append(RowWarning(row=row_idx, reason=str(row_err)))
                    logger.warning(f"Row validation failed on line {row_idx}: {row_err}")

        # Bulk register products and insert raw sales records for fast processing
        logger.info(f"Bulk inserting {len(raw_sale_dicts)} raw sale records...")
        unique_skus = {}
        for item in raw_sale_dicts:
            s_norm = item["sku"]
            if s_norm not in unique_skus:
                unique_skus[s_norm] = (item["sku_display"], item["category"])

        # Fetch existing products in one query
        existing_products = await ProductDocument.find(
            ProductDocument.retailer_id == upload.retailer_id,
            {"sku": {"$in": list(unique_skus.keys())}}
        ).to_list()
        product_map = {p.sku: p for p in existing_products}

        # Bulk create new products
        new_products = []
        for s_norm, (s_disp, cat) in unique_skus.items():
            if s_norm not in product_map:
                p_doc = ProductDocument(
                    retailer_id=upload.retailer_id,
                    sku=s_norm,
                    sku_display=s_disp,
                    product_name=s_disp,
                    category=cat,
                    first_seen_upload_id=upload.id,
                    last_seen_upload_id=upload.id
                )
                new_products.append(p_doc)

        if new_products:
            await ProductDocument.insert_many(new_products)
            for p in new_products:
                product_map[p.sku] = p

        # Build final RawSaleDocument models and bulk insert
        raw_docs = []
        for item in raw_sale_dicts:
            sku_str = str(item["sku"])
            p_obj = product_map.get(sku_str)
            if p_obj:
                raw_docs.append(RawSaleDocument(
                    retailer_id=item["retailer_id"],
                    upload_id=item["upload_id"],
                    product_id=p_obj.id,
                    sku=item["sku"],
                    date=item["date"],
                    quantity_sold=item["quantity_sold"],
                    selling_price=item["selling_price"],
                    category=item["category"],
                    unit_cost=item["unit_cost"],
                    discount=item["discount"],
                    store_id=item["store_id"],
                    inventory_level=item["inventory_level"],
                    promotion_flag=item["promotion_flag"],
                    holiday_flag=item["holiday_flag"],
                    row_number_in_file=item["row_number_in_file"],
                    source_row_raw=item["source_row_raw"]
                ))

        if raw_docs:
            await RawSaleDocument.insert_many(raw_docs)

        # Update final document statistics
        upload.row_count = row_idx - 1 # excluding header row
        upload.rows_ingested = rows_ingested
        upload.rows_rejected = rows_rejected
        upload.row_warnings = warnings_list
        upload.processing_completed_at = datetime.now(timezone.utc)

        if rows_ingested == 0:
            upload.status = UploadStatus.FAILED
            upload.error_reason = "All rows in the CSV file failed validation and were rejected."
            await upload.save()
        else:
            # 3. Trigger downstream pipeline for feature engineering & inference
            try:
                await run_downstream_pipeline(upload)
                if rows_rejected > 0:
                    upload.status = UploadStatus.COMPLETED_WITH_WARNINGS
                else:
                    upload.status = UploadStatus.COMPLETED
            except Exception as pipe_err:
                logger.error(f"Downstream pipeline failed for upload {upload.upload_id}: {pipe_err}")
                upload.status = UploadStatus.FAILED
                upload.error_reason = f"Downstream pipeline failed: {str(pipe_err)}"
            
            await upload.save()

        logger.info(
            f"Successfully processed upload job {upload.upload_id}: "
            f"ingested={rows_ingested}, rejected={rows_rejected}, status={upload.status.value}"
        )

    except Exception as file_err:
        logger.error(f"Failed to process CSV file {upload.upload_id}: {file_err}")
        upload.status = UploadStatus.FAILED
        upload.error_reason = f"Fatal dataset parse error: {str(file_err)}"
        upload.processing_completed_at = datetime.now(timezone.utc)
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
    await init_beanie(database=cast(Any, db), document_models=document_models)
    
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
