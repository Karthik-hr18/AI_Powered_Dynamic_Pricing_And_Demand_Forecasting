import logging
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ml.shared.feature_engineering")


def aggregate_raw_sales_daily(raw_sales: List[Any]) -> pd.DataFrame:
    """
    Groups raw transaction entries by date and product, summing quantities
    and calculating a quantity-weighted average selling price.
    """
    if not raw_sales:
        return pd.DataFrame()

    rows = []
    for doc in raw_sales:
        rows.append({
            "product_id": str(getattr(doc, "product_id", "")),
            "date": pd.to_datetime(getattr(doc, "date", datetime.now())).normalize(),
            "quantity_sold": getattr(doc, "quantity_sold", 0),
            "selling_price": getattr(doc, "selling_price", 0.0),
            "unit_cost": getattr(doc, "unit_cost", np.nan) if getattr(doc, "unit_cost", None) is not None else np.nan,
            "discount": getattr(doc, "discount", 0.0) if getattr(doc, "discount", None) is not None else 0.0,
            "store_id": getattr(doc, "store_id", None),
            "inventory_level": getattr(doc, "inventory_level", np.nan) if getattr(doc, "inventory_level", None) is not None else np.nan,
            "promotion_flag": 1 if getattr(doc, "promotion_flag", False) else 0,
            "holiday_flag": 1 if getattr(doc, "holiday_flag", False) else 0,
            "category": getattr(doc, "category", None)
        })
    
    df = pd.DataFrame(rows)

    def group_daily(group):
        qty_sum = group["quantity_sold"].sum()
        if qty_sum > 0:
            avg_price = (group["selling_price"] * group["quantity_sold"]).sum() / qty_sum
        else:
            avg_price = group["selling_price"].mean()
            
        unit_cost = group["unit_cost"].mean()
        inv_level = group["inventory_level"].mean()
        
        # Safely extract first string identifier
        store_id = group["store_id"].dropna().iloc[0] if not group["store_id"].dropna().empty else None
        category = group["category"].dropna().iloc[0] if not group["category"].dropna().empty else None
        
        return pd.Series({
            "quantity_sold": qty_sum,
            "selling_price": avg_price,
            "unit_cost": unit_cost,
            "discount": group["discount"].mean(),
            "store_id": store_id,
            "inventory_level": inv_level,
            "promotion_flag": bool(group["promotion_flag"].max()),
            "holiday_flag": bool(group["holiday_flag"].max()),
            "category": category
        })
        
    aggregated = df.groupby(["product_id", "date"]).apply(group_daily, include_groups=False).reset_index()
    return aggregated


def compute_rolling_features(
    df: pd.DataFrame, 
    historical_processed: Optional[List[Any]] = None
) -> List[Dict[str, Any]]:
    """
    Appends historical records, builds calendar continuity, zero-fills sales quantities,
    calculates lags/rolling averages, and formats output dictionaries to be JSON-compatible (cleans NaNs).
    """
    if df.empty:
        return []

    # 1. Integrate historical processed records to get prior context
    hist_rows = []
    if historical_processed:
        for doc in historical_processed:
            hist_rows.append({
                "product_id": str(getattr(doc, "product_id", "")),
                "date": pd.to_datetime(getattr(doc, "date", datetime.now())).normalize(),
                "quantity_sold": getattr(doc, "quantity_sold", 0),
                "selling_price": getattr(doc, "selling_price", 0.0),
                "unit_cost": getattr(doc, "unit_cost", np.nan) if getattr(doc, "unit_cost", None) is not None else np.nan,
                "discount": getattr(doc, "discount", 0.0) if getattr(doc, "discount", None) is not None else 0.0,
                "store_id": getattr(doc, "store_id", None),
                "inventory_level": getattr(doc, "inventory_level", np.nan) if getattr(doc, "inventory_level", None) is not None else np.nan,
                "promotion_flag": getattr(doc, "promotion_flag", False),
                "holiday_flag": getattr(doc, "holiday_flag", False),
                "category": getattr(doc, "category", None)
            })

    if hist_rows:
        hist_df = pd.DataFrame(hist_rows)
        # Deduplicate to avoid overlap conflicts (preferring new uploads data over historical)
        combined_df = pd.concat([df, hist_df]).drop_duplicates(subset=["product_id", "date"], keep="first")
    else:
        combined_df = df

    processed_records = []

    # Group by product to process individual timelines
    for prod_id, prod_group in combined_df.groupby("product_id"):
        prod_group = prod_group.sort_values("date").set_index("date").copy()

        # 2. Build continuous daily calendar range
        min_date = prod_group.index.min()
        max_date = prod_group.index.max()
        all_dates = pd.date_range(start=min_date, end=max_date, freq="D")

        # Reindex to continuous timeline
        prod_continuous = prod_group.reindex(all_dates).copy()
        
        # 3. Propagate and fill variables
        prod_continuous["quantity_sold"] = prod_continuous["quantity_sold"].fillna(0.0)
        prod_continuous["discount"] = prod_continuous["discount"].fillna(0.0)
        prod_continuous["promotion_flag"] = prod_continuous["promotion_flag"].fillna(False).astype(bool)
        prod_continuous["holiday_flag"] = prod_continuous["holiday_flag"].fillna(False).astype(bool)
        prod_continuous["product_id"] = prod_continuous["product_id"].fillna(prod_id)

        # Forward fill and backward fill standing variables (price, cost, store, category)
        prod_continuous["selling_price"] = prod_continuous["selling_price"].ffill().bfill()
        prod_continuous["unit_cost"] = prod_continuous["unit_cost"].ffill().bfill()
        prod_continuous["inventory_level"] = prod_continuous["inventory_level"].ffill().bfill()
        prod_continuous["store_id"] = prod_continuous["store_id"].ffill().bfill()
        prod_continuous["category"] = prod_continuous["category"].ffill().bfill()

        # 4. Perform lag and rolling average calculations
        prod_continuous["lag_1d_quantity"] = prod_continuous["quantity_sold"].shift(1)
        prod_continuous["rolling_avg_7d"] = prod_continuous["quantity_sold"].rolling(window=7, min_periods=7).mean()
        prod_continuous["rolling_avg_30d"] = prod_continuous["quantity_sold"].rolling(window=30, min_periods=30).mean()

        # Enforce price change logic: True if selling_price differs from previous day's price
        lag_price = prod_continuous["selling_price"].shift(1)
        prod_continuous["price_change_flag"] = (prod_continuous["selling_price"] != lag_price) & lag_price.notna()

        # 5. Format results to JSON-friendly records (filtering NaNs to None)
        prod_continuous = prod_continuous.reset_index().rename(columns={"index": "date"})
        
        for _, row in prod_continuous.iterrows():
            row_date = row["date"].to_pydatetime()
            record = {
                "product_id": row["product_id"],
                "date": row_date,
                "quantity_sold": float(row["quantity_sold"]),
                "selling_price": float(row["selling_price"]) if not pd.isna(row["selling_price"]) else 0.0,
                "unit_cost": float(row["unit_cost"]) if not pd.isna(row["unit_cost"]) else None,
                "discount": float(row["discount"]) if not pd.isna(row["discount"]) else 0.0,
                "store_id": row["store_id"] if not pd.isna(row["store_id"]) else None,
                "inventory_level": int(row["inventory_level"]) if not pd.isna(row["inventory_level"]) else None,
                "promotion_flag": bool(row["promotion_flag"]),
                "holiday_flag": bool(row["holiday_flag"]),
                "category": row["category"] if not pd.isna(row["category"]) else None,
                "lag_1d_quantity": int(row["lag_1d_quantity"]) if not pd.isna(row["lag_1d_quantity"]) else None,
                "rolling_avg_7d": float(row["rolling_avg_7d"]) if not pd.isna(row["rolling_avg_7d"]) else None,
                "rolling_avg_30d": float(row["rolling_avg_30d"]) if not pd.isna(row["rolling_avg_30d"]) else None,
                "price_change_flag": bool(row["price_change_flag"]),
                "day_of_week": row_date.weekday(),
                "is_weekend": row_date.weekday() in (5, 6),
                "feature_engineering_version": "1.0.0-mock"
            }
            processed_records.append(record)

    return processed_records
