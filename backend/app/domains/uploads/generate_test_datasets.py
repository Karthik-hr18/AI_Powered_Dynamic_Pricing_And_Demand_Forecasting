import csv
import random
from datetime import date, datetime, timedelta

def generate_store_monthly_datasets():
    store_id = "S1001"
    store_name = "SuperMart Express - Bengaluru"
    city = "Bengaluru"
    state = "Karnataka"

    products = [
        {"id": "P1001", "name": "Royal Basmati Rice 5kg", "cat": "Staples", "subcat": "Rice & Grains", "base_price": 480.0, "cost": 380.0},
        {"id": "P1002", "name": "Fortune Sun Lite Oil 1L", "cat": "Staples", "subcat": "Edible Oils", "base_price": 165.0, "cost": 135.0},
        {"id": "P1003", "name": "Tata Tea Premium 500g", "cat": "Beverages", "subcat": "Tea & Coffee", "base_price": 270.0, "cost": 210.0},
        {"id": "P1004", "name": "Aashirvaad Shudh Chakki Atta 10kg", "cat": "Staples", "subcat": "Flours", "base_price": 440.0, "cost": 360.0},
        {"id": "P1005", "name": "Cadbury Dairy Milk Silk 150g", "cat": "Snacks", "subcat": "Chocolates", "base_price": 180.0, "cost": 140.0},
        {"id": "P1006", "name": "Lay's Classic Salted 90g", "cat": "Snacks", "subcat": "Chips & Crisps", "base_price": 40.0, "cost": 30.0},
        {"id": "P1007", "name": "Dettol Liquid Handwash 750ml", "cat": "Personal Care", "subcat": "Hygiene", "base_price": 145.0, "cost": 105.0},
        {"id": "P1008", "name": "Colgate Total Toothpaste 200g", "cat": "Personal Care", "subcat": "Oral Care", "base_price": 195.0, "cost": 145.0},
        {"id": "P1009", "name": "Surf Excel Matic Front Load 2kg", "cat": "Household", "subcat": "Detergents", "base_price": 460.0, "cost": 370.0},
        {"id": "P1010", "name": "Haldiram's Bhujia Sev 400g", "cat": "Snacks", "subcat": "Namkeen", "base_price": 120.0, "cost": 90.0},
        {"id": "P1011", "name": "Nescafe Classic Coffee 100g", "cat": "Beverages", "subcat": "Tea & Coffee", "base_price": 320.0, "cost": 250.0},
        {"id": "P1012", "name": "Dove Moisturizing Soap 125g (Pack of 3)", "cat": "Personal Care", "subcat": "Bath & Body", "base_price": 210.0, "cost": 160.0},
    ]

    payment_modes = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
    channels = ["In-Store", "In-Store", "Online", "Online", "Phone Order"]
    cust_types = ["Retail", "Retail", "Retail", "Wholesale", "Online"]
    promotions = ["None", "None", "Seasonal Discount", "BOGO", "Clearance Sale", "Festive Offer"]

    def generate_month_csv(start_d, end_d, filename, order_start_idx, promo_boost=False):
        fieldnames = [
            "Order_ID", "Order_Date", "Store_ID", "Store_Name", "Customer_ID",
            "Customer_Type", "City", "State", "Product_ID", "Product_Name",
            "Category", "Sub_Category", "Quantity_Sold", "Unit_Price_INR",
            "Discount_Percent", "Total_Sales_INR", "Cost_Price_INR", "Profit_INR",
            "Payment_Mode", "Sales_Channel", "Promotion_Type", "Festival_Season",
            "Stock_Availability", "Delivery_Status", "Return_Status",
            "Demand_Level", "Weather_Impact", "Anomaly_Flag"
        ]

        curr_order_id = order_start_idx
        rows = []
        cur = start_d
        random.seed(42 if not promo_boost else 99)

        while cur <= end_d:
            is_weekend = cur.weekday() in (5, 6)
            is_month_start = cur.day in (1, 2, 3, 4, 5)
            
            # Each product gets 1-4 sales per day
            for prod in products:
                daily_trans_count = random.randint(1, 3)
                if is_weekend:
                    daily_trans_count += random.randint(1, 2)
                
                for _ in range(daily_trans_count):
                    curr_order_id += 1
                    order_id = f"ORD{curr_order_id:06d}"
                    customer_id = f"C{random.randint(10000, 35000)}"
                    customer_type = random.choice(cust_types)
                    
                    # Quantity logic with weekend & payday boosts
                    base_qty = random.randint(1, 4)
                    if customer_type == "Wholesale":
                        base_qty = random.randint(8, 20)
                    elif is_weekend or is_month_start:
                        base_qty += random.randint(1, 3)
                    
                    if promo_boost:
                        base_qty = max(1, int(base_qty * 1.25))

                    qty = base_qty

                    # Price & Discount logic
                    price_var = random.uniform(0.95, 1.05)
                    unit_price = round(prod["base_price"] * price_var, 2)
                    
                    discount_pct = 0.0
                    promo = "None"
                    if promo_boost or random.random() < 0.25:
                        promo = random.choice(["Seasonal Discount", "Festive Offer", "BOGO", "Clearance Sale"])
                        discount_pct = round(random.uniform(5.0, 20.0), 2)
                    
                    total_sales = round(qty * unit_price * (1.0 - (discount_pct / 100.0)), 2)
                    cost_price = round(prod["cost"] * qty, 2)
                    profit = round(total_sales - cost_price, 2)

                    pay_mode = random.choice(payment_modes)
                    channel = random.choice(channels)
                    festival = "Varalakshmi / Independence Sale" if (promo_boost and cur.month == 8 and cur.day in range(12, 18)) else "None"
                    
                    stock = "In Stock" if random.random() > 0.06 else "Low Stock"
                    del_status = "Delivered" if channel == "Online" else "Delivered"
                    return_status = "No" if random.random() > 0.03 else "Yes"
                    
                    demand = "High" if is_weekend else ("Very High" if is_month_start else "Medium")
                    weather = "Heavy Rain" if random.random() < 0.2 else "Pleasant"
                    anomaly = "No"

                    rows.append({
                        "Order_ID": order_id,
                        "Order_Date": cur.strftime("%Y-%m-%d"),
                        "Store_ID": store_id,
                        "Store_Name": store_name,
                        "Customer_ID": customer_id,
                        "Customer_Type": customer_type,
                        "City": city,
                        "State": state,
                        "Product_ID": prod["id"],
                        "Product_Name": prod["name"],
                        "Category": prod["cat"],
                        "Sub_Category": prod["subcat"],
                        "Quantity_Sold": qty,
                        "Unit_Price_INR": unit_price,
                        "Discount_Percent": discount_pct,
                        "Total_Sales_INR": total_sales,
                        "Cost_Price_INR": cost_price,
                        "Profit_INR": profit,
                        "Payment_Mode": pay_mode,
                        "Sales_Channel": channel,
                        "Promotion_Type": promo,
                        "Festival_Season": festival,
                        "Stock_Availability": stock,
                        "Delivery_Status": del_status,
                        "Return_Status": return_status,
                        "Demand_Level": demand,
                        "Weather_Impact": weather,
                        "Anomaly_Flag": anomaly
                    })

            cur += timedelta(days=1)

        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Generated {len(rows)} records in {filename}")
        return curr_order_id, len(rows)

    # 1. Month 1: July 2026 (July 1 to July 31)
    d1_start = date(2026, 7, 1)
    d1_end = date(2026, 7, 31)
    next_id, count1 = generate_month_csv(
        d1_start, d1_end, "c:/Users/karth/Projects/AI Powered/docs/store_sales_month1_july_2026.csv", 200000, promo_boost=False
    )

    # 2. Month 2: August 2026 (August 1 to August 31)
    d2_start = date(2026, 8, 1)
    d2_end = date(2026, 8, 31)
    _, count2 = generate_month_csv(
        d2_start, d2_end, "c:/Users/karth/Projects/AI Powered/docs/store_sales_month2_august_2026.csv", next_id, promo_boost=True
    )

    print(f"Summary: Month 1 = {count1} transactions, Month 2 = {count2} transactions.")

if __name__ == "__main__":
    generate_store_monthly_datasets()
