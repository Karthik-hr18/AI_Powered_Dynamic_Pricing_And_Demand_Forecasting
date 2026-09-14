import csv
import random
from datetime import date, datetime, timedelta
import os

def generate_kirana_store_extended_datasets():
    source_file = "c:/Users/karth/Projects/AI Powered/docs/Kirana_Store_10000_Rows.csv"
    
    # 1. Extract base product catalog from reference Kirana store file
    base_catalog = {}
    with open(source_file, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row["Product_ID"]
            if pid not in base_catalog:
                base_catalog[pid] = {
                    "Product_ID": pid,
                    "Product_Name": row["Product_Name"],
                    "Category": row["Category"],
                    "Brand": row["Brand"],
                    "Supplier_ID": row["Supplier_ID"],
                    "Reorder_Level": int(row["Reorder_Level"]) if row["Reorder_Level"].isdigit() else 50,
                    "Unit_Price_INR": float(row["Unit_Price_INR"]),
                    "Cost_Price_INR": float(row["Cost_Price_INR"]),
                    "Profit_Margin": float(row["Profit_Margin"]),
                    "Launch_Month": 1,
                }

    print(f"Extracted {len(base_catalog)} base SKUs from Kirana_Store_10000_Rows.csv")

    # 2. Define realistic new products to introduce across months 4, 5, and 6
    new_products_october = [
        {"Product_ID": "P0501", "Product_Name": "Haldiram Kaju Katli 500g", "Category": "Sweets", "Brand": "Haldiram", "Supplier_ID": "S015", "Reorder_Level": 35, "Unit_Price_INR": 480.0, "Cost_Price_INR": 380.0, "Profit_Margin": 20.83, "Launch_Month": 4},
        {"Product_ID": "P0502", "Product_Name": "Tata Sampann California Almonds 500g", "Category": "Dry Fruits", "Brand": "Tata", "Supplier_ID": "S014", "Reorder_Level": 40, "Unit_Price_INR": 520.0, "Cost_Price_INR": 410.0, "Profit_Margin": 21.15, "Launch_Month": 4},
        {"Product_ID": "P0503", "Product_Name": "Haldiram Soan Papdi 500g", "Category": "Sweets", "Brand": "Haldiram", "Supplier_ID": "S015", "Reorder_Level": 50, "Unit_Price_INR": 160.0, "Cost_Price_INR": 120.0, "Profit_Margin": 25.0, "Launch_Month": 4},
        {"Product_ID": "P0504", "Product_Name": "Amul Pure Cow Desi Ghee 1L", "Category": "Oil & Ghee", "Brand": "Amul", "Supplier_ID": "S006", "Reorder_Level": 60, "Unit_Price_INR": 610.0, "Cost_Price_INR": 510.0, "Profit_Margin": 16.39, "Launch_Month": 4},
        {"Product_ID": "P0505", "Product_Name": "MTR Gulab Jamun Instant Mix 500g", "Category": "Instant Food", "Brand": "MTR", "Supplier_ID": "S029", "Reorder_Level": 45, "Unit_Price_INR": 145.0, "Cost_Price_INR": 110.0, "Profit_Margin": 24.14, "Launch_Month": 4},
        {"Product_ID": "P0506", "Product_Name": "Patanjali Kesar 1g", "Category": "Spices", "Brand": "Patanjali", "Supplier_ID": "S017", "Reorder_Level": 20, "Unit_Price_INR": 290.0, "Cost_Price_INR": 220.0, "Profit_Margin": 24.14, "Launch_Month": 4},
        {"Product_ID": "P0507", "Product_Name": "Cadbury Celebrations Premium Gift Box", "Category": "Chocolates", "Brand": "Cadbury", "Supplier_ID": "S007", "Reorder_Level": 50, "Unit_Price_INR": 350.0, "Cost_Price_INR": 270.0, "Profit_Margin": 22.86, "Launch_Month": 4},
        {"Product_ID": "P0508", "Product_Name": "Fortune Special Biryani Basmati Rice 5kg", "Category": "Rice", "Brand": "Fortune", "Supplier_ID": "S025", "Reorder_Level": 40, "Unit_Price_INR": 580.0, "Cost_Price_INR": 470.0, "Profit_Margin": 18.97, "Launch_Month": 4},
        {"Product_ID": "P0509", "Product_Name": "Bikaji Bhujia Sev 1kg Festive Pack", "Category": "Snacks", "Brand": "Bikaji", "Supplier_ID": "S020", "Reorder_Level": 55, "Unit_Price_INR": 260.0, "Cost_Price_INR": 195.0, "Profit_Margin": 25.0, "Launch_Month": 4},
        {"Product_ID": "P0510", "Product_Name": "Tata Sampann Organic Poha 500g", "Category": "Flours", "Brand": "Tata", "Supplier_ID": "S013", "Reorder_Level": 50, "Unit_Price_INR": 65.0, "Cost_Price_INR": 48.0, "Profit_Margin": 26.15, "Launch_Month": 4},
    ]

    new_products_november = [
        {"Product_ID": "P0511", "Product_Name": "Dabur Chyawanprash Special 1kg", "Category": "Health & Wellness", "Brand": "Dabur", "Supplier_ID": "S018", "Reorder_Level": 40, "Unit_Price_INR": 395.0, "Cost_Price_INR": 310.0, "Profit_Margin": 21.52, "Launch_Month": 5},
        {"Product_ID": "P0512", "Product_Name": "Tata Tea Gold Royal 500g", "Category": "Beverages", "Brand": "Tata", "Supplier_ID": "S030", "Reorder_Level": 60, "Unit_Price_INR": 310.0, "Cost_Price_INR": 245.0, "Profit_Margin": 20.97, "Launch_Month": 5},
        {"Product_ID": "P0513", "Product_Name": "Nivea Nourishing Body Cold Cream 200ml", "Category": "Personal Care", "Brand": "Nivea", "Supplier_ID": "S011", "Reorder_Level": 35, "Unit_Price_INR": 240.0, "Cost_Price_INR": 180.0, "Profit_Margin": 25.0, "Launch_Month": 5},
        {"Product_ID": "P0514", "Product_Name": "Saffola Masala Oats Classic 500g", "Category": "Instant Food", "Brand": "Saffola", "Supplier_ID": "S029", "Reorder_Level": 45, "Unit_Price_INR": 175.0, "Cost_Price_INR": 135.0, "Profit_Margin": 22.86, "Launch_Month": 5},
        {"Product_ID": "P0515", "Product_Name": "Patanjali Pure Wild Forest Honey 1kg", "Category": "Sugar & Salt", "Brand": "Patanjali", "Supplier_ID": "S008", "Reorder_Level": 50, "Unit_Price_INR": 420.0, "Cost_Price_INR": 330.0, "Profit_Margin": 21.43, "Launch_Month": 5},
        {"Product_ID": "P0516", "Product_Name": "Wagh Bakri Premium Masala Tea 500g", "Category": "Beverages", "Brand": "Wagh Bakri", "Supplier_ID": "S030", "Reorder_Level": 40, "Unit_Price_INR": 275.0, "Cost_Price_INR": 215.0, "Profit_Margin": 21.82, "Launch_Month": 5},
        {"Product_ID": "P0517", "Product_Name": "Organic Tattva Jaggery Powder 1kg", "Category": "Sugar & Salt", "Brand": "Organic Tattva", "Supplier_ID": "S015", "Reorder_Level": 50, "Unit_Price_INR": 130.0, "Cost_Price_INR": 95.0, "Profit_Margin": 26.92, "Launch_Month": 5},
        {"Product_ID": "P0518", "Product_Name": "Aashirvaad Organic Chana Dal 1kg", "Category": "Pulses", "Brand": "Aashirvaad", "Supplier_ID": "S020", "Reorder_Level": 55, "Unit_Price_INR": 145.0, "Cost_Price_INR": 115.0, "Profit_Margin": 20.69, "Launch_Month": 5},
        {"Product_ID": "P0519", "Product_Name": "Kissan Mixed Fruit Jam 1kg", "Category": "Spreads", "Brand": "Kissan", "Supplier_ID": "S029", "Reorder_Level": 40, "Unit_Price_INR": 280.0, "Cost_Price_INR": 220.0, "Profit_Margin": 21.43, "Launch_Month": 5},
        {"Product_ID": "P0520", "Product_Name": "Vaseline Deep Moisture Body Lotion 400ml", "Category": "Personal Care", "Brand": "Vaseline", "Supplier_ID": "S011", "Reorder_Level": 35, "Unit_Price_INR": 310.0, "Cost_Price_INR": 240.0, "Profit_Margin": 22.58, "Launch_Month": 5},
    ]

    new_products_december = [
        {"Product_ID": "P0521", "Product_Name": "Britannia Rich Plum Cake 400g", "Category": "Bakery & Cakes", "Brand": "Britannia", "Supplier_ID": "S007", "Reorder_Level": 50, "Unit_Price_INR": 190.0, "Cost_Price_INR": 140.0, "Profit_Margin": 26.32, "Launch_Month": 6},
        {"Product_ID": "P0522", "Product_Name": "Nestle Milkmaid Sweetened Condensed Milk 400g", "Category": "Dairy", "Brand": "Nestle", "Supplier_ID": "S019", "Reorder_Level": 45, "Unit_Price_INR": 145.0, "Cost_Price_INR": 115.0, "Profit_Margin": 20.69, "Launch_Month": 6},
        {"Product_ID": "P0523", "Product_Name": "Hershey Chocolate Syrup 623g", "Category": "Spreads", "Brand": "Hershey", "Supplier_ID": "S029", "Reorder_Level": 35, "Unit_Price_INR": 220.0, "Cost_Price_INR": 170.0, "Profit_Margin": 22.73, "Launch_Month": 6},
        {"Product_ID": "P0524", "Product_Name": "Cadbury Bournville Rich Dark Chocolate 80g", "Category": "Chocolates", "Brand": "Cadbury", "Supplier_ID": "S007", "Reorder_Level": 40, "Unit_Price_INR": 110.0, "Cost_Price_INR": 82.0, "Profit_Margin": 25.45, "Launch_Month": 6},
        {"Product_ID": "P0525", "Product_Name": "Tropicana 100% Festive Orange Juice 1L", "Category": "Beverages", "Brand": "Tropicana", "Supplier_ID": "S030", "Reorder_Level": 50, "Unit_Price_INR": 135.0, "Cost_Price_INR": 105.0, "Profit_Margin": 22.22, "Launch_Month": 6},
        {"Product_ID": "P0526", "Product_Name": "Borges Extra Virgin Olive Oil 1L", "Category": "Oil & Ghee", "Brand": "Borges", "Supplier_ID": "S006", "Reorder_Level": 30, "Unit_Price_INR": 980.0, "Cost_Price_INR": 790.0, "Profit_Margin": 19.39, "Launch_Month": 6},
        {"Product_ID": "P0527", "Product_Name": "Pringles Sour Cream & Onion 107g", "Category": "Snacks", "Brand": "Pringles", "Supplier_ID": "S016", "Reorder_Level": 45, "Unit_Price_INR": 115.0, "Cost_Price_INR": 88.0, "Profit_Margin": 23.48, "Launch_Month": 6},
        {"Product_ID": "P0528", "Product_Name": "Amul Dark Chocolate Truffles Box 250g", "Category": "Chocolates", "Brand": "Amul", "Supplier_ID": "S019", "Reorder_Level": 40, "Unit_Price_INR": 240.0, "Cost_Price_INR": 185.0, "Profit_Margin": 22.92, "Launch_Month": 6},
        {"Product_ID": "P0529", "Product_Name": "Tata Sampann Unpolished Toor Dal 1kg", "Category": "Pulses", "Brand": "Tata", "Supplier_ID": "S009", "Reorder_Level": 60, "Unit_Price_INR": 175.0, "Cost_Price_INR": 140.0, "Profit_Margin": 20.0, "Launch_Month": 6},
        {"Product_ID": "P0530", "Product_Name": "Real Activ Mixed Fruit Juice 1L", "Category": "Beverages", "Brand": "Real", "Supplier_ID": "S030", "Reorder_Level": 50, "Unit_Price_INR": 130.0, "Cost_Price_INR": 100.0, "Profit_Margin": 23.08, "Launch_Month": 6},
    ]

    all_catalog = dict(base_catalog)
    for p in new_products_october:
        all_catalog[p["Product_ID"]] = p
    for p in new_products_november:
        all_catalog[p["Product_ID"]] = p
    for p in new_products_december:
        all_catalog[p["Product_ID"]] = p

    print(f"Total catalog expanded to {len(all_catalog)} unique SKUs.")

    fieldnames = [
        "Order_ID", "Order_Date", "Product_ID", "Product_Name", "Category",
        "Brand", "Quantity_Sold", "Unit_Price_INR", "Cost_Price_INR",
        "Discount_Percent", "Inventory_Available", "Demand_Level",
        "Festival_Flag", "Weekend_Flag", "Season", "Weather",
        "Supplier_ID", "Reorder_Level", "Profit_Margin", "Total_Sales_INR"
    ]

    weather_options = ["Sunny", "Rainy", "Cloudy"]
    discount_choices = [0, 5, 10, 15, 20]

    # Global rolling state
    inventory = {pid: random.randint(150, 600) for pid in all_catalog}

    def generate_month_records(month_num, start_d, end_d, target_rows, start_order_num, seed_val):
        random.seed(seed_val)
        rows = []
        cur = start_d
        order_num = start_order_num
        days = (end_d - start_d).days + 1

        # Available products for this month
        active_products = [p for p in all_catalog.values() if int(p["Launch_Month"]) <= month_num]
        weights = []
        for p in active_products:
            # Give slight weight bonus to festive/staple items
            if p["Category"] in ("Oil & Ghee", "Flours", "Pulses", "Sweets", "Dry Fruits", "Chocolates"):
                weights.append(1.4)
            else:
                weights.append(1.0)

        # Distribute target_rows across the days
        base_per_day = target_rows // days
        extra_rows = target_rows % days

        for day_idx in range(days):
            weekend_flag = 1 if cur.weekday() in (5, 6) else 0
            
            # Festivals calendar for Sep-Dec 2026
            festival_flag = 0
            if month_num == 3: # September: Ganesh Chaturthi (14-16 Sep), Navratri start (21-22 Sep)
                if cur.day in (14, 15, 16, 21, 22):
                    festival_flag = 1
                season = "Monsoon"
            elif month_num == 4: # October: Dussehra (20 Oct), Karwa Chauth (28 Oct), Diwali prep (29-31 Oct)
                if cur.day in (19, 20, 21, 28, 29, 30, 31):
                    festival_flag = 1
                season = "Autumn"
            elif month_num == 5: # November: Diwali / Govardhan / Bhai Dooj (1-4 Nov), Wedding season
                if cur.day in (1, 2, 3, 4, 14, 15, 22, 23):
                    festival_flag = 1
                season = "Winter"
            elif month_num == 6: # December: Christmas & New Year Holiday rush (22-31 Dec)
                if cur.day in (22, 23, 24, 25, 26, 29, 30, 31):
                    festival_flag = 1
                season = "Winter"
            else:
                season = "Summer"

            weather = random.choice(weather_options)

            # Daily transactions target with weekend & festival surges
            daily_count = base_per_day
            if festival_flag:
                daily_count += random.randint(12, 22)
            elif weekend_flag:
                daily_count += random.randint(6, 14)
            else:
                daily_count -= random.randint(2, 6)

            if day_idx < extra_rows:
                daily_count += 1

            for _ in range(max(15, daily_count)):
                order_num += 1
                prod = random.choices(active_products, weights=weights, k=1)[0]
                pid = str(prod["Product_ID"])
                base_u_price = float(prod["Unit_Price_INR"])
                base_c_price = float(prod["Cost_Price_INR"])
                reorder_lvl = int(prod["Reorder_Level"])

                # Realistic quantity distribution
                if festival_flag:
                    qty = random.randint(5, 20)
                    demand = "Spike" if qty > 14 else "High"
                elif weekend_flag:
                    qty = random.randint(3, 10)
                    demand = "High" if qty > 6 else "Normal"
                else:
                    qty = random.randint(1, 5)
                    demand = "Low" if qty == 1 else "Normal"

                # Price variation (±3%)
                unit_price = round(base_u_price * random.uniform(0.97, 1.03), 2)
                cost_price = round(base_c_price * random.uniform(0.98, 1.02), 2)
                
                # Promotional discounts on festive days or weekends
                if festival_flag:
                    discount_pct = random.choice([5, 10, 15, 20])
                elif weekend_flag and random.random() < 0.40:
                    discount_pct = random.choice([5, 10])
                elif random.random() < 0.20:
                    discount_pct = 5
                else:
                    discount_pct = 0

                # Total sales calculation with discount
                discount_factor = (100 - discount_pct) / 100.0
                total_sales = round(qty * unit_price * discount_factor, 2)

                # Profit margin
                if unit_price > 0:
                    profit_margin = round(((unit_price - cost_price) / unit_price) * 100, 2)
                else:
                    profit_margin = float(prod["Profit_Margin"])

                # Inventory update & restocking
                inventory[pid] = max(10, inventory.get(pid, 200) - qty)
                if inventory[pid] < reorder_lvl:
                    inventory[pid] += random.randint(150, 350)

                rows.append({
                    "Order_ID": f"ORD{order_num:06d}",
                    "Order_Date": cur.strftime("%Y-%m-%d"),
                    "Product_ID": prod["Product_ID"],
                    "Product_Name": prod["Product_Name"],
                    "Category": prod["Category"],
                    "Brand": prod["Brand"],
                    "Quantity_Sold": qty,
                    "Unit_Price_INR": unit_price,
                    "Cost_Price_INR": cost_price,
                    "Discount_Percent": discount_pct,
                    "Inventory_Available": inventory[pid],
                    "Demand_Level": demand,
                    "Festival_Flag": festival_flag,
                    "Weekend_Flag": weekend_flag,
                    "Season": season,
                    "Weather": weather,
                    "Supplier_ID": prod["Supplier_ID"],
                    "Reorder_Level": prod["Reorder_Level"],
                    "Profit_Margin": profit_margin,
                    "Total_Sales_INR": total_sales
                })

            cur += timedelta(days=1)

        return rows, order_num

    # Target rows scaling across 4 months to total exactly ~10,000 rows:
    # Month 3 (September): ~2,000 rows
    # Month 4 (October):   ~2,400 rows
    # Month 5 (November):  ~2,700 rows
    # Month 6 (December):  ~2,900 rows
    # Total = 10,000 rows!
    
    current_order = 20000

    # 1. Month 3 (September 2026)
    m3_rows, current_order = generate_month_records(
        month_num=3,
        start_d=date(2026, 9, 1),
        end_d=date(2026, 9, 30),
        target_rows=2000,
        start_order_num=current_order,
        seed_val=301
    )
    m3_file = "c:/Users/karth/Projects/AI Powered/docs/kirana_store_month3_september_2026.csv"
    with open(m3_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(m3_rows)
    print(f"Generated Month 3: {len(m3_rows)} rows -> {m3_file}")

    # 2. Month 4 (October 2026) - Launches 10 new Festive & Sweet SKUs
    m4_rows, current_order = generate_month_records(
        month_num=4,
        start_d=date(2026, 10, 1),
        end_d=date(2026, 10, 31),
        target_rows=2400,
        start_order_num=current_order,
        seed_val=402
    )
    m4_file = "c:/Users/karth/Projects/AI Powered/docs/kirana_store_month4_october_2026.csv"
    with open(m4_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(m4_rows)
    print(f"Generated Month 4: {len(m4_rows)} rows -> {m4_file}")

    # 3. Month 5 (November 2026) - Launches 10 new Winter & Wellness SKUs
    m5_rows, current_order = generate_month_records(
        month_num=5,
        start_d=date(2026, 11, 1),
        end_d=date(2026, 11, 30),
        target_rows=2700,
        start_order_num=current_order,
        seed_val=503
    )
    m5_file = "c:/Users/karth/Projects/AI Powered/docs/kirana_store_month5_november_2026.csv"
    with open(m5_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(m5_rows)
    print(f"Generated Month 5: {len(m5_rows)} rows -> {m5_file}")

    # 4. Month 6 (December 2026) - Launches 10 new Bakery & Holiday SKUs
    m6_rows, current_order = generate_month_records(
        month_num=6,
        start_d=date(2026, 12, 1),
        end_d=date(2026, 12, 31),
        target_rows=2900,
        start_order_num=current_order,
        seed_val=604
    )
    m6_file = "c:/Users/karth/Projects/AI Powered/docs/kirana_store_month6_december_2026.csv"
    with open(m6_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(m6_rows)
    print(f"Generated Month 6: {len(m6_rows)} rows -> {m6_file}")

    # 5. Combined 4-Month 10,000 Rows Dataset
    combined_rows = m3_rows + m4_rows + m5_rows + m6_rows
    # Adjust to exactly 10,000 rows if slight variance from festival loops
    if len(combined_rows) > 10000:
        combined_rows = combined_rows[:10000]
    elif len(combined_rows) < 10000:
        # duplicate last realistic row with incremented order
        diff = 10000 - len(combined_rows)
        for i in range(diff):
            r = dict(combined_rows[-1])
            r["Order_ID"] = f"ORD{current_order + i + 1:06d}"
            combined_rows.append(r)

    combined_file = "c:/Users/karth/Projects/AI Powered/docs/kirana_store_4months_10000_rows.csv"
    with open(combined_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)
    print(f"Generated Master 4-Month Dataset: {len(combined_rows)} rows -> {combined_file}")

    print("\nSummary of Generated Datasets:")
    print(f"1. Month 3 (September 2026): {len(m3_rows)} rows -> {m3_file}")
    print(f"2. Month 4 (October 2026):   {len(m4_rows)} rows -> {m4_file}")
    print(f"3. Month 5 (November 2026):  {len(m5_rows)} rows -> {m5_file}")
    print(f"4. Month 6 (December 2026):  {len(m6_rows)} rows -> {m6_file}")
    print(f"5. Combined (4 Months Sep-Dec): {len(combined_rows)} rows -> {combined_file}")

if __name__ == "__main__":
    generate_kirana_store_extended_datasets()
