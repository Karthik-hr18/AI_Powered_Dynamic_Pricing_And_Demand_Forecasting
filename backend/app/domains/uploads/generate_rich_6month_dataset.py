import csv
import random
from datetime import date, datetime, timedelta
import os

def generate_rich_6month_kirana_dataset():
    # Set seed for reproducible, high-quality simulation
    random.seed(42)
    
    docs_dir = "c:/Users/karth/Projects/AI Powered/docs"
    os.makedirs(docs_dir, exist_ok=True)
    
    # 1. Catalog of 50 Rich Kirana Store SKUs covering 10 diverse categories
    catalog = [
        # --- Staples & Grains ---
        {"Product_ID": "P001", "Product_Name": "Aashirvaad Superior Sharbati Atta 5kg", "Category": "Flours", "Brand": "Aashirvaad", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 275.0, "Cost_Price_INR": 220.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.4},
        {"Product_ID": "P002", "Product_Name": "Fortune Special Biryani Basmati Rice 5kg", "Category": "Rice", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 30, "Unit_Price_INR": 560.0, "Cost_Price_INR": 450.0, "Base_Stock": 140, "Restock_Qty": 100, "Velocity": 1.2},
        {"Product_ID": "P003", "Product_Name": "Tata Sampann Organic Unpolished Toor Dal 1kg", "Category": "Pulses", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 175.0, "Cost_Price_INR": 138.0, "Base_Stock": 180, "Restock_Qty": 150, "Velocity": 1.5},
        {"Product_ID": "P004", "Product_Name": "Tata Sampann Organic Moong Dal 1kg", "Category": "Pulses", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 35, "Unit_Price_INR": 155.0, "Cost_Price_INR": 122.0, "Base_Stock": 150, "Restock_Qty": 120, "Velocity": 1.3},
        {"Product_ID": "P005", "Product_Name": "Aashirvaad Organic Chana Dal 1kg", "Category": "Pulses", "Brand": "Aashirvaad", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 140.0, "Cost_Price_INR": 110.0, "Base_Stock": 140, "Restock_Qty": 120, "Velocity": 1.2},
        {"Product_ID": "P006", "Product_Name": "Tata Sampann Organic Poha 500g", "Category": "Flours", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 65.0, "Cost_Price_INR": 48.0, "Base_Stock": 160, "Restock_Qty": 130, "Velocity": 1.4},
        {"Product_ID": "P007", "Product_Name": "MTR Roasted Rava 1kg", "Category": "Flours", "Brand": "MTR", "Supplier_ID": "S003", "Reorder_Level": 35, "Unit_Price_INR": 85.0, "Cost_Price_INR": 65.0, "Base_Stock": 140, "Restock_Qty": 110, "Velocity": 1.1},
        
        # --- Cooking Oil & Ghee ---
        {"Product_ID": "P008", "Product_Name": "Fortune Sunlite Refined Sunflower Oil 1L Pouch", "Category": "Oil & Ghee", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 50, "Unit_Price_INR": 145.0, "Cost_Price_INR": 120.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.8},
        {"Product_ID": "P009", "Product_Name": "Dhara Kachi Ghani Mustard Oil 1L Bottle", "Category": "Oil & Ghee", "Brand": "Dhara", "Supplier_ID": "S001", "Reorder_Level": 40, "Unit_Price_INR": 165.0, "Cost_Price_INR": 135.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P010", "Product_Name": "Amul Pure Cow Desi Ghee 1L Tin", "Category": "Oil & Ghee", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 45, "Unit_Price_INR": 620.0, "Cost_Price_INR": 520.0, "Base_Stock": 150, "Restock_Qty": 100, "Velocity": 1.3},
        {"Product_ID": "P011", "Product_Name": "Nandini Pure Cow Ghee 500ml Pouch", "Category": "Oil & Ghee", "Brand": "Nandini", "Supplier_ID": "S004", "Reorder_Level": 40, "Unit_Price_INR": 310.0, "Cost_Price_INR": 260.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.4},

        # --- Dairy, Breakfast & Spreads ---
        {"Product_ID": "P012", "Product_Name": "Amul Pasteurised Salted Butter 500g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 45, "Unit_Price_INR": 275.0, "Cost_Price_INR": 235.0, "Base_Stock": 180, "Restock_Qty": 150, "Velocity": 1.6},
        {"Product_ID": "P013", "Product_Name": "Amul Processed Cheese Block 400g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 35, "Unit_Price_INR": 230.0, "Cost_Price_INR": 190.0, "Base_Stock": 140, "Restock_Qty": 110, "Velocity": 1.2},
        {"Product_ID": "P014", "Product_Name": "Amul Fresh Malai Paneer 200g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 30, "Unit_Price_INR": 95.0, "Cost_Price_INR": 78.0, "Base_Stock": 130, "Restock_Qty": 100, "Velocity": 1.5},
        {"Product_ID": "P015", "Product_Name": "Nestle Milkmaid Sweetened Condensed Milk 400g", "Category": "Dairy", "Brand": "Nestle", "Supplier_ID": "S005", "Reorder_Level": 35, "Unit_Price_INR": 145.0, "Cost_Price_INR": 115.0, "Base_Stock": 120, "Restock_Qty": 90, "Velocity": 1.1},
        {"Product_ID": "P016", "Product_Name": "Kelloggs Corn Flakes Original 500g", "Category": "Instant Food", "Brand": "Kelloggs", "Supplier_ID": "S005", "Reorder_Level": 35, "Unit_Price_INR": 210.0, "Cost_Price_INR": 168.0, "Base_Stock": 130, "Restock_Qty": 100, "Velocity": 1.1},
        {"Product_ID": "P017", "Product_Name": "Saffola Masala Oats Classic 500g", "Category": "Instant Food", "Brand": "Saffola", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 175.0, "Cost_Price_INR": 135.0, "Base_Stock": 150, "Restock_Qty": 120, "Velocity": 1.3},
        {"Product_ID": "P018", "Product_Name": "Kissan Mixed Fruit Jam 1kg", "Category": "Spreads", "Brand": "Kissan", "Supplier_ID": "S005", "Reorder_Level": 30, "Unit_Price_INR": 280.0, "Cost_Price_INR": 220.0, "Base_Stock": 120, "Restock_Qty": 90, "Velocity": 1.0},

        # --- Tea, Coffee & Beverages ---
        {"Product_ID": "P019", "Product_Name": "Tata Tea Gold Royal 500g", "Category": "Beverages", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 50, "Unit_Price_INR": 310.0, "Cost_Price_INR": 245.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.7},
        {"Product_ID": "P020", "Product_Name": "Brooke Bond Red Label Tea 500g", "Category": "Beverages", "Brand": "Red Label", "Supplier_ID": "S006", "Reorder_Level": 50, "Unit_Price_INR": 290.0, "Cost_Price_INR": 230.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.6},
        {"Product_ID": "P021", "Product_Name": "Wagh Bakri Premium Masala Tea 500g", "Category": "Beverages", "Brand": "Wagh Bakri", "Supplier_ID": "S006", "Reorder_Level": 35, "Unit_Price_INR": 275.0, "Cost_Price_INR": 215.0, "Base_Stock": 140, "Restock_Qty": 110, "Velocity": 1.2},
        {"Product_ID": "P022", "Product_Name": "Nescafe Classic Instant Coffee Jar 100g", "Category": "Beverages", "Brand": "Nescafe", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 340.0, "Cost_Price_INR": 270.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.4},
        {"Product_ID": "P023", "Product_Name": "Bru Instant Coffee Jar 100g", "Category": "Beverages", "Brand": "Bru", "Supplier_ID": "S006", "Reorder_Level": 40, "Unit_Price_INR": 295.0, "Cost_Price_INR": 235.0, "Base_Stock": 150, "Restock_Qty": 120, "Velocity": 1.3},
        {"Product_ID": "P024", "Product_Name": "Cadbury Bournvita Pro-Health Drink 1kg", "Category": "Beverages", "Brand": "Cadbury", "Supplier_ID": "S007", "Reorder_Level": 40, "Unit_Price_INR": 420.0, "Cost_Price_INR": 335.0, "Base_Stock": 150, "Restock_Qty": 110, "Velocity": 1.3},

        # --- Snacks, Biscuits & Noodles ---
        {"Product_ID": "P025", "Product_Name": "Maggi 2-Minute Masala Noodles 12-Pack 840g", "Category": "Instant Food", "Brand": "Nestle", "Supplier_ID": "S005", "Reorder_Level": 60, "Unit_Price_INR": 168.0, "Cost_Price_INR": 134.0, "Base_Stock": 250, "Restock_Qty": 200, "Velocity": 2.0},
        {"Product_ID": "P026", "Product_Name": "Parle-G Gold Glucose Biscuits 1kg Family Pack", "Category": "Biscuits", "Brand": "Parle", "Supplier_ID": "S008", "Reorder_Level": 65, "Unit_Price_INR": 120.0, "Cost_Price_INR": 95.0, "Base_Stock": 260, "Restock_Qty": 220, "Velocity": 2.1},
        {"Product_ID": "P027", "Product_Name": "Britannia Good Day Cashew Cookies 600g", "Category": "Biscuits", "Brand": "Britannia", "Supplier_ID": "S008", "Reorder_Level": 50, "Unit_Price_INR": 150.0, "Cost_Price_INR": 115.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.7},
        {"Product_ID": "P028", "Product_Name": "Sunfeast Dark Fantasy Choco Fills 300g", "Category": "Biscuits", "Brand": "Sunfeast", "Supplier_ID": "S008", "Reorder_Level": 40, "Unit_Price_INR": 160.0, "Cost_Price_INR": 120.0, "Base_Stock": 150, "Restock_Qty": 120, "Velocity": 1.3},
        {"Product_ID": "P029", "Product_Name": "Haldiram Nagpur Aloo Bhujia 1kg", "Category": "Snacks", "Brand": "Haldiram", "Supplier_ID": "S009", "Reorder_Level": 50, "Unit_Price_INR": 240.0, "Cost_Price_INR": 180.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.6},
        {"Product_ID": "P030", "Product_Name": "Bikaji Bhujia Sev 1kg Festive Pack", "Category": "Snacks", "Brand": "Bikaji", "Supplier_ID": "S009", "Reorder_Level": 45, "Unit_Price_INR": 260.0, "Cost_Price_INR": 195.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.4},
        {"Product_ID": "P031", "Product_Name": "Lays India's Magic Masala Potato Chips 115g", "Category": "Snacks", "Brand": "Lays", "Supplier_ID": "S009", "Reorder_Level": 55, "Unit_Price_INR": 50.0, "Cost_Price_INR": 38.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.9},
        {"Product_ID": "P032", "Product_Name": "Kurkure Masala Munch Crunchy Snacks 115g", "Category": "Snacks", "Brand": "Kurkure", "Supplier_ID": "S009", "Reorder_Level": 55, "Unit_Price_INR": 50.0, "Cost_Price_INR": 38.0, "Base_Stock": 210, "Restock_Qty": 180, "Velocity": 1.8},

        # --- Spices, Sugar, Salt & Condiments ---
        {"Product_ID": "P033", "Product_Name": "Tata Salt Vacuum Evaporated Iodized 1kg", "Category": "Sugar & Salt", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 65, "Unit_Price_INR": 28.0, "Cost_Price_INR": 22.0, "Base_Stock": 280, "Restock_Qty": 240, "Velocity": 2.2},
        {"Product_ID": "P034", "Product_Name": "Madhur Pure & Hygienic Refined Sugar 5kg", "Category": "Sugar & Salt", "Brand": "Madhur", "Supplier_ID": "S002", "Reorder_Level": 50, "Unit_Price_INR": 250.0, "Cost_Price_INR": 205.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.7},
        {"Product_ID": "P035", "Product_Name": "Organic Tattva Jaggery Powder 1kg", "Category": "Sugar & Salt", "Brand": "Organic Tattva", "Supplier_ID": "S002", "Reorder_Level": 35, "Unit_Price_INR": 130.0, "Cost_Price_INR": 95.0, "Base_Stock": 140, "Restock_Qty": 110, "Velocity": 1.2},
        {"Product_ID": "P036", "Product_Name": "Everest Super Garam Masala 100g", "Category": "Spices", "Brand": "Everest", "Supplier_ID": "S003", "Reorder_Level": 45, "Unit_Price_INR": 92.0, "Cost_Price_INR": 70.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.5},
        {"Product_ID": "P037", "Product_Name": "MDH Deggi Mirch Powder 100g", "Category": "Spices", "Brand": "MDH", "Supplier_ID": "S003", "Reorder_Level": 45, "Unit_Price_INR": 88.0, "Cost_Price_INR": 66.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.5},
        {"Product_ID": "P038", "Product_Name": "Catch Turmeric Haldi Powder 200g", "Category": "Spices", "Brand": "Catch", "Supplier_ID": "S003", "Reorder_Level": 45, "Unit_Price_INR": 75.0, "Cost_Price_INR": 56.0, "Base_Stock": 170, "Restock_Qty": 140, "Velocity": 1.4},
        {"Product_ID": "P039", "Product_Name": "Kissan Fresh Tomato Ketchup Bottle 1kg", "Category": "Sauces", "Brand": "Kissan", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 160.0, "Cost_Price_INR": 122.0, "Base_Stock": 150, "Restock_Qty": 120, "Velocity": 1.3},

        # --- Personal Care & Hygiene ---
        {"Product_ID": "P040", "Product_Name": "Dettol Original Germ Protection Bathing Soap 125g (Pack of 4)", "Category": "Personal Care", "Brand": "Dettol", "Supplier_ID": "S010", "Reorder_Level": 45, "Unit_Price_INR": 230.0, "Cost_Price_INR": 175.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.5},
        {"Product_ID": "P041", "Product_Name": "Dove Deep Moisture Nourishing Body Wash 400ml", "Category": "Personal Care", "Brand": "Dove", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 340.0, "Cost_Price_INR": 260.0, "Base_Stock": 130, "Restock_Qty": 100, "Velocity": 1.1},
        {"Product_ID": "P042", "Product_Name": "Colgate MaxFresh Spicy Fresh Toothpaste 300g Saver Pack", "Category": "Personal Care", "Brand": "Colgate", "Supplier_ID": "S010", "Reorder_Level": 50, "Unit_Price_INR": 220.0, "Cost_Price_INR": 165.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.7},
        {"Product_ID": "P043", "Product_Name": "Vaseline Deep Moisture Body Lotion 400ml", "Category": "Personal Care", "Brand": "Vaseline", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 310.0, "Cost_Price_INR": 240.0, "Base_Stock": 130, "Restock_Qty": 100, "Velocity": 1.2},
        {"Product_ID": "P044", "Product_Name": "Head & Shoulders Anti-Dandruff Shampoo 340ml", "Category": "Personal Care", "Brand": "Head & Shoulders", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 380.0, "Cost_Price_INR": 295.0, "Base_Stock": 140, "Restock_Qty": 110, "Velocity": 1.2},

        # --- Home Care & Cleaning ---
        {"Product_ID": "P045", "Product_Name": "Surf Excel Easy Wash Detergent Powder 1kg", "Category": "Household Cleaning", "Brand": "Surf Excel", "Supplier_ID": "S010", "Reorder_Level": 50, "Unit_Price_INR": 155.0, "Cost_Price_INR": 122.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.7},
        {"Product_ID": "P046", "Product_Name": "Vim Lemon Dishwash Gel Bottle 750ml", "Category": "Household Cleaning", "Brand": "Vim", "Supplier_ID": "S010", "Reorder_Level": 45, "Unit_Price_INR": 180.0, "Cost_Price_INR": 138.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.5},
        {"Product_ID": "P047", "Product_Name": "Lizol Citrus Disinfectant Surface Cleaner 1L", "Category": "Household Cleaning", "Brand": "Lizol", "Supplier_ID": "S010", "Reorder_Level": 40, "Unit_Price_INR": 215.0, "Cost_Price_INR": 165.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.3},

        # --- Sweets, Dry Fruits & Special Festive ---
        {"Product_ID": "P048", "Product_Name": "Haldiram Kaju Katli Premium Box 500g", "Category": "Sweets", "Brand": "Haldiram", "Supplier_ID": "S009", "Reorder_Level": 35, "Unit_Price_INR": 480.0, "Cost_Price_INR": 380.0, "Base_Stock": 140, "Restock_Qty": 100, "Velocity": 1.3},
        {"Product_ID": "P049", "Product_Name": "Tata Sampann California Raw Almonds 500g", "Category": "Dry Fruits", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 35, "Unit_Price_INR": 520.0, "Cost_Price_INR": 410.0, "Base_Stock": 130, "Restock_Qty": 100, "Velocity": 1.2},
        {"Product_ID": "P050", "Product_Name": "Dabur Chyawanprash Special Immunity Booster 1kg", "Category": "Health & Wellness", "Brand": "Dabur", "Supplier_ID": "S003", "Reorder_Level": 35, "Unit_Price_INR": 395.0, "Cost_Price_INR": 310.0, "Base_Stock": 140, "Restock_Qty": 100, "Velocity": 1.2},
    ]

    # Initialize rolling inventory stock for each product
    inventory_tracker = {p["Product_ID"]: p["Base_Stock"] for p in catalog}

    start_date = date(2026, 7, 1)
    end_date = date(2026, 12, 31)
    total_days = (end_date - start_date).days + 1  # 184 days

    monthly_rows = {m: [] for m in range(1, 7)}
    all_rows = []

    tx_counter = 10001

    # Date progression loop
    for day_idx in range(total_days):
        current_date = start_date + timedelta(days=day_idx)
        month_num = current_date.month - 6  # 7=1, 8=2, 9=3, 10=4, 11=5, 12=6
        
        weekday = current_date.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
        is_weekend = weekday in [4, 5, 6]

        # Festive multiplier detection
        # Ganesh Chaturthi: Sept 13 - Sept 20
        # Navratri / Dussehra / Diwali: Oct 15 - Nov 6
        # Winter / Christmas / New Year: Dec 20 - Dec 31
        festive_mult = 1.0
        if current_date.month == 9 and 13 <= current_date.day <= 20:
            festive_mult = 1.35
        elif current_date.month == 10 and current_date.day >= 15:
            festive_mult = 1.55
        elif current_date.month == 11 and current_date.day <= 6:
            festive_mult = 1.50
        elif current_date.month == 12 and current_date.day >= 20:
            festive_mult = 1.45

        # Target 34-38 transactions per day on average
        base_tx_count = random.randint(30, 34)
        if is_weekend:
            base_tx_count += random.randint(6, 12)
        if festive_mult > 1.0:
            base_tx_count += random.randint(4, 10)

        # Shuffle catalog and select products for the day so all 50 SKUs get sampled uniformly over the week
        daily_sample_pids = random.sample(catalog, min(len(catalog), base_tx_count))

        for prod in daily_sample_pids:
            pid = prod["Product_ID"]
            pname = prod["Product_Name"]
            cat = prod["Category"]
            brand = prod["Brand"]
            supp = prod["Supplier_ID"]
            reorder_lvl = prod["Reorder_Level"]
            mrp = prod["Unit_Price_INR"]
            cost_price = prod["Cost_Price_INR"]
            velocity = prod["Velocity"]

            # Units sold simulation based on product velocity, weekend lift, and festival factor
            units_sold = int(round(random.uniform(1.0, 4.0) * velocity * (1.25 if is_weekend else 1.0) * (1.3 if festive_mult > 1.0 else 1.0)))
            units_sold = max(1, min(24, units_sold))

            # Special subtle anomaly injections (5-8 throughout 6 months to showcase anomaly system)
            is_anomaly = False
            if day_idx == 45 and pid == "P001": # Aug 15 bulk festival purchase
                units_sold = 38
                is_anomaly = True
            elif day_idx == 110 and pid == "P048": # Oct 19 Diwali massive sweets purchase
                units_sold = 42
                is_anomaly = True
            elif day_idx == 160 and pid == "P010": # Dec 8 Cow Ghee marriage bulk order
                units_sold = 32
                is_anomaly = True

            # Dynamic price elasticity simulation:
            # On weekends or festivals, slight premium (+2% to +6%) or strategic promotional discount (-3% to -8%)
            discount_pct = 0.0
            if is_weekend:
                if random.random() < 0.35:
                    discount_pct = random.choice([3.0, 5.0, 8.0]) # promotional weekend discount
                elif random.random() < 0.40:
                    discount_pct = random.choice([-2.0, -4.0, -5.0]) # weekend peak demand dynamic price lift
            elif festive_mult > 1.0 and random.random() < 0.45:
                discount_pct = random.choice([5.0, 7.5, 10.0])

            selling_price = round(mrp * (1.0 - (discount_pct / 100.0)), 2)
            # Ensure price never falls below cost
            if selling_price < cost_price * 1.05:
                selling_price = round(cost_price * 1.08, 2)

            discount_inr = round(max(0.0, mrp - selling_price), 2)
            total_rev = round(units_sold * selling_price, 2)
            total_cost = round(units_sold * cost_price, 2)
            gross_profit = round(total_rev - total_cost, 2)
            margin_pct = round((gross_profit / total_rev) * 100.0, 2) if total_rev > 0 else 0.0

            # Inventory restocking simulation
            curr_stock = inventory_tracker[pid] - units_sold
            if curr_stock <= reorder_lvl:
                # Restock triggered!
                curr_stock += prod["Restock_Qty"]
            
            # For 2 demo SKUs in late December, simulate low stock to showcase stockout alerts
            if month_num == 6 and current_date.day >= 25 and pid in ["P014", "P041"]:
                curr_stock = random.randint(8, 16) # Below reorder level!

            inventory_tracker[pid] = max(5, curr_stock)

            row = {
                "Transaction_ID": f"TXN{tx_counter}",
                "Date": current_date.strftime("%Y-%m-%d"),
                "Product_ID": pid,
                "Product_Name": pname,
                "Category": cat,
                "Brand": brand,
                "Supplier_ID": supp,
                "Unit_Price_INR": f"{mrp:.2f}",
                "Cost_Price_INR": f"{cost_price:.2f}",
                "Selling_Price_INR": f"{selling_price:.2f}",
                "Units_Sold": units_sold,
                "Discount_INR": f"{discount_inr:.2f}",
                "Total_Revenue_INR": f"{total_rev:.2f}",
                "Total_Cost_INR": f"{total_cost:.2f}",
                "Gross_Profit_INR": f"{gross_profit:.2f}",
                "Profit_Margin_Pct": f"{margin_pct:.2f}",
                "Stock_Level": inventory_tracker[pid],
                "Reorder_Level": reorder_lvl,
            }

            all_rows.append(row)
            monthly_rows[month_num].append(row)
            tx_counter += 1

    # Write files to docs/ directory
    headers = [
        "Transaction_ID", "Date", "Product_ID", "Product_Name", "Category", "Brand",
        "Supplier_ID", "Unit_Price_INR", "Cost_Price_INR", "Selling_Price_INR",
        "Units_Sold", "Discount_INR", "Total_Revenue_INR", "Total_Cost_INR",
        "Gross_Profit_INR", "Profit_Margin_Pct", "Stock_Level", "Reorder_Level"
    ]

    month_names = {
        1: ("kirana_store_month1_july_2026.csv", "July 2026"),
        2: ("kirana_store_month2_august_2026.csv", "August 2026"),
        3: ("kirana_store_month3_september_2026.csv", "September 2026"),
        4: ("kirana_store_month4_october_2026.csv", "October 2026"),
        5: ("kirana_store_month5_november_2026.csv", "November 2026"),
        6: ("kirana_store_month6_december_2026.csv", "December 2026"),
    }

    print("--- 6-MONTH DATASET GENERATION SUMMARY ---")
    for m_num, (fname, label) in month_names.items():
        fpath = os.path.join(docs_dir, fname)
        rows_m = monthly_rows[m_num]
        with open(fpath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows_m)
        
        unique_skus = len(set(r["Product_ID"] for r in rows_m))
        total_units = sum(r["Units_Sold"] for r in rows_m)
        total_rev = sum(float(r["Total_Revenue_INR"]) for r in rows_m)
        print(f"{label} ({fname}): {len(rows_m):,} rows | {unique_skus} SKUs | {total_units:,} units | INR {total_rev:,.2f}")

    # Write the complete 6-month combined master dataset
    master_fname = "kirana_store_6months_demo_dataset.csv"
    master_fpath = os.path.join(docs_dir, master_fname)
    with open(master_fpath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_rows)

    total_skus = len(set(r["Product_ID"] for r in all_rows))
    total_units_all = sum(r["Units_Sold"] for r in all_rows)
    total_rev_all = sum(float(r["Total_Revenue_INR"]) for r in all_rows)
    sku_counts = {}
    for r in all_rows:
        sku_counts[r["Product_ID"]] = sku_counts.get(r["Product_ID"], 0) + 1
    min_sku_count = min(sku_counts.values())
    max_sku_count = max(sku_counts.values())

    print("\n--- MASTER 6-MONTH DATASET ---")
    print(f"File: {master_fname}")
    print(f"Total Rows: {len(all_rows):,}")
    print(f"Active SKUs: {total_skus} (100% catalog coverage)")
    print(f"Min transactions per SKU: {min_sku_count} | Max: {max_sku_count}")
    print(f"Total Units Sold: {total_units_all:,}")
    print(f"Total Revenue: INR {total_rev_all:,.2f}")

if __name__ == "__main__":
    generate_rich_6month_kirana_dataset()
