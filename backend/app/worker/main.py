import asyncio
import csv
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Locate the project root containing the `ml/` package directory so that ML
# modules can be imported even when this worker is launched from any cwd.
# ---------------------------------------------------------------------------
_curr = os.path.abspath(__file__)
_parent_dir = None
for _ in range(10):
    _curr = os.path.dirname(_curr)
    if os.path.isdir(os.path.join(_curr, "ml")):
        _parent_dir = _curr
        break

if _parent_dir and _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from typing import Any, Dict, List, Optional, Tuple, cast

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("app.worker")


# ---------------------------------------------------------------------------
# CSV parse helpers
# ---------------------------------------------------------------------------

def _parse_bool(value: Optional[str]) -> Optional[bool]:
    """Parse varied CSV string representations to Boolean."""
    if value is None or value.strip() == "":
        return None
    val_norm = value.strip().lower()
    if val_norm in ("1", "true", "t", "y", "yes"):
        return True
    if val_norm in ("0", "false", "f", "n", "no"):
        return False
    raise ValueError(f"Value '{value}' cannot be parsed as a boolean.")


def _parse_int(value: Optional[str]) -> Optional[int]:
    """Parse string representations to Integer (handles float strings like '1.0')."""
    if value is None or value.strip() == "":
        return None
    try:
        return int(float(value.strip()))
    except ValueError:
        raise ValueError(f"Value '{value}' is not a valid integer.")


def _parse_float(value: Optional[str]) -> Optional[float]:
    """Parse string representations to Float."""
    if value is None or value.strip() == "":
        return None
    try:
        return float(value.strip())
    except ValueError:
        raise ValueError(f"Value '{value}' is not a valid float.")


# ---------------------------------------------------------------------------
# Stage failure helper — marks upload FAILED with structured metadata
# ---------------------------------------------------------------------------

async def _fail_upload(
    upload: UploadDocument,
    stage: str,
    message: str,
    tb: Optional[str] = None,
) -> None:
    """Persist a structured FAILED state for the given upload."""
    upload.status = UploadStatus.FAILED
    upload.current_stage = stage
    upload.failed_stage = stage
    upload.error_reason = message
    upload.error_traceback = tb
    upload.processing_completed_at = datetime.now(timezone.utc)
    try:
        await upload.save()
    except Exception as save_err:
        logger.error(f"[WORKER] Could not persist FAILED status for {upload.upload_id}: {save_err}")


# ---------------------------------------------------------------------------
# Phase 2: Scalable aggregation via MongoDB aggregation pipeline
# ---------------------------------------------------------------------------

async def _aggregate_sales_via_mongo(upload_id: PydanticObjectId, retailer_id: PydanticObjectId) -> List[Dict[str, Any]]:
    """
    Phase 2 — Scalability: Use MongoDB $group aggregation pipeline instead of
    fetching all RawSaleDocuments into Python RAM.

    Returns a list of dicts shaped as:
      {product_id, date, quantity_sold, selling_price, unit_cost,
       discount, store_id, inventory_level, promotion_flag, holiday_flag, category}

    Grouped by (product_id, date) — equivalent to aggregate_raw_sales_daily()
    but executed entirely inside MongoDB, transferring only aggregated rows.
    """
    pipeline = [
        # Phase 1 fix: ONLY match records belonging to THIS upload batch
        {"$match": {"upload_id": upload_id, "retailer_id": retailer_id}},
        {
            "$group": {
                "_id": {
                    "product_id": "$product_id",
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
                },
                "quantity_sold": {"$sum": "$quantity_sold"},
                # Quantity-weighted average selling price
                "price_qty_weighted": {"$sum": {"$multiply": ["$selling_price", "$quantity_sold"]}},
                "unit_cost": {"$avg": "$unit_cost"},
                "discount": {"$avg": "$discount"},
                "inventory_level": {"$avg": "$inventory_level"},
                "store_id": {"$first": "$store_id"},
                "category": {"$first": "$category"},
                "promotion_flag": {"$max": {"$cond": ["$promotion_flag", 1, 0]}},
                "holiday_flag": {"$max": {"$cond": ["$holiday_flag", 1, 0]}},
            }
        },
        {
            "$project": {
                "_id": 0,
                "product_id": "$_id.product_id",
                "date": "$_id.date",
                "quantity_sold": 1,
                "selling_price": {
                    "$cond": [
                        {"$gt": ["$quantity_sold", 0]},
                        {"$divide": ["$price_qty_weighted", "$quantity_sold"]},
                        0.0,
                    ]
                },
                "unit_cost": 1,
                "discount": 1,
                "inventory_level": 1,
                "store_id": 1,
                "category": 1,
                "promotion_flag": {"$eq": ["$promotion_flag", 1]},
                "holiday_flag": {"$eq": ["$holiday_flag", 1]},
            }
        },
        {"$sort": {"product_id": 1, "date": 1}},
    ]

    db = get_database()
    cursor = db["raw_sales"].aggregate(pipeline)
    results = await cursor.to_list(length=None)
    return results


def _build_agg_dataframe(agg_rows: List[Dict[str, Any]]):
    """Convert MongoDB aggregation results to a pandas DataFrame for feature engineering."""
    import pandas as pd
    import numpy as np

    if not agg_rows:
        return pd.DataFrame()

    rows = []
    for doc in agg_rows:
        rows.append({
            "product_id": str(doc["product_id"]),
            "date": pd.to_datetime(doc["date"]).normalize(),
            "quantity_sold": doc.get("quantity_sold", 0),
            "selling_price": doc.get("selling_price", 0.0) or 0.0,
            "unit_cost": doc.get("unit_cost") if doc.get("unit_cost") is not None else np.nan,
            "discount": doc.get("discount", 0.0) or 0.0,
            "store_id": doc.get("store_id"),
            "inventory_level": doc.get("inventory_level") if doc.get("inventory_level") is not None else np.nan,
            "promotion_flag": 1 if doc.get("promotion_flag") else 0,
            "holiday_flag": 1 if doc.get("holiday_flag") else 0,
            "category": doc.get("category"),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Phase 2: Per-product ProcessedSale upsert (async cursor, not to_list())
# ---------------------------------------------------------------------------

async def _process_product_features(
    upload: UploadDocument,
    pid: PydanticObjectId,
    df_agg,
    compute_rolling_features,
    run_time: datetime,
) -> None:
    """
    For a single product, load its historical ProcessedSaleDocuments via async
    cursor (not .to_list()), compute rolling features, and upsert results.
    """
    import pandas as pd

    # Async cursor — avoids pulling all processed records into memory at once
    history_processed: List[ProcessedSaleDocument] = []
    async for doc in ProcessedSaleDocument.find(
        ProcessedSaleDocument.retailer_id == upload.retailer_id,
        ProcessedSaleDocument.product_id == pid,
    ).sort("+date"):
        history_processed.append(doc)

    df_prod = df_agg[df_agg["product_id"] == str(pid)]
    feature_records = compute_rolling_features(df_prod, history_processed)

    def _date_key(d: Any) -> str:
        if hasattr(d, "strftime"):
            return d.strftime("%Y-%m-%d")
        return str(d)[:10]

    # Build lookup of existing processed records for upsert using normalized date key
    existing_map: Dict[str, ProcessedSaleDocument] = {_date_key(p.date): p for p in history_processed}

    updated_ex_docs: List[ProcessedSaleDocument] = []
    seen_new_dates = set()
    new_feats: List[ProcessedSaleDocument] = []
    for feat in feature_records:
        feat_date = feat["date"]
        d_key = _date_key(feat_date)

        if d_key in existing_map:
            ex = existing_map[d_key]
            ex.quantity_sold = feat["quantity_sold"]
            ex.selling_price = feat["selling_price"]
            ex.lag_1d_quantity = feat["lag_1d_quantity"]
            ex.rolling_avg_7d = feat["rolling_avg_7d"]
            ex.rolling_avg_30d = feat["rolling_avg_30d"]
            updated_ex_docs.append(ex)
        elif d_key not in seen_new_dates:
            seen_new_dates.add(d_key)
            new_feats.append(ProcessedSaleDocument(
                retailer_id=upload.retailer_id,
                product_id=pid,
                date=feat_date,
                quantity_sold=feat["quantity_sold"],
                selling_price=feat["selling_price"],
                unit_cost=feat["unit_cost"],
                discount=feat.get("discount"),
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
                feature_engineering_version=feat["feature_engineering_version"],
            ))

    if updated_ex_docs:
        await asyncio.gather(*(d.save() for d in updated_ex_docs))

    if new_feats:
        try:
            await ProcessedSaleDocument.insert_many(new_feats)
        except Exception as ex_bulk:
            logger.warning(f"[WORKER] Batch insert warning for product {pid}: {ex_bulk}. Falling back to atomic upserts.")
            for doc in new_feats:
                try:
                    existing_doc = await ProcessedSaleDocument.find_one(
                        ProcessedSaleDocument.retailer_id == doc.retailer_id,
                        ProcessedSaleDocument.product_id == doc.product_id,
                        ProcessedSaleDocument.date == doc.date,
                    )
                    if existing_doc:
                        existing_doc.quantity_sold = doc.quantity_sold
                        existing_doc.selling_price = doc.selling_price
                        existing_doc.lag_1d_quantity = doc.lag_1d_quantity
                        existing_doc.rolling_avg_7d = doc.rolling_avg_7d
                        existing_doc.rolling_avg_30d = doc.rolling_avg_30d
                        await existing_doc.save()
                    else:
                        await doc.insert()
                except Exception as single_ex:
                    logger.warning(f"[WORKER] Skipping duplicate processed sale insert for {pid} on {doc.date}: {single_ex}")


# ---------------------------------------------------------------------------
# Downstream pipeline
# ---------------------------------------------------------------------------

async def run_downstream_pipeline(upload: UploadDocument) -> None:
    """
    Phase 2 — Scalability: Aggregates raw sales via MongoDB $group pipeline
    (zero in-memory document fetch for the raw collection), then runs
    feature engineering and ML inference per product.
    """
    from ml.shared.feature_engineering import compute_rolling_features  # type: ignore[import]
    from ml.forecasting.inference.predict import predict_demand  # type: ignore[import]
    from ml.pricing.inference.predict import recommend_price  # type: ignore[import]
    from ml.anomaly.inference.predict import detect_anomalies  # type: ignore[import]

    stage = "aggregation"
    upload.current_stage = stage
    await upload.save()

    # ------------------------------------------------------------------ #
    # Stage 1 — MongoDB aggregation (Phase 1 + Phase 2 combined fix)
    # Filters ONLY by upload.id so historical records from other jobs are
    # never mixed into this processing run.
    # ------------------------------------------------------------------ #
    t0 = time.perf_counter()
    logger.info(f"[WORKER] Aggregating raw sales for upload {upload.upload_id} (upload_id={upload.id})")
    if upload.id is None:
        await _fail_upload(upload, "aggregation", "Upload document has no database ID.")
        return
    agg_rows = await _aggregate_sales_via_mongo(upload.id, upload.retailer_id)
    t1 = time.perf_counter()
    logger.info(f"[WORKER] Aggregation complete: {len(agg_rows)} product-day rows in {t1 - t0:.2f}s")

    if not agg_rows:
        logger.warning(f"[WORKER] No aggregated rows for upload {upload.upload_id} — skipping downstream.")
        return

    df_agg = _build_agg_dataframe(agg_rows)
    if df_agg.empty:
        logger.warning(f"[WORKER] Empty dataframe after aggregation for upload {upload.upload_id}.")
        return

    product_ids = [PydanticObjectId(str(pid)) for pid in df_agg["product_id"].unique()]
    run_time = datetime.now(timezone.utc)
    run_id = PydanticObjectId()

    logger.info(f"[WORKER] Downstream pipeline starting for {len(product_ids)} products. run_id={run_id}")

async def _process_single_product_pipeline(
    upload: UploadDocument,
    pid: PydanticObjectId,
    df_agg: Any,
    compute_rolling_features: Any,
    predict_demand: Any,
    recommend_price: Any,
    detect_anomalies: Any,
    run_time: datetime,
    run_id: PydanticObjectId,
) -> bool:
    try:
        # 1. Feature Engineering
        await _process_product_features(upload, pid, df_agg, compute_rolling_features, run_time)

        # 2. History Load
        full_history: List[ProcessedSaleDocument] = []
        async for doc in ProcessedSaleDocument.find(
            ProcessedSaleDocument.retailer_id == upload.retailer_id,
            ProcessedSaleDocument.product_id == pid,
        ).sort("+date"):
            full_history.append(doc)

        current_price = full_history[-1].selling_price if full_history else 0.0

        # 3. Forecasting
        forecast_curr, forecast_hist = predict_demand(
            retailer_id=upload.retailer_id,
            product_id=pid,
            history=full_history,
            upload_id=upload.id,
            run_id=run_id,
            trigger_by=ForecastTriggeredBy.UPLOAD,
        )
        existing_f = await ForecastCurrentDocument.find_one(
            ForecastCurrentDocument.retailer_id == upload.retailer_id,
            ForecastCurrentDocument.product_id == pid,
        )
        if existing_f:
            forecast_curr.id = existing_f.id
            await forecast_curr.replace()
        else:
            await forecast_curr.insert()

        await ForecastHistoryDocument.find(
            ForecastHistoryDocument.retailer_id == upload.retailer_id,
            ForecastHistoryDocument.product_id == pid,
            ForecastHistoryDocument.superseded_at == None,
        ).update_many({"$set": {"superseded_at": run_time}})
        await forecast_hist.insert()

        # 4. Pricing
        pricing_curr, pricing_hist = recommend_price(
            retailer_id=upload.retailer_id,
            product_id=pid,
            history=full_history,
            current_price=current_price,
            upload_id=upload.id,
            run_id=run_id,
            trigger_by=ForecastTriggeredBy.UPLOAD,
        )
        existing_p = await PricingCurrentDocument.find_one(
            PricingCurrentDocument.retailer_id == upload.retailer_id,
            PricingCurrentDocument.product_id == pid,
        )
        if existing_p:
            pricing_curr.id = existing_p.id
            await pricing_curr.replace()
        else:
            await pricing_curr.insert()

        await PricingHistoryDocument.find(
            PricingHistoryDocument.retailer_id == upload.retailer_id,
            PricingHistoryDocument.product_id == pid,
            PricingHistoryDocument.superseded_at == None,
        ).update_many({"$set": {"superseded_at": run_time}})
        await pricing_hist.insert()

        # 5. Anomaly Detection
        anomaly_curr = detect_anomalies(
            retailer_id=upload.retailer_id,
            product_id=pid,
            history=full_history,
            upload_id=upload.id,
        )
        existing_a = await AnomalyCurrentDocument.find_one(
            AnomalyCurrentDocument.retailer_id == upload.retailer_id,
            AnomalyCurrentDocument.product_id == pid,
        )
        if existing_a:
            existing_dates = {a.date for a in existing_a.flagged_anomalies}
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

        return True
    except Exception as e:
        logger.error(f"[WORKER] Pipeline error for product {pid}: {e}", exc_info=True)
        return False


async def run_downstream_pipeline(upload: UploadDocument) -> None:
    """
    Phase 2 — Scalability: Aggregates raw sales via MongoDB $group pipeline,
    then runs feature engineering and ML inference concurrently in batches.
    """
    from ml.shared.feature_engineering import compute_rolling_features  # type: ignore[import]
    from ml.forecasting.inference.predict import predict_demand  # type: ignore[import]
    from ml.pricing.inference.predict import recommend_price  # type: ignore[import]
    from ml.anomaly.inference.predict import detect_anomalies  # type: ignore[import]

    stage = "aggregation"
    upload.current_stage = stage
    await upload.save()

    t0 = time.perf_counter()
    logger.info(f"[WORKER] Aggregating raw sales for upload {upload.upload_id} (upload_id={upload.id})")
    if upload.id is None:
        await _fail_upload(upload, "aggregation", "Upload document has no database ID.")
        return
    agg_rows = await _aggregate_sales_via_mongo(upload.id, upload.retailer_id)
    t1 = time.perf_counter()
    logger.info(f"[WORKER] Aggregation complete: {len(agg_rows)} product-day rows in {t1 - t0:.2f}s")

    if not agg_rows:
        logger.warning(f"[WORKER] No aggregated rows for upload {upload.upload_id} — skipping downstream.")
        return

    df_agg = _build_agg_dataframe(agg_rows)
    if df_agg.empty:
        logger.warning(f"[WORKER] Empty dataframe after aggregation for upload {upload.upload_id}.")
        return

    product_ids = [PydanticObjectId(str(pid)) for pid in df_agg["product_id"].unique()]
    run_time = datetime.now(timezone.utc)
    run_id = PydanticObjectId()

    logger.info(f"[WORKER] Downstream pipeline starting for {len(product_ids)} products. run_id={run_id}")

    # Process products in batches of 5 for optimal database pool throughput
    batch_size = 5
    total_products = len(product_ids)
    processed_count = 0

    upload.current_stage = "downstream_pipeline"
    await upload.save()

    for i in range(0, total_products, batch_size):
        batch = product_ids[i:i + batch_size]
        tasks = [
            _process_single_product_pipeline(
                upload=upload,
                pid=pid,
                df_agg=df_agg,
                compute_rolling_features=compute_rolling_features,
                predict_demand=predict_demand,
                recommend_price=recommend_price,
                detect_anomalies=detect_anomalies,
                run_time=run_time,
                run_id=run_id,
            )
            for pid in batch
        ]
        await asyncio.gather(*tasks)
        processed_count += len(batch)
        if processed_count % 50 == 0 or processed_count == total_products:
            logger.info(f"[WORKER] Downstream pipeline progress: {processed_count}/{total_products} products completed.")

    logger.info(f"[WORKER] Downstream pipeline completed successfully for upload {upload.upload_id}")


# ---------------------------------------------------------------------------
# Main ingestion entry point
# ---------------------------------------------------------------------------

async def process_single_upload(upload: UploadDocument) -> None:
    """
    Ingests raw CSV rows, registers RawSaleDocuments, then triggers the
    downstream feature engineering + ML inference pipeline.

    Phase 1: Only records belonging to upload.id are processed.
    Phase 3: Every stage is guarded — FAILED is always set with structured
             metadata if anything goes wrong.
    """
    logger.info(f"[WORKER] Claimed upload job: {upload.upload_id}")

    os.makedirs(settings.UPLOAD_STORAGE_DIR, exist_ok=True)
    filepath = os.path.join(settings.UPLOAD_STORAGE_DIR, f"{upload.upload_id}.csv")
    if not os.path.exists(filepath):
        logger.error(f"[WORKER] CSV file missing from storage: {filepath}")
        await _fail_upload(upload, "file_check", "CSV file missing from storage. Please re-upload the CSV dataset file.")
        return

    # Transition to PROCESSING
    upload.status = UploadStatus.PROCESSING
    upload.current_stage = "csv_parsing"
    upload.processing_started_at = datetime.now(timezone.utc)
    await upload.save()
    logger.info(f"[WORKER] Status → PROCESSING for {upload.upload_id}")

    rows_ingested = 0
    rows_rejected = 0
    warnings_list: List[RowWarning] = []
    raw_sale_dicts: List[Dict] = []

    # ------------------------------------------------------------------ #
    # Stage: CSV Parsing
    # ------------------------------------------------------------------ #
    try:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV contains no header row or columns.")

            header_map = {h.strip().lower(): h for h in fieldnames}
            def _find_header(aliases: list) -> str:
                for alias in aliases:
                    if alias in header_map:
                        return header_map[alias]
                return ""

            h_date  = _find_header(["date", "order_date", "transaction_date", "timestamp"])
            h_sku   = _find_header(["sku", "product_id", "item_id"])
            h_name  = _find_header(["product_name", "product_title", "title", "name", "item_name"])
            h_qty   = _find_header(["quantity_sold", "quantity", "qty", "units_sold", "units"])
            h_price = _find_header(["selling_price", "unit_price_inr", "unit_price", "price", "total_sales_inr", "sales"])

            if not h_sku:
                h_sku = _find_header(["sku", "product_id", "item_id", "product_name", "item_name", "product"])

            row_idx = 1
            for row in reader:
                row_idx += 1
                try:
                    date_raw  = row.get(h_date) if h_date else None
                    sku_raw   = row.get(h_sku) if h_sku else None
                    name_raw  = row.get(h_name) if h_name else None
                    qty_raw   = row.get(h_qty) if h_qty else None
                    price_raw = row.get(h_price) if h_price else None

                    if not date_raw or not sku_raw or not qty_raw or not price_raw:
                        missing = []
                        if not date_raw: missing.append("date/order_date")
                        if not sku_raw: missing.append("sku/product_id")
                        if not qty_raw: missing.append("quantity_sold/qty")
                        if not price_raw: missing.append("selling_price/unit_price_inr")
                        raise ValueError(f"Missing mandatory fields: {', '.join(missing)}")

                    try:
                        date_parsed = datetime.strptime(date_raw.strip(), "%Y-%m-%d")
                    except ValueError:
                        raise ValueError(f"Date format must be YYYY-MM-DD (got: '{date_raw}')")

                    sku_display = sku_raw.strip()
                    sku_normalized = sku_display.lower()
                    if not sku_normalized:
                        raise ValueError("SKU cannot be empty or whitespace.")

                    product_name_parsed = name_raw.strip() if name_raw and name_raw.strip() else sku_display

                    qty_parsed = _parse_int(qty_raw)
                    if qty_parsed is None or qty_parsed < 0:
                        raise ValueError(f"quantity_sold must be non-negative (got: '{qty_raw}')")

                    price_parsed = _parse_float(price_raw)
                    if price_parsed is None or price_parsed < 0:
                        raise ValueError(f"selling_price must be non-negative (got: '{price_raw}')")

                    cat_raw      = row.get(header_map.get("category", None))
                    unit_cost_raw = row.get(header_map.get("unit_cost", None))
                    disc_raw     = row.get(header_map.get("discount", None))
                    store_raw    = row.get(header_map.get("store_id", None))
                    inv_raw      = row.get(header_map.get("inventory_level", None))
                    promo_raw    = row.get(header_map.get("promotion_flag", None))
                    hol_raw      = row.get(header_map.get("holiday_flag", None))

                    unit_cost_parsed = _parse_float(unit_cost_raw)
                    if unit_cost_parsed is not None and unit_cost_parsed < 0:
                        raise ValueError(f"unit_cost must be non-negative (got: '{unit_cost_raw}')")

                    discount_parsed = _parse_float(disc_raw)
                    if discount_parsed is not None and discount_parsed < 0:
                        raise ValueError(f"discount must be non-negative (got: '{disc_raw}')")

                    inv_parsed = _parse_int(inv_raw)
                    if inv_parsed is not None and inv_parsed < 0:
                        raise ValueError(f"inventory_level must be non-negative (got: '{inv_raw}')")

                    raw_sale_dicts.append({
                        "retailer_id": upload.retailer_id,
                        "upload_id": upload.id,
                        "sku": sku_normalized,
                        "sku_display": sku_display,
                        "product_name": product_name_parsed,
                        "date": date_parsed,
                        "quantity_sold": qty_parsed,
                        "selling_price": price_parsed,
                        "category": cat_raw.strip() if cat_raw else None,
                        "unit_cost": unit_cost_parsed,
                        "discount": discount_parsed,
                        "store_id": store_raw.strip() if store_raw else None,
                        "inventory_level": inv_parsed,
                        "promotion_flag": _parse_bool(promo_raw),
                        "holiday_flag": _parse_bool(hol_raw),
                        "row_number_in_file": row_idx,
                        "source_row_raw": row,
                    })
                    rows_ingested += 1

                except Exception as row_err:
                    rows_rejected += 1
                    warnings_list.append(RowWarning(row=row_idx, reason=str(row_err)))
                    logger.warning(f"[WORKER] Row {row_idx} rejected: {row_err}")

        logger.info(
            f"[WORKER] CSV parsed: total={row_idx - 1} valid={rows_ingested} rejected={rows_rejected}"
        )

    except Exception as parse_err:
        tb = traceback.format_exc()
        logger.error(f"[WORKER] Fatal CSV parse error for {upload.upload_id}: {parse_err}", exc_info=True)
        await _fail_upload(upload, "csv_parsing", str(parse_err), tb)
        return

    # ------------------------------------------------------------------ #
    # Stage: Product upsert + RawSaleDocument bulk insert
    # ------------------------------------------------------------------ #
    if rows_ingested == 0:
        logger.error(f"[WORKER] All rows rejected for upload {upload.upload_id}")
        await _fail_upload(upload, "csv_parsing", "All rows in the CSV file failed validation.")
        return

    upload.current_stage = "raw_sales_ingestion"
    await upload.save()

    try:
        unique_skus: Dict[str, Tuple] = {}
        for item in raw_sale_dicts:
            s_norm = item["sku"]
            if s_norm not in unique_skus:
                unique_skus[s_norm] = (item["sku_display"], item["product_name"], item["category"])

        existing_products = await ProductDocument.find(
            ProductDocument.retailer_id == upload.retailer_id,
            {"sku": {"$in": list(unique_skus.keys())}},
        ).to_list()
        product_map = {p.sku: p for p in existing_products}

        new_products = []
        for s_norm, (s_disp, p_name, cat) in unique_skus.items():
            if s_norm not in product_map:
                p_doc = ProductDocument(
                    id=PydanticObjectId(),
                    retailer_id=upload.retailer_id,
                    sku=s_norm,
                    sku_display=s_disp,
                    product_name=p_name,
                    category=cat,
                    first_seen_upload_id=upload.id,
                    last_seen_upload_id=upload.id,
                )
                new_products.append(p_doc)

        if new_products:
            await ProductDocument.insert_many(new_products)
            for p in new_products:
                product_map[p.sku] = p

        raw_docs = []
        for item in raw_sale_dicts:
            p_obj = product_map.get(item["sku"])
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
                    source_row_raw=item["source_row_raw"],
                ))

        if raw_docs:
            t0 = time.perf_counter()
            await RawSaleDocument.insert_many(raw_docs)
            t1 = time.perf_counter()
            logger.info(f"[WORKER] Bulk inserted {len(raw_docs)} RawSaleDocuments in {t1 - t0:.2f}s")

        # Persist row statistics
        upload.row_count = row_idx - 1
        upload.rows_ingested = rows_ingested
        upload.rows_rejected = rows_rejected
        upload.row_warnings = warnings_list
        await upload.save()

    except Exception as ingest_err:
        tb = traceback.format_exc()
        logger.error(f"[WORKER] Raw ingestion failed for {upload.upload_id}: {ingest_err}", exc_info=True)
        await _fail_upload(upload, "raw_sales_ingestion", str(ingest_err), tb)
        return

    # ------------------------------------------------------------------ #
    # Stage: Downstream pipeline (feature engineering + ML inference)
    # ------------------------------------------------------------------ #
    try:
        await run_downstream_pipeline(upload)
    except Exception as pipe_err:
        tb = traceback.format_exc()
        logger.error(f"[WORKER] Downstream pipeline failed for {upload.upload_id}: {pipe_err}", exc_info=True)
        # If upload.status is already FAILED (set by _fail_upload inside run_downstream_pipeline),
        # do not overwrite the detailed stage info.
        if upload.status != UploadStatus.FAILED:
            await _fail_upload(upload, "downstream_pipeline", str(pipe_err), tb)
        return

    # ------------------------------------------------------------------ #
    # Success — set terminal status
    # ------------------------------------------------------------------ #
    if upload.status == UploadStatus.FAILED:
        # run_downstream_pipeline called _fail_upload internally; respect it.
        logger.warning(f"[WORKER] Upload {upload.upload_id} ended with FAILED during downstream pipeline.")
        return

    upload.status = UploadStatus.COMPLETED_WITH_WARNINGS if rows_rejected > 0 else UploadStatus.COMPLETED
    upload.current_stage = "completed"
    upload.processing_completed_at = datetime.now(timezone.utc)
    await upload.save()
    logger.info(f"[WORKER] Upload {upload.upload_id} → {upload.status}")

    # Clean up temporary staging CSV file after successful ingestion
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.info(f"[WORKER] Cleaned up temporary staging CSV file: {filepath}")
        except Exception as remove_err:
            logger.warning(f"[WORKER] Staging file cleanup warning: {remove_err}")


# ---------------------------------------------------------------------------
# Worker polling loop
# ---------------------------------------------------------------------------

async def worker_loop() -> None:
    """Infinite polling loop querying for new UPLOADED dataset entries."""
    logger.info(f"[WORKER] Entering polling loop. interval={settings.WORKER_POLL_INTERVAL_SECONDS}s")
    while True:
        try:
            # 1. Automatically recover/fail stale PROCESSING uploads older than 3 minutes (e.g. from server restarts)
            now_utc = datetime.now(timezone.utc)
            stale_cutoff = now_utc - timedelta(minutes=3)

            proc_uploads = await UploadDocument.find(
                UploadDocument.status == UploadStatus.PROCESSING
            ).to_list()

            stale_uploads = [
                u for u in proc_uploads
                if u.processing_started_at is not None and u.processing_started_at < stale_cutoff
            ]

            for stale in stale_uploads:
                logger.warning(f"[WORKER] Timing out stale processing job: {stale.upload_id}")
                stale.status = UploadStatus.FAILED
                stale.stage_errors = ["Upload processing timed out due to server restart."]
                await stale.save()

            # 2. Fetch oldest pending upload job (FIFO order)
            upload = await UploadDocument.find(
                {"status": {"$in": [UploadStatus.UPLOADED.value, "PENDING"]}}
            ).sort("+created_at").first_or_none()

            if upload:
                await process_single_upload(upload)
        except Exception as loop_err:
            logger.error(f"[WORKER] Polling loop error: {loop_err}", exc_info=True)

        await asyncio.sleep(settings.WORKER_POLL_INTERVAL_SECONDS)


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

async def main() -> None:
    """Bootstraps database, Beanie ODM model registries, and starts worker loop."""
    logger.info("[WORKER] Initializing background worker...")

    await connect_to_mongo()

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
        AnomalyCurrentDocument,
    ]
    await init_beanie(database=cast(Any, db), document_models=document_models)
    await create_all_indexes()

    try:
        await worker_loop()
    except asyncio.CancelledError:
        logger.info("[WORKER] Worker loop cancelled.")
    finally:
        await close_mongo_connection()
        logger.info("[WORKER] Worker process cleaned up.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[WORKER] Stopped by keyboard interrupt.")
        sys.exit(0)
