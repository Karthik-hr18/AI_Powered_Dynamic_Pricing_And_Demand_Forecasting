import asyncio
import logging
import random
from datetime import datetime, timedelta

from beanie import init_beanie

from app.core.constants import (
    AnomalyStage,
    AnomalyType,
    ForecastConfidenceLabel,
    ForecastPipelineType,
    ForecastTriggeredBy,
    InventoryClassification,
    InventoryMode,
    PricingEligibilityStatus,
    UploadStatus,
    UserRole,
)
from app.domains.anomaly.models import AnomalyCurrentDocument, FlaggedAnomaly
from app.domains.auth.models import UserDocument
from app.domains.forecasting.models import (
    ForecastCurrentDocument,
    ForecastHistoryDocument,
    ForecastHorizon,
    ForecastPrediction,
)
from app.domains.inventory.models import (
    InventoryCurrentDocument,
    TrueRiskDetail,
)
from app.domains.pricing.models import (
    BoundRange,
    CandidateGridEntry,
    PricingCurrentDocument,
    PricingHistoryDocument,
)
from app.domains.products.models import ProductDocument
from app.domains.sales_data.models import ProcessedSaleDocument, RawSaleDocument
from app.domains.uploads.models import UploadDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_demo_data")


# Comprehensive Product Catalogue definition (75 realistic retail items across 6 categories)
CATEGORIES_CATALOGUE = {
    "Dairy": [
        ("SKU-DAIRY-001", "Organic Whole Milk 1L", 3.99, 2.50),
        ("SKU-DAIRY-002", "Greek Yogurt Plain 500g", 4.49, 2.80),
        ("SKU-DAIRY-003", "Unsalted Butter 250g", 3.79, 2.20),
        ("SKU-DAIRY-004", "Cheddar Cheese Block 400g", 5.99, 3.80),
        ("SKU-DAIRY-005", "Almond Milk Unsweetened 1L", 3.49, 2.10),
        ("SKU-DAIRY-006", "Heavy Whipping Cream 250ml", 2.99, 1.70),
        ("SKU-DAIRY-007", "Mozzarella Shredded 300g", 4.99, 3.10),
        ("SKU-DAIRY-008", "Sour Cream 200g", 2.29, 1.30),
        ("SKU-DAIRY-009", "Cottage Cheese 400g", 3.29, 1.90),
        ("SKU-DAIRY-010", "Oat Milk Barista 1L", 3.99, 2.40),
        ("SKU-DAIRY-011", "Swiss Cheese Slices 200g", 4.29, 2.60),
        ("SKU-DAIRY-012", "Cream Cheese Spread 250g", 3.19, 1.80),
    ],
    "Bakery": [
        ("SKU-BAKE-001", "Artisan Sourdough Bread 500g", 4.99, 2.20),
        ("SKU-BAKE-002", "Whole Wheat Sandwich Bread", 3.29, 1.40),
        ("SKU-BAKE-003", "Butter Croissant 4-Pack", 4.49, 2.00),
        ("SKU-BAKE-004", "Everything Bagels 6-Pack", 3.99, 1.80),
        ("SKU-BAKE-005", "Chocolate Chip Muffins 2-Pack", 3.49, 1.50),
        ("SKU-BAKE-006", "Brioche Hamburger Buns 4s", 3.79, 1.60),
        ("SKU-BAKE-007", "Cinnamon Rolls 4-Pack", 4.99, 2.30),
        ("SKU-BAKE-008", "Multigrain Loaf 600g", 3.89, 1.70),
        ("SKU-BAKE-009", "Pita Bread White 5-Pack", 2.49, 1.00),
        ("SKU-BAKE-010", "French Baguette 300g", 2.29, 0.90),
        ("SKU-BAKE-011", "Blueberry Scones 2-Pack", 3.99, 1.80),
        ("SKU-BAKE-012", "Tortilla Wraps Large 8-Pack", 3.19, 1.30),
    ],
    "Beverages": [
        ("SKU-BEV-001", "Cold Brew Coffee Concentrate 946ml", 7.99, 4.20),
        ("SKU-BEV-002", "Sparkling Water Lemon 12-Pack", 5.49, 3.10),
        ("SKU-BEV-003", "Pure Orange Juice No Pulp 1.5L", 4.79, 2.80),
        ("SKU-BEV-004", "Green Tea Unsweetened 500ml", 1.99, 0.90),
        ("SKU-BEV-005", "Kombucha Ginger Lemon 473ml", 3.99, 2.10),
        ("SKU-BEV-006", "Energy Drink Sugar Free 250ml", 2.79, 1.30),
        ("SKU-BEV-007", "Coconut Water 100% Pure 1L", 4.29, 2.40),
        ("SKU-BEV-008", "Apple Juice Organic 1L", 3.69, 2.00),
        ("SKU-BEV-009", "Craft Cola 4-Pack Bottles", 6.49, 3.60),
        ("SKU-BEV-010", "Iced Black Tea Peach 1.5L", 3.19, 1.60),
        ("SKU-BEV-011", "Matcha Latte Drink 330ml", 3.89, 2.00),
        ("SKU-BEV-012", "Electrolyte Hydration Drink 500ml", 2.49, 1.10),
        ("SKU-BEV-013", "Espresso Beans Medium Roast 340g", 12.99, 7.50),
    ],
    "Snacks": [
        ("SKU-SNACK-001", "Sea Salt Potato Chips 180g", 3.49, 1.50),
        ("SKU-SNACK-002", "Roasted Almonds Salted 200g", 6.99, 4.00),
        ("SKU-SNACK-003", "Dark Chocolate Bar 70% 100g", 2.99, 1.40),
        ("SKU-SNACK-004", "Granola Bars Variety 6-Pack", 4.19, 2.00),
        ("SKU-SNACK-005", "Organic Corn Tortilla Chips 250g", 3.79, 1.70),
        ("SKU-SNACK-006", "Mild Salsa Dip 400g", 3.29, 1.50),
        ("SKU-SNACK-007", "Mixed Berry Trail Mix 250g", 5.49, 3.00),
        ("SKU-SNACK-008", "Pretzel Twists Salted 300g", 2.89, 1.20),
        ("SKU-SNACK-009", "Rice Cakes Cheddar 150g", 2.49, 1.00),
        ("SKU-SNACK-010", "Dried Mango Slices 150g", 4.99, 2.70),
        ("SKU-SNACK-011", "Protein Bar Chocolate 60g", 2.79, 1.30),
        ("SKU-SNACK-012", "Gummy Bears Fruit Flavored 200g", 2.19, 0.90),
        ("SKU-SNACK-013", "Popcorn Butter Flavored 100g", 1.99, 0.70),
    ],
    "Household": [
        ("SKU-HOUSE-001", "Paper Towels 2-Ply 6 Rolls", 8.99, 5.20),
        ("SKU-HOUSE-002", "Dish Soap Citrus Scent 739ml", 3.79, 1.90),
        ("SKU-HOUSE-003", "Laundry Detergent Pods 42ct", 14.99, 9.10),
        ("SKU-HOUSE-004", "Trash Bags 13-Gallon 40ct", 9.49, 5.50),
        ("SKU-HOUSE-005", "All-Purpose Cleaner Spray 946ml", 4.29, 2.20),
        ("SKU-HOUSE-006", "Disinfecting Wipes 75ct", 5.29, 2.90),
        ("SKU-HOUSE-007", "Toilet Paper 3-Ply 12 Rolls", 11.99, 7.30),
        ("SKU-HOUSE-008", "Sponges Heavy Duty 4-Pack", 2.99, 1.20),
        ("SKU-HOUSE-009", "Aluminum Foil 75 sq ft", 4.79, 2.60),
        ("SKU-HOUSE-010", "Food Storage Bags Gallon 30ct", 3.99, 1.90),
        ("SKU-HOUSE-011", "Fabric Softener Liquid 1.5L", 6.29, 3.60),
        ("SKU-HOUSE-012", "Air Freshener Spray 250ml", 3.49, 1.70),
        ("SKU-HOUSE-013", "Hand Soap Refill 1L", 4.99, 2.50),
    ],
    "Personal Care": [
        ("SKU-CARE-001", "Hydrating Body Wash 500ml", 5.99, 3.20),
        ("SKU-CARE-002", "Daily Shampoo Moisture 400ml", 6.49, 3.50),
        ("SKU-CARE-003", "Fluoride Toothpaste Mint 150g", 3.49, 1.60),
        ("SKU-CARE-004", "Soft Bristle Toothbrush 2-Pack", 3.99, 1.70),
        ("SKU-CARE-005", "Moisturizing Face Cream 100ml", 12.49, 6.80),
        ("SKU-CARE-006", "Antiperspirant Deodorant 75g", 4.29, 2.10),
        ("SKU-CARE-007", "Cotton Swabs 500ct Box", 2.99, 1.30),
        ("SKU-CARE-008", "Foaming Hand Sanitizer 250ml", 3.29, 1.50),
        ("SKU-CARE-009", "Conditioner Repair 400ml", 6.49, 3.50),
        ("SKU-CARE-010", "Sunscreen Lotion SPF 50 200ml", 9.99, 5.60),
        ("SKU-CARE-011", "Razor Cartridges 4-Pack", 11.49, 6.70),
        ("SKU-CARE-012", "Micellar Cleansing Water 400ml", 7.29, 3.90),
    ]
}


from app.core.db.connection import connect_to_mongo, get_database, close_mongo_connection


async def seed_demo_data():
    logger.info("Initializing database connection for demo data seeding...")
    await connect_to_mongo()
    db = get_database()

    await init_beanie(
        database=db,
        document_models=[
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
        ],
    )

    logger.info("Purging existing database collections for a clean seed environment...")
    await UserDocument.get_pymongo_collection().drop()
    await ProductDocument.get_pymongo_collection().drop()
    await UploadDocument.get_pymongo_collection().drop()
    await RawSaleDocument.get_pymongo_collection().drop()
    await ProcessedSaleDocument.get_pymongo_collection().drop()
    await ForecastCurrentDocument.get_pymongo_collection().drop()
    await ForecastHistoryDocument.get_pymongo_collection().drop()
    await PricingCurrentDocument.get_pymongo_collection().drop()
    await InventoryCurrentDocument.get_pymongo_collection().drop()
    await AnomalyCurrentDocument.get_pymongo_collection().drop()

    # --------------------------------------------------------------------------
    # 1. Seed Accounts (1 Admin + 5 Retailers)
    # --------------------------------------------------------------------------
    logger.info("Seeding 1 Admin and 5 Retailer accounts...")
    
    admin_user = UserDocument(
        firebase_uid="admin_karthik_uid",
        email="karthikhr676@gmail.com",
        role=UserRole.ADMIN,
        is_email_verified=True,
        is_active=True,
    )
    await admin_user.insert()

    # Demo Mart (Primary Demo Retailer)
    demo_mart = UserDocument(
        firebase_uid="karthikhrvidyanidhi676",
        email="karthikhrvidyanidhi676@gmail.com",
        role=UserRole.RETAILER,
        business_name="Demo Mart Premium Retailers",
        is_email_verified=True,
        is_active=True,
    )
    await demo_mart.insert()

    # Secondary Retailers for Admin Panel realism
    other_retailers = [
        ("freshchoice_uid", "freshchoice@example.com", "Fresh Choice Supermarket", True),
        ("metrofoods_uid", "metrofoods@example.com", "Metro Foods Market", True),
        ("apex_uid", "apex@example.com", "Apex Retail Group", True),
        ("xyzexpress_uid", "xyzexpress@example.com", "XYZ Express Mini", False),
    ]

    for uid, email, bname, active in other_retailers:
        u = UserDocument(
            firebase_uid=uid,
            email=email,
            role=UserRole.RETAILER,
            business_name=bname,
            is_email_verified=True,
            is_active=active,
        )
        await u.insert()

    logger.info("Successfully seeded 6 User accounts in MongoDB.")

    logger.info("Seeding upload history records...")
    now = datetime.utcnow()
    u1 = UploadDocument(
        retailer_id=demo_mart.id,
        original_filename="sales_august_2026.csv",
        file_size_bytes=2450800,
        row_count=14820,
        rows_ingested=14820,
        schema_mapping_used="standard",
        status=UploadStatus.COMPLETED,
        current_stage="completed",
        created_at=now - timedelta(hours=2),
    )
    await u1.insert()

    u2 = UploadDocument(
        retailer_id=demo_mart.id,
        original_filename="sales_july_2026.csv",
        file_size_bytes=2100400,
        row_count=12400,
        rows_ingested=12400,
        schema_mapping_used="standard",
        status=UploadStatus.COMPLETED,
        current_stage="completed",
        created_at=now - timedelta(days=15),
    )
    await u2.insert()

    u3 = UploadDocument(
        retailer_id=demo_mart.id,
        original_filename="inventory_baseline.csv",
        file_size_bytes=890100,
        row_count=75,
        rows_ingested=75,
        schema_mapping_used="standard",
        status=UploadStatus.COMPLETED,
        current_stage="completed",
        created_at=now - timedelta(days=30),
    )
    await u3.insert()

    # --------------------------------------------------------------------------
    # 2. Seed 75 Products for Demo Mart
    # --------------------------------------------------------------------------
    logger.info("Seeding 75 retail products for Demo Mart...")
    created_products = []
    product_prices = {}
    
    for category, items in CATEGORIES_CATALOGUE.items():
        for sku, p_name, price, cost in items:
            p = ProductDocument(
                retailer_id=demo_mart.id,
                sku=sku.lower(),
                sku_display=sku,
                product_name=p_name,
                category=category,
                is_active=True,
                first_seen_upload_id=u1.id,
                last_seen_upload_id=u1.id,
            )
            await p.insert()
            created_products.append(p)
            product_prices[p.id] = (price, cost)

    logger.info(f"Seeded {len(created_products)} products.")

    # --------------------------------------------------------------------------
    # 3. Seed ~14,820 Transaction Records over 60 Days with Seasonality
    # --------------------------------------------------------------------------
    logger.info("Generating ~14,820 daily transaction sales records across trailing 60 days...")
    total_sales_count = 0
    total_revenue_acc = 0.0

    processed_sales_docs = []

    # Generate daily records for each product over past 60 days
    for p in created_products:
        price, cost = product_prices[p.id]
        # Base daily sales velocity based on category
        if p.category in ["Dairy", "Bakery"]:
            base_daily_qty = random.randint(8, 16)
        elif p.category in ["Beverages", "Snacks"]:
            base_daily_qty = random.randint(6, 14)
        else:
            base_daily_qty = random.randint(2, 7)

        for day_offset in range(60, 0, -1):
            sale_date = now - timedelta(days=day_offset)
            is_weekend = sale_date.weekday() in [5, 6]
            multiplier = 1.35 if is_weekend else 1.0

            # Add gaussian noise & compute quantity
            qty = max(1, int(random.gauss(base_daily_qty * multiplier, 2)))

            sale_doc = ProcessedSaleDocument(
                retailer_id=demo_mart.id,
                product_id=p.id,
                date=sale_date,
                quantity_sold=int(qty),
                selling_price=price,
                unit_cost=cost,
                category=p.category,
                day_of_week=sale_date.weekday(),
                is_weekend=is_weekend,
                source_upload_ids=[u1.id],
                feature_engineering_version="v1.0",
            )
            processed_sales_docs.append(sale_doc)
            total_sales_count += 1
            if day_offset <= 30:
                total_revenue_acc += qty * price

    # Bulk insert sales in chunks of 2,000 for high performance
    chunk_size = 2000
    for i in range(0, len(processed_sales_docs), chunk_size):
        chunk = processed_sales_docs[i : i + chunk_size]
        await ProcessedSaleDocument.insert_many(chunk)

    logger.info(f"Seeded {total_sales_count} sales records. Trailing 30d Revenue: ${total_revenue_acc:,.2f}")



    # --------------------------------------------------------------------------
    # 5. Programmatically Execute / Seed Pipeline Documents (Forecast, Pricing, Inventory, Anomaly)
    # --------------------------------------------------------------------------
    logger.info("Populating ML pipeline documents (Forecasts, Pricing Recommendations, Inventory Risk, Anomalies)...")

    for idx, p in enumerate(created_products):
        # 5a. Forecast Current Document
        confidence_lbl = (
            ForecastConfidenceLabel.HIGH if idx % 4 != 0
            else ForecastConfidenceLabel.LOW if idx % 7 != 0
            else ForecastConfidenceLabel.NONE
        )

        predictions_7d = [
            ForecastPrediction(
                date=now + timedelta(days=d),
                predicted_quantity=round(max(5.0, random.gauss(45, 8)), 1),
            )
            for d in range(1, 8)
        ]

        if confidence_lbl != ForecastConfidenceLabel.NONE:
            fc_doc = ForecastCurrentDocument(
                retailer_id=demo_mart.id,
                product_id=p.id,
                history_days_available=60,
                confidence_label=confidence_lbl,
                pipeline_type=ForecastPipelineType.FULL if confidence_lbl == ForecastConfidenceLabel.HIGH else ForecastPipelineType.FALLBACK,
                horizon_7d=ForecastHorizon(predictions=predictions_7d, confidence=confidence_lbl.value.lower()),
                model_version="v1.0",
                run_id=u1.id,
                upload_id=u1.id,
                run_timestamp=now,
            )
            await fc_doc.insert()

            # Also seed Forecast History Document for 7-day actual vs forecast timeline
            predictions_hist = [
                ForecastPrediction(
                    date=now - timedelta(days=d),
                    predicted_quantity=round(max(5.0, random.gauss(42, 6)), 1),
                )
                for d in range(7, 0, -1)
            ]
            hist_doc = ForecastHistoryDocument(
                retailer_id=demo_mart.id,
                product_id=p.id,
                history_days_available=60,
                confidence_label=confidence_lbl,
                pipeline_type=ForecastPipelineType.FULL,
                horizon_7d=ForecastHorizon(predictions=predictions_hist, confidence="high"),
                model_version="v1.0",
                run_id=u1.id,
                upload_id=u1.id,
                triggered_by=ForecastTriggeredBy.UPLOAD,
                run_timestamp=now - timedelta(days=7),
            )
            await hist_doc.insert()

        # 5b. Pricing Current Document
        base_price, cost_price = product_prices[p.id]
        min_bound = round(cost_price * 1.15, 2)
        max_bound = round(base_price * 1.30, 2)

        # Highlight Organic Whole Milk (SKU-DAIRY-001) as the Hero Recommendation
        if p.sku == "sku-dairy-001":
            rec_price = 4.25
        elif p.category in ["Dairy", "Bakery"]:
            rec_price = round(base_price * random.choice([1.05, 1.08, 0.95]), 2)
        else:
            rec_price = round(base_price * random.choice([1.03, 1.06, 0.98]), 2)

        candidates = [
            CandidateGridEntry(candidate_price=round(base_price * mult, 2), estimated_demand=50.0, estimated_revenue=round(base_price * mult * 50, 2))
            for mult in [0.9, 0.95, 1.0, 1.05, 1.1]
        ]

        pr_doc = PricingCurrentDocument(
            retailer_id=demo_mart.id,
            product_id=p.id,
            eligibility_status=PricingEligibilityStatus.ELIGIBLE,
            current_price=base_price,
            bound_pct=0.20,
            bound_range=BoundRange(min=min_bound, max=max_bound),
            candidate_grid=candidates,
            recommended_price=rec_price,
            expected_revenue=round(rec_price * 50.0, 2),
            model_version="v1.0",
            run_id=u1.id,
            upload_id=u1.id,
            run_timestamp=now,
        )
        await pr_doc.insert()

        # 5c. Inventory Current Document
        # Mix: 80% Healthy, 15% Overstock, 5% Stockout Risk
        if idx in [2, 14, 28]:
            inv_classification = InventoryClassification.STOCKOUT_RISK
            runout = 4
        elif idx % 6 == 0:
            inv_classification = InventoryClassification.OVERSTOCK_RISK
            runout = 45
        else:
            inv_classification = InventoryClassification.HEALTHY
            runout = 18

        inv_doc = InventoryCurrentDocument(
            retailer_id=demo_mart.id,
            product_id=p.id,
            mode=InventoryMode.TRUE_RISK,
            true_risk=TrueRiskDetail(
                days_of_cover=float(runout),
                classification=inv_classification,
                current_inventory_level=runout * 12,
                horizon_used="7d",
            ),
            forecast_horizon_used="7d",
            forecast_run_id=u1.id,
            upload_id=u1.id,
            run_timestamp=now,
        )
        await inv_doc.insert()

        # 5d. Anomaly Current Document (3 active alerts)
        has_alerts = idx in [0, 8, 25]
        flagged = []
        if has_alerts:
            anom_type = AnomalyType.SPIKE if idx == 0 else AnomalyType.UNUSUAL if idx == 8 else AnomalyType.DROP
            flagged.append(
                FlaggedAnomaly(
                    date=now - timedelta(days=1),
                    stage=AnomalyStage.POST_UPLOAD_ALERT,
                    anomaly_type=anom_type,
                    severity_score=2.8,
                    explanation=f"Significant statistical deviation detected for {p.product_name}.",
                    acknowledged=False,
                )
            )

        anom_doc = AnomalyCurrentDocument(
            retailer_id=demo_mart.id,
            product_id=p.id,
            has_unreviewed_alerts=has_alerts,
            total_flagged_count=len(flagged),
            flagged_anomalies=flagged,
            model_version="v1.0",
            upload_id=u1.id,
            run_timestamp=now,
        )
        await anom_doc.insert()

    await close_mongo_connection()
    logger.info("Successfully completed demo database seeding!")
    logger.info("=" * 60)
    logger.info("DEMO RETAILER CREDENTIALS:")
    logger.info("  Email:    karthikhrvidyanidhi676@gmail.com")
    logger.info("  Password: 11111111")
    logger.info("ADMIN CREDENTIALS:")
    logger.info("  Email:    karthikhr676@gmail.com")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
