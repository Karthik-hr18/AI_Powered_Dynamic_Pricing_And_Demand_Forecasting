import csv
import random
from datetime import date, datetime, timedelta
import os

def generate_120_sku_6month_datasets():
    random.seed(42)
    docs_dir = "c:/Users/karth/Projects/AI Powered/docs"
    os.makedirs(docs_dir, exist_ok=True)

    # 115 Realistic Indian Kirana & Supermarket Products across 12 Categories
    catalog = [
        # --- 1. Flours, Grains & Staples ---
        {"Product_ID": "P001", "Product_Name": "Aashirvaad Superior Sharbati Atta 5kg", "Category": "Flours & Grains", "Brand": "Aashirvaad", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 285.0, "Cost_Price_INR": 230.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.6},
        {"Product_ID": "P002", "Product_Name": "Aashirvaad Select 100% MP Sharbati Wheat 10kg", "Category": "Flours & Grains", "Brand": "Aashirvaad", "Supplier_ID": "S001", "Reorder_Level": 25, "Unit_Price_INR": 580.0, "Cost_Price_INR": 470.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.3},
        {"Product_ID": "P003", "Product_Name": "Fortune Chakki Fresh Atta 5kg", "Category": "Flours & Grains", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 260.0, "Cost_Price_INR": 210.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},
        {"Product_ID": "P004", "Product_Name": "Pillsbury Chakki Fresh Wheat Atta 5kg", "Category": "Flours & Grains", "Brand": "Pillsbury", "Supplier_ID": "S001", "Reorder_Level": 30, "Unit_Price_INR": 270.0, "Cost_Price_INR": 215.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.3},
        {"Product_ID": "P005", "Product_Name": "Tata Sampann Fine Maida 1kg", "Category": "Flours & Grains", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 55.0, "Cost_Price_INR": 42.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P006", "Product_Name": "Tata Sampann 100% Chana Dal Besan 1kg", "Category": "Flours & Grains", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 115.0, "Cost_Price_INR": 88.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},
        {"Product_ID": "P007", "Product_Name": "Tata Sampann Organic Thick Poha 500g", "Category": "Flours & Grains", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 65.0, "Cost_Price_INR": 48.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P008", "Product_Name": "MTR Roasted Bombay Rava 1kg", "Category": "Flours & Grains", "Brand": "MTR", "Supplier_ID": "S003", "Reorder_Level": 35, "Unit_Price_INR": 85.0, "Cost_Price_INR": 65.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.4},
        {"Product_ID": "P009", "Product_Name": "MTR Double Roasted Rice Vermicelli 400g", "Category": "Flours & Grains", "Brand": "MTR", "Supplier_ID": "S003", "Reorder_Level": 35, "Unit_Price_INR": 55.0, "Cost_Price_INR": 40.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},

        # --- 2. Rice & Grains ---
        {"Product_ID": "P010", "Product_Name": "Fortune Special Biryani Basmati Rice 5kg", "Category": "Rice & Grains", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 30, "Unit_Price_INR": 560.0, "Cost_Price_INR": 450.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.4},
        {"Product_ID": "P011", "Product_Name": "India Gate Basmati Rice Classic 5kg", "Category": "Rice & Grains", "Brand": "India Gate", "Supplier_ID": "S001", "Reorder_Level": 30, "Unit_Price_INR": 640.0, "Cost_Price_INR": 520.0, "Base_Stock": 150, "Restock_Qty": 110, "Velocity": 1.3},
        {"Product_ID": "P012", "Product_Name": "Daawat Rozana Gold Basmati Rice 5kg", "Category": "Rice & Grains", "Brand": "Daawat", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 420.0, "Cost_Price_INR": 340.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.5},
        {"Product_ID": "P013", "Product_Name": "Royal Sona Masoori Premium Raw Rice 10kg", "Category": "Rice & Grains", "Brand": "Royal", "Supplier_ID": "S001", "Reorder_Level": 25, "Unit_Price_INR": 680.0, "Cost_Price_INR": 550.0, "Base_Stock": 150, "Restock_Qty": 110, "Velocity": 1.4},
        {"Product_ID": "P014", "Product_Name": "24 Mantra Organic Brown Rice 1kg", "Category": "Rice & Grains", "Brand": "24 Mantra", "Supplier_ID": "S002", "Reorder_Level": 30, "Unit_Price_INR": 145.0, "Cost_Price_INR": 112.0, "Base_Stock": 140, "Restock_Qty": 100, "Velocity": 1.1},
        {"Product_ID": "P015", "Product_Name": "Quaker Rolled Oats 100% Wholegrain 1kg", "Category": "Rice & Grains", "Brand": "Quaker", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 210.0, "Cost_Price_INR": 165.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.5},
        {"Product_ID": "P016", "Product_Name": "Kelloggs Corn Flakes Original 500g", "Category": "Rice & Grains", "Brand": "Kelloggs", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 210.0, "Cost_Price_INR": 168.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.4},
        {"Product_ID": "P017", "Product_Name": "Saffola Masala Oats Classic Masala 500g", "Category": "Rice & Grains", "Brand": "Saffola", "Supplier_ID": "S005", "Reorder_Level": 45, "Unit_Price_INR": 175.0, "Cost_Price_INR": 135.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.7},

        # --- 3. Pulses & Dals ---
        {"Product_ID": "P018", "Product_Name": "Tata Sampann Unpolished Toor Dal 1kg", "Category": "Pulses & Dals", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 50, "Unit_Price_INR": 175.0, "Cost_Price_INR": 138.0, "Base_Stock": 250, "Restock_Qty": 200, "Velocity": 2.0},
        {"Product_ID": "P019", "Product_Name": "Tata Sampann Organic Moong Dal Yellow 1kg", "Category": "Pulses & Dals", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 45, "Unit_Price_INR": 155.0, "Cost_Price_INR": 122.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.7},
        {"Product_ID": "P020", "Product_Name": "Tata Sampann Organic Moong Chilka Dal 1kg", "Category": "Pulses & Dals", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 35, "Unit_Price_INR": 160.0, "Cost_Price_INR": 126.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P021", "Product_Name": "Aashirvaad Organic Chana Dal 1kg", "Category": "Pulses & Dals", "Brand": "Aashirvaad", "Supplier_ID": "S001", "Reorder_Level": 45, "Unit_Price_INR": 140.0, "Cost_Price_INR": 110.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P022", "Product_Name": "Tata Sampann Unpolished Urad Dal Whole 1kg", "Category": "Pulses & Dals", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 185.0, "Cost_Price_INR": 146.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.5},
        {"Product_ID": "P023", "Product_Name": "Tata Sampann Unpolished Masoor Dal Malka 1kg", "Category": "Pulses & Dals", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 135.0, "Cost_Price_INR": 105.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P024", "Product_Name": "Fortune Special Red Rajma Chitra 1kg", "Category": "Pulses & Dals", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 195.0, "Cost_Price_INR": 155.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P025", "Product_Name": "Fortune Big Kabuli Chana Chickpeas 1kg", "Category": "Pulses & Dals", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 35, "Unit_Price_INR": 190.0, "Cost_Price_INR": 150.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},

        # --- 4. Edible Oils & Ghee ---
        {"Product_ID": "P026", "Product_Name": "Fortune Sunlite Refined Sunflower Oil 1L Pouch", "Category": "Oil & Ghee", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 60, "Unit_Price_INR": 145.0, "Cost_Price_INR": 120.0, "Base_Stock": 300, "Restock_Qty": 250, "Velocity": 2.2},
        {"Product_ID": "P027", "Product_Name": "Fortune Sunlite Refined Sunflower Oil 5L Jar", "Category": "Oil & Ghee", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 25, "Unit_Price_INR": 710.0, "Cost_Price_INR": 590.0, "Base_Stock": 140, "Restock_Qty": 100, "Velocity": 1.3},
        {"Product_ID": "P028", "Product_Name": "Dhara Kachi Ghani Mustard Oil 1L Bottle", "Category": "Oil & Ghee", "Brand": "Dhara", "Supplier_ID": "S001", "Reorder_Level": 45, "Unit_Price_INR": 165.0, "Cost_Price_INR": 135.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P029", "Product_Name": "Saffola Gold Pro Healthy Blend Oil 1L Pouch", "Category": "Oil & Ghee", "Brand": "Saffola", "Supplier_ID": "S005", "Reorder_Level": 45, "Unit_Price_INR": 185.0, "Cost_Price_INR": 152.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},
        {"Product_ID": "P030", "Product_Name": "Fortune Rice Bran Health Oil 1L Pouch", "Category": "Oil & Ghee", "Brand": "Fortune", "Supplier_ID": "S001", "Reorder_Level": 40, "Unit_Price_INR": 155.0, "Cost_Price_INR": 128.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P031", "Product_Name": "Amul Pure Cow Desi Ghee 1L Tin", "Category": "Oil & Ghee", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 45, "Unit_Price_INR": 620.0, "Cost_Price_INR": 520.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.6},
        {"Product_ID": "P032", "Product_Name": "Amul Pure Cow Desi Ghee 500ml Pouch", "Category": "Oil & Ghee", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 50, "Unit_Price_INR": 320.0, "Cost_Price_INR": 265.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.7},
        {"Product_ID": "P033", "Product_Name": "Nandini Pure Cow Ghee 500ml Pouch", "Category": "Oil & Ghee", "Brand": "Nandini", "Supplier_ID": "S004", "Reorder_Level": 45, "Unit_Price_INR": 310.0, "Cost_Price_INR": 260.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P034", "Product_Name": "Patanjali Cow Ghee 1L Cartridge", "Category": "Oil & Ghee", "Brand": "Patanjali", "Supplier_ID": "S004", "Reorder_Level": 35, "Unit_Price_INR": 595.0, "Cost_Price_INR": 495.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},

        # --- 5. Dairy & Breakfast ---
        {"Product_ID": "P035", "Product_Name": "Amul Pasteurised Salted Butter 500g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 55, "Unit_Price_INR": 275.0, "Cost_Price_INR": 235.0, "Base_Stock": 240, "Restock_Qty": 200, "Velocity": 1.9},
        {"Product_ID": "P036", "Product_Name": "Amul Pasteurised Salted Butter 100g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 65, "Unit_Price_INR": 58.0, "Cost_Price_INR": 49.0, "Base_Stock": 280, "Restock_Qty": 240, "Velocity": 2.2},
        {"Product_ID": "P037", "Product_Name": "Amul Processed Cheese Block 400g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 40, "Unit_Price_INR": 230.0, "Cost_Price_INR": 190.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.5},
        {"Product_ID": "P038", "Product_Name": "Amul Cheese Slices 200g (10 Slices)", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 45, "Unit_Price_INR": 145.0, "Cost_Price_INR": 120.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.7},
        {"Product_ID": "P039", "Product_Name": "Amul Fresh Malai Paneer 200g", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 45, "Unit_Price_INR": 95.0, "Cost_Price_INR": 78.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.8},
        {"Product_ID": "P040", "Product_Name": "Mother Dairy Classic Dahi Cup 400g", "Category": "Dairy", "Brand": "Mother Dairy", "Supplier_ID": "S004", "Reorder_Level": 50, "Unit_Price_INR": 45.0, "Cost_Price_INR": 36.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.9},
        {"Product_ID": "P041", "Product_Name": "Nestle Milkmaid Sweetened Condensed Milk 400g", "Category": "Dairy", "Brand": "Nestle", "Supplier_ID": "S005", "Reorder_Level": 35, "Unit_Price_INR": 145.0, "Cost_Price_INR": 115.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P042", "Product_Name": "Amul Taaza Homogenised Toned Milk 1L Tetra", "Category": "Dairy", "Brand": "Amul", "Supplier_ID": "S004", "Reorder_Level": 60, "Unit_Price_INR": 74.0, "Cost_Price_INR": 63.0, "Base_Stock": 280, "Restock_Qty": 240, "Velocity": 2.1},

        # --- 6. Beverages (Tea, Coffee, Health Drinks) ---
        {"Product_ID": "P043", "Product_Name": "Tata Tea Gold Royal 500g", "Category": "Beverages", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 60, "Unit_Price_INR": 310.0, "Cost_Price_INR": 245.0, "Base_Stock": 260, "Restock_Qty": 220, "Velocity": 2.0},
        {"Product_ID": "P044", "Product_Name": "Tata Tea Premium Desh Ki Chai 1kg", "Category": "Beverages", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 50, "Unit_Price_INR": 480.0, "Cost_Price_INR": 385.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.7},
        {"Product_ID": "P045", "Product_Name": "Brooke Bond Red Label Tea 500g", "Category": "Beverages", "Brand": "Red Label", "Supplier_ID": "S006", "Reorder_Level": 60, "Unit_Price_INR": 290.0, "Cost_Price_INR": 230.0, "Base_Stock": 250, "Restock_Qty": 210, "Velocity": 1.9},
        {"Product_ID": "P046", "Product_Name": "Brooke Bond Taj Mahal Tea 500g", "Category": "Beverages", "Brand": "Taj Mahal", "Supplier_ID": "S006", "Reorder_Level": 35, "Unit_Price_INR": 380.0, "Cost_Price_INR": 300.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P047", "Product_Name": "Wagh Bakri Premium Masala Tea 500g", "Category": "Beverages", "Brand": "Wagh Bakri", "Supplier_ID": "S006", "Reorder_Level": 40, "Unit_Price_INR": 275.0, "Cost_Price_INR": 215.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.5},
        {"Product_ID": "P048", "Product_Name": "Tetley Pure Green Tea Bags (Pack of 100)", "Category": "Beverages", "Brand": "Tetley", "Supplier_ID": "S002", "Reorder_Level": 30, "Unit_Price_INR": 450.0, "Cost_Price_INR": 355.0, "Base_Stock": 150, "Restock_Qty": 110, "Velocity": 1.2},
        {"Product_ID": "P049", "Product_Name": "Nescafe Classic Instant Coffee Jar 100g", "Category": "Beverages", "Brand": "Nescafe", "Supplier_ID": "S005", "Reorder_Level": 45, "Unit_Price_INR": 340.0, "Cost_Price_INR": 270.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P050", "Product_Name": "Nescafe Sunrise Instant Coffee-Chicory 200g", "Category": "Beverages", "Brand": "Nescafe", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 260.0, "Cost_Price_INR": 205.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P051", "Product_Name": "Bru Instant Coffee Jar 100g", "Category": "Beverages", "Brand": "Bru", "Supplier_ID": "S006", "Reorder_Level": 45, "Unit_Price_INR": 295.0, "Cost_Price_INR": 235.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},
        {"Product_ID": "P052", "Product_Name": "Cadbury Bournvita Pro-Health Drink 1kg", "Category": "Beverages", "Brand": "Cadbury", "Supplier_ID": "S007", "Reorder_Level": 45, "Unit_Price_INR": 420.0, "Cost_Price_INR": 335.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},
        {"Product_ID": "P053", "Product_Name": "Horlicks Classic Malt Health Drink 1kg", "Category": "Beverages", "Brand": "Horlicks", "Supplier_ID": "S006", "Reorder_Level": 40, "Unit_Price_INR": 435.0, "Cost_Price_INR": 350.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P054", "Product_Name": "Real Fruit Power Mixed Fruit Juice 1L", "Category": "Beverages", "Brand": "Real", "Supplier_ID": "S005", "Reorder_Level": 45, "Unit_Price_INR": 125.0, "Cost_Price_INR": 98.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.7},

        # --- 7. Biscuits, Cookies & Bakery ---
        {"Product_ID": "P055", "Product_Name": "Parle-G Gold Glucose Biscuits 1kg Family Pack", "Category": "Biscuits & Bakery", "Brand": "Parle", "Supplier_ID": "S008", "Reorder_Level": 75, "Unit_Price_INR": 120.0, "Cost_Price_INR": 95.0, "Base_Stock": 320, "Restock_Qty": 270, "Velocity": 2.4},
        {"Product_ID": "P056", "Product_Name": "Parle-G Original Glucose Biscuits 800g", "Category": "Biscuits & Bakery", "Brand": "Parle", "Supplier_ID": "S008", "Reorder_Level": 75, "Unit_Price_INR": 85.0, "Cost_Price_INR": 68.0, "Base_Stock": 310, "Restock_Qty": 260, "Velocity": 2.3},
        {"Product_ID": "P057", "Product_Name": "Britannia Good Day Butter Cookies 600g", "Category": "Biscuits & Bakery", "Brand": "Britannia", "Supplier_ID": "S008", "Reorder_Level": 60, "Unit_Price_INR": 140.0, "Cost_Price_INR": 108.0, "Base_Stock": 260, "Restock_Qty": 220, "Velocity": 2.0},
        {"Product_ID": "P058", "Product_Name": "Britannia Good Day Cashew Cookies 600g", "Category": "Biscuits & Bakery", "Brand": "Britannia", "Supplier_ID": "S008", "Reorder_Level": 60, "Unit_Price_INR": 150.0, "Cost_Price_INR": 115.0, "Base_Stock": 250, "Restock_Qty": 210, "Velocity": 1.9},
        {"Product_ID": "P059", "Product_Name": "Britannia Marie Gold Biscuits 1kg Super Saver", "Category": "Biscuits & Bakery", "Brand": "Britannia", "Supplier_ID": "S008", "Reorder_Level": 65, "Unit_Price_INR": 140.0, "Cost_Price_INR": 110.0, "Base_Stock": 270, "Restock_Qty": 230, "Velocity": 2.1},
        {"Product_ID": "P060", "Product_Name": "Sunfeast Dark Fantasy Choco Fills 300g", "Category": "Biscuits & Bakery", "Brand": "Sunfeast", "Supplier_ID": "S008", "Reorder_Level": 45, "Unit_Price_INR": 160.0, "Cost_Price_INR": 120.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P061", "Product_Name": "Britannia Bourbon Chocolate Cream Biscuits 400g", "Category": "Biscuits & Bakery", "Brand": "Britannia", "Supplier_ID": "S008", "Reorder_Level": 50, "Unit_Price_INR": 95.0, "Cost_Price_INR": 72.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.7},
        {"Product_ID": "P062", "Product_Name": "Parle Hide & Seek Chocolate Chip Cookies 350g", "Category": "Biscuits & Bakery", "Brand": "Parle", "Supplier_ID": "S008", "Reorder_Level": 45, "Unit_Price_INR": 110.0, "Cost_Price_INR": 82.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P063", "Product_Name": "Britannia Premium Bake Rusk Toast 400g", "Category": "Biscuits & Bakery", "Brand": "Britannia", "Supplier_ID": "S008", "Reorder_Level": 50, "Unit_Price_INR": 60.0, "Cost_Price_INR": 46.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.8},

        # --- 8. Snacks, Namkeen & Noodles ---
        {"Product_ID": "P064", "Product_Name": "Maggi 2-Minute Masala Noodles 12-Pack 840g", "Category": "Snacks & Noodles", "Brand": "Nestle", "Supplier_ID": "S005", "Reorder_Level": 75, "Unit_Price_INR": 168.0, "Cost_Price_INR": 134.0, "Base_Stock": 320, "Restock_Qty": 270, "Velocity": 2.3},
        {"Product_ID": "P065", "Product_Name": "Maggi 2-Minute Masala Noodles 4-Pack 280g", "Category": "Snacks & Noodles", "Brand": "Nestle", "Supplier_ID": "S005", "Reorder_Level": 80, "Unit_Price_INR": 56.0, "Cost_Price_INR": 45.0, "Base_Stock": 340, "Restock_Qty": 290, "Velocity": 2.5},
        {"Product_ID": "P066", "Product_Name": "Sunfeast YiPPee! Magic Masala Noodles 8-Pack 560g", "Category": "Snacks & Noodles", "Brand": "Sunfeast", "Supplier_ID": "S008", "Reorder_Level": 55, "Unit_Price_INR": 110.0, "Cost_Price_INR": 86.0, "Base_Stock": 240, "Restock_Qty": 200, "Velocity": 1.8},
        {"Product_ID": "P067", "Product_Name": "Haldiram Nagpur Aloo Bhujia 1kg", "Category": "Snacks & Noodles", "Brand": "Haldiram", "Supplier_ID": "S009", "Reorder_Level": 60, "Unit_Price_INR": 240.0, "Cost_Price_INR": 180.0, "Base_Stock": 260, "Restock_Qty": 220, "Velocity": 1.9},
        {"Product_ID": "P068", "Product_Name": "Haldiram Nagpur Khatta Meetha Namkeen 1kg", "Category": "Snacks & Noodles", "Brand": "Haldiram", "Supplier_ID": "S009", "Reorder_Level": 55, "Unit_Price_INR": 230.0, "Cost_Price_INR": 172.0, "Base_Stock": 240, "Restock_Qty": 200, "Velocity": 1.8},
        {"Product_ID": "P069", "Product_Name": "Bikaji Bhujia Sev 1kg Festive Pack", "Category": "Snacks & Noodles", "Brand": "Bikaji", "Supplier_ID": "S009", "Reorder_Level": 50, "Unit_Price_INR": 260.0, "Cost_Price_INR": 195.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.7},
        {"Product_ID": "P070", "Product_Name": "Haldiram Salted Moong Dal 400g", "Category": "Snacks & Noodles", "Brand": "Haldiram", "Supplier_ID": "S009", "Reorder_Level": 45, "Unit_Price_INR": 115.0, "Cost_Price_INR": 86.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},
        {"Product_ID": "P071", "Product_Name": "Lays India's Magic Masala Potato Chips 115g", "Category": "Snacks & Noodles", "Brand": "Lays", "Supplier_ID": "S009", "Reorder_Level": 70, "Unit_Price_INR": 50.0, "Cost_Price_INR": 38.0, "Base_Stock": 300, "Restock_Qty": 260, "Velocity": 2.2},
        {"Product_ID": "P072", "Product_Name": "Lays Classic Salted Potato Chips 115g", "Category": "Snacks & Noodles", "Brand": "Lays", "Supplier_ID": "S009", "Reorder_Level": 65, "Unit_Price_INR": 50.0, "Cost_Price_INR": 38.0, "Base_Stock": 280, "Restock_Qty": 240, "Velocity": 2.0},
        {"Product_ID": "P073", "Product_Name": "Kurkure Masala Munch Crunchy Snacks 115g", "Category": "Snacks & Noodles", "Brand": "Kurkure", "Supplier_ID": "S009", "Reorder_Level": 70, "Unit_Price_INR": 50.0, "Cost_Price_INR": 38.0, "Base_Stock": 300, "Restock_Qty": 260, "Velocity": 2.2},
        {"Product_ID": "P074", "Product_Name": "Bingo! Mad Angles Achaari Masti 130g", "Category": "Snacks & Noodles", "Brand": "Bingo", "Supplier_ID": "S008", "Reorder_Level": 50, "Unit_Price_INR": 50.0, "Cost_Price_INR": 38.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.6},
        {"Product_ID": "P075", "Product_Name": "Act II Golden Sizzle Butter Popcorn 150g", "Category": "Snacks & Noodles", "Brand": "Act II", "Supplier_ID": "S005", "Reorder_Level": 45, "Unit_Price_INR": 65.0, "Cost_Price_INR": 48.0, "Base_Stock": 200, "Restock_Qty": 160, "Velocity": 1.5},

        # --- 9. Spices, Sugar, Salt & Condiments ---
        {"Product_ID": "P076", "Product_Name": "Tata Salt Vacuum Evaporated Iodized 1kg", "Category": "Spices & Seasoning", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 80, "Unit_Price_INR": 28.0, "Cost_Price_INR": 22.0, "Base_Stock": 360, "Restock_Qty": 310, "Velocity": 2.5},
        {"Product_ID": "P077", "Product_Name": "Tata Salt Rock Salt Sendha Namak 1kg", "Category": "Spices & Seasoning", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 110.0, "Cost_Price_INR": 82.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P078", "Product_Name": "Madhur Pure & Hygienic Refined Sugar 5kg", "Category": "Spices & Seasoning", "Brand": "Madhur", "Supplier_ID": "S002", "Reorder_Level": 60, "Unit_Price_INR": 250.0, "Cost_Price_INR": 205.0, "Base_Stock": 270, "Restock_Qty": 230, "Velocity": 2.1},
        {"Product_ID": "P079", "Product_Name": "Madhur Pure & Hygienic Refined Sugar 1kg", "Category": "Spices & Seasoning", "Brand": "Madhur", "Supplier_ID": "S002", "Reorder_Level": 70, "Unit_Price_INR": 55.0, "Cost_Price_INR": 44.0, "Base_Stock": 300, "Restock_Qty": 260, "Velocity": 2.2},
        {"Product_ID": "P080", "Product_Name": "Organic Tattva Natural Jaggery Powder 1kg", "Category": "Spices & Seasoning", "Brand": "Organic Tattva", "Supplier_ID": "S002", "Reorder_Level": 40, "Unit_Price_INR": 130.0, "Cost_Price_INR": 95.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P081", "Product_Name": "Everest Super Garam Masala 100g", "Category": "Spices & Seasoning", "Brand": "Everest", "Supplier_ID": "S003", "Reorder_Level": 55, "Unit_Price_INR": 92.0, "Cost_Price_INR": 70.0, "Base_Stock": 240, "Restock_Qty": 200, "Velocity": 1.8},
        {"Product_ID": "P082", "Product_Name": "Everest Pav Bhaji Masala 100g", "Category": "Spices & Seasoning", "Brand": "Everest", "Supplier_ID": "S003", "Reorder_Level": 50, "Unit_Price_INR": 82.0, "Cost_Price_INR": 62.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.6},
        {"Product_ID": "P083", "Product_Name": "MDH Deggi Mirch Red Chilli Powder 100g", "Category": "Spices & Seasoning", "Brand": "MDH", "Supplier_ID": "S003", "Reorder_Level": 55, "Unit_Price_INR": 88.0, "Cost_Price_INR": 66.0, "Base_Stock": 240, "Restock_Qty": 200, "Velocity": 1.8},
        {"Product_ID": "P084", "Product_Name": "MDH Sambhar Masala Powder 100g", "Category": "Spices & Seasoning", "Brand": "MDH", "Supplier_ID": "S003", "Reorder_Level": 50, "Unit_Price_INR": 80.0, "Cost_Price_INR": 60.0, "Base_Stock": 220, "Restock_Qty": 180, "Velocity": 1.6},
        {"Product_ID": "P085", "Product_Name": "Catch Pure Turmeric Haldi Powder 200g", "Category": "Spices & Seasoning", "Brand": "Catch", "Supplier_ID": "S003", "Reorder_Level": 55, "Unit_Price_INR": 75.0, "Cost_Price_INR": 56.0, "Base_Stock": 240, "Restock_Qty": 200, "Velocity": 1.7},
        {"Product_ID": "P086", "Product_Name": "Catch Coriander Dhaniya Powder 200g", "Category": "Spices & Seasoning", "Brand": "Catch", "Supplier_ID": "S003", "Reorder_Level": 50, "Unit_Price_INR": 70.0, "Cost_Price_INR": 52.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.6},
        {"Product_ID": "P087", "Product_Name": "Patanjali Natural Kashmiri Kesar 1g", "Category": "Spices & Seasoning", "Brand": "Patanjali", "Supplier_ID": "S003", "Reorder_Level": 20, "Unit_Price_INR": 290.0, "Cost_Price_INR": 220.0, "Base_Stock": 110, "Restock_Qty": 80, "Velocity": 1.0},

        # --- 10. Sauces, Spreads & Instant Food ---
        {"Product_ID": "P088", "Product_Name": "Kissan Fresh Tomato Ketchup Bottle 1kg", "Category": "Sauces & Spreads", "Brand": "Kissan", "Supplier_ID": "S005", "Reorder_Level": 50, "Unit_Price_INR": 160.0, "Cost_Price_INR": 122.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.8},
        {"Product_ID": "P089", "Product_Name": "Kissan Mixed Fruit Jam 1kg Glass Jar", "Category": "Sauces & Spreads", "Brand": "Kissan", "Supplier_ID": "S005", "Reorder_Level": 40, "Unit_Price_INR": 280.0, "Cost_Price_INR": 220.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.4},
        {"Product_ID": "P090", "Product_Name": "Ching's Secret Schezwan Chutney 250g", "Category": "Sauces & Spreads", "Brand": "Ching's", "Supplier_ID": "S005", "Reorder_Level": 45, "Unit_Price_INR": 90.0, "Cost_Price_INR": 68.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P091", "Product_Name": "Dr. Oetker FunFoods Creamy Mayonnaise 800g", "Category": "Sauces & Spreads", "Brand": "FunFoods", "Supplier_ID": "S005", "Reorder_Level": 35, "Unit_Price_INR": 195.0, "Cost_Price_INR": 150.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P092", "Product_Name": "Pintola All Natural Peanut Butter Crunchy 1kg", "Category": "Sauces & Spreads", "Brand": "Pintola", "Supplier_ID": "S005", "Reorder_Level": 30, "Unit_Price_INR": 425.0, "Cost_Price_INR": 330.0, "Base_Stock": 150, "Restock_Qty": 110, "Velocity": 1.2},
        {"Product_ID": "P093", "Product_Name": "MTR Instant Gulab Jamun Mix 500g", "Category": "Sauces & Spreads", "Brand": "MTR", "Supplier_ID": "S003", "Reorder_Level": 40, "Unit_Price_INR": 145.0, "Cost_Price_INR": 110.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.5},
        {"Product_ID": "P094", "Product_Name": "Bambino Macaroni Pasta 1kg", "Category": "Sauces & Spreads", "Brand": "Bambino", "Supplier_ID": "S003", "Reorder_Level": 45, "Unit_Price_INR": 105.0, "Cost_Price_INR": 78.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},

        # --- 11. Personal Care & Hygiene ---
        {"Product_ID": "P095", "Product_Name": "Dettol Original Germ Protection Bathing Soap 125g (Pack of 4)", "Category": "Personal Care", "Brand": "Dettol", "Supplier_ID": "S010", "Reorder_Level": 55, "Unit_Price_INR": 230.0, "Cost_Price_INR": 175.0, "Base_Stock": 250, "Restock_Qty": 210, "Velocity": 1.9},
        {"Product_ID": "P096", "Product_Name": "Lifebuoy Total 10 Antibacterial Soap 125g (Pack of 4)", "Category": "Personal Care", "Brand": "Lifebuoy", "Supplier_ID": "S010", "Reorder_Level": 50, "Unit_Price_INR": 160.0, "Cost_Price_INR": 122.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.7},
        {"Product_ID": "P097", "Product_Name": "Dove Deep Moisture Nourishing Body Wash 400ml", "Category": "Personal Care", "Brand": "Dove", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 340.0, "Cost_Price_INR": 260.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P098", "Product_Name": "Dove Daily Shine Therapy Shampoo 650ml", "Category": "Personal Care", "Brand": "Dove", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 490.0, "Cost_Price_INR": 380.0, "Base_Stock": 160, "Restock_Qty": 120, "Velocity": 1.3},
        {"Product_ID": "P099", "Product_Name": "Head & Shoulders Anti-Dandruff Shampoo 340ml", "Category": "Personal Care", "Brand": "Head & Shoulders", "Supplier_ID": "S010", "Reorder_Level": 40, "Unit_Price_INR": 380.0, "Cost_Price_INR": 295.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.4},
        {"Product_ID": "P100", "Product_Name": "Colgate MaxFresh Spicy Fresh Toothpaste 300g Saver Pack", "Category": "Personal Care", "Brand": "Colgate", "Supplier_ID": "S010", "Reorder_Level": 60, "Unit_Price_INR": 220.0, "Cost_Price_INR": 165.0, "Base_Stock": 270, "Restock_Qty": 230, "Velocity": 2.0},
        {"Product_ID": "P101", "Product_Name": "Colgate Strong Teeth Anticavity Toothpaste 500g", "Category": "Personal Care", "Brand": "Colgate", "Supplier_ID": "S010", "Reorder_Level": 65, "Unit_Price_INR": 240.0, "Cost_Price_INR": 185.0, "Base_Stock": 280, "Restock_Qty": 240, "Velocity": 2.1},
        {"Product_ID": "P102", "Product_Name": "Dettol Liquid Handwash Refill Pouch 1500ml", "Category": "Personal Care", "Brand": "Dettol", "Supplier_ID": "S010", "Reorder_Level": 45, "Unit_Price_INR": 235.0, "Cost_Price_INR": 178.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P103", "Product_Name": "Vaseline Deep Moisture Body Lotion 400ml", "Category": "Personal Care", "Brand": "Vaseline", "Supplier_ID": "S010", "Reorder_Level": 40, "Unit_Price_INR": 310.0, "Cost_Price_INR": 240.0, "Base_Stock": 190, "Restock_Qty": 150, "Velocity": 1.5},
        {"Product_ID": "P104", "Product_Name": "Nivea Nourishing Body Cold Cream 200ml", "Category": "Personal Care", "Brand": "Nivea", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 240.0, "Cost_Price_INR": 180.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.4},
        {"Product_ID": "P105", "Product_Name": "Fogg Master Intense Men Body Spray 150ml", "Category": "Personal Care", "Brand": "Fogg", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 250.0, "Cost_Price_INR": 190.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.4},

        # --- 12. Household Cleaning & Festive Specials ---
        {"Product_ID": "P106", "Product_Name": "Surf Excel Easy Wash Detergent Powder 1kg", "Category": "Household Cleaning", "Brand": "Surf Excel", "Supplier_ID": "S010", "Reorder_Level": 60, "Unit_Price_INR": 155.0, "Cost_Price_INR": 122.0, "Base_Stock": 270, "Restock_Qty": 230, "Velocity": 2.1},
        {"Product_ID": "P107", "Product_Name": "Surf Excel Matic Front Load Liquid Detergent 2L", "Category": "Household Cleaning", "Brand": "Surf Excel", "Supplier_ID": "S010", "Reorder_Level": 35, "Unit_Price_INR": 480.0, "Cost_Price_INR": 380.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.4},
        {"Product_ID": "P108", "Product_Name": "Ariel Complete Washing Powder 1kg", "Category": "Household Cleaning", "Brand": "Ariel", "Supplier_ID": "S010", "Reorder_Level": 50, "Unit_Price_INR": 170.0, "Cost_Price_INR": 132.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.7},
        {"Product_ID": "P109", "Product_Name": "Vim Lemon Dishwash Gel Bottle 750ml", "Category": "Household Cleaning", "Brand": "Vim", "Supplier_ID": "S010", "Reorder_Level": 55, "Unit_Price_INR": 180.0, "Cost_Price_INR": 138.0, "Base_Stock": 250, "Restock_Qty": 210, "Velocity": 1.9},
        {"Product_ID": "P110", "Product_Name": "Vim Dishwash Bar 300g (Pack of 3)", "Category": "Household Cleaning", "Brand": "Vim", "Supplier_ID": "S010", "Reorder_Level": 65, "Unit_Price_INR": 65.0, "Cost_Price_INR": 50.0, "Base_Stock": 290, "Restock_Qty": 250, "Velocity": 2.2},
        {"Product_ID": "P111", "Product_Name": "Lizol Citrus Disinfectant Surface Cleaner 1L", "Category": "Household Cleaning", "Brand": "Lizol", "Supplier_ID": "S010", "Reorder_Level": 45, "Unit_Price_INR": 215.0, "Cost_Price_INR": 165.0, "Base_Stock": 210, "Restock_Qty": 170, "Velocity": 1.6},
        {"Product_ID": "P112", "Product_Name": "Harpic Power Plus Disinfectant Toilet Cleaner 1L", "Category": "Household Cleaning", "Brand": "Harpic", "Supplier_ID": "S010", "Reorder_Level": 50, "Unit_Price_INR": 205.0, "Cost_Price_INR": 158.0, "Base_Stock": 230, "Restock_Qty": 190, "Velocity": 1.8},
        {"Product_ID": "P113", "Product_Name": "Haldiram Kaju Katli Premium Box 500g", "Category": "Sweets & Festives", "Brand": "Haldiram", "Supplier_ID": "S009", "Reorder_Level": 35, "Unit_Price_INR": 480.0, "Cost_Price_INR": 380.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.4},
        {"Product_ID": "P114", "Product_Name": "Tata Sampann California Raw Almonds 500g", "Category": "Sweets & Festives", "Brand": "Tata", "Supplier_ID": "S002", "Reorder_Level": 35, "Unit_Price_INR": 520.0, "Cost_Price_INR": 410.0, "Base_Stock": 170, "Restock_Qty": 130, "Velocity": 1.3},
        {"Product_ID": "P115", "Product_Name": "Dabur Chyawanprash Special Immunity Booster 1kg", "Category": "Sweets & Festives", "Brand": "Dabur", "Supplier_ID": "S003", "Reorder_Level": 35, "Unit_Price_INR": 395.0, "Cost_Price_INR": 310.0, "Base_Stock": 180, "Restock_Qty": 140, "Velocity": 1.4},
    ]

    print(f"Total Master Catalog SKUs: {len(catalog)} products across 12 categories.")

    inventory_tracker = {p["Product_ID"]: p["Base_Stock"] for p in catalog}

    start_date = date(2026, 7, 1)
    end_date = date(2026, 12, 31)
    total_days = (end_date - start_date).days + 1  # 184 days

    monthly_rows = {m: [] for m in range(1, 7)}
    all_rows = []

    tx_counter = 100001

    # Date progression loop
    for day_idx in range(total_days):
        current_date = start_date + timedelta(days=day_idx)
        month_num = current_date.month - 6  # 7->1, 8->2, 9->3, 10->4, 11->5, 12->6
        
        weekday = current_date.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
        is_weekend = weekday in [4, 5, 6]

        # Festive multiplier detection
        festive_mult = 1.0
        if current_date.month == 9 and 13 <= current_date.day <= 20: # Ganesh Chaturthi
            festive_mult = 1.25
        elif current_date.month == 10 and current_date.day >= 14: # Navratri & Diwali start
            festive_mult = 1.40
        elif current_date.month == 11 and current_date.day <= 6: # Diwali celebration
            festive_mult = 1.35
        elif current_date.month == 12 and current_date.day >= 20: # Christmas & Year-End
            festive_mult = 1.30

        # Target ~190-210 transactions/day in standard months (giving ~6,000 rows/month)
        base_tx_count = random.randint(185, 205)
        if is_weekend:
            base_tx_count += random.randint(20, 35)
        if festive_mult > 1.0:
            base_tx_count += random.randint(25, 45)

        # Draw transactions from the 115 products
        # We ensure all products are drawn repeatedly throughout the day
        sampled_products = random.choices(catalog, k=base_tx_count)

        for prod in sampled_products:
            pid = prod["Product_ID"]
            pname = prod["Product_Name"]
            cat = prod["Category"]
            brand = prod["Brand"]
            supp = prod["Supplier_ID"]
            reorder_lvl = prod["Reorder_Level"]
            mrp = prod["Unit_Price_INR"]
            cost_price = prod["Cost_Price_INR"]
            velocity = prod["Velocity"]

            # Realistic basket sizing
            units_sold = int(round(random.uniform(1.0, 3.5) * velocity * (1.20 if is_weekend else 1.0) * (1.25 if festive_mult > 1.0 else 1.0)))
            units_sold = max(1, min(24, units_sold))

            # Subtle natural anomaly simulation
            if day_idx == 45 and pid == "P001" and random.random() < 0.1: # Aug 15 bulk order
                units_sold = 36
            elif day_idx == 112 and pid == "P113" and random.random() < 0.1: # Oct 21 Diwali sweets bulk order
                units_sold = 40

            # Dynamic price elasticity simulation:
            discount_pct = 0.0
            if is_weekend:
                if random.random() < 0.35:
                    discount_pct = random.choice([3.0, 5.0, 8.0]) # Promotional discount
                elif random.random() < 0.40:
                    discount_pct = random.choice([-2.0, -4.0, -5.0]) # Peak surge price
            elif festive_mult > 1.0 and random.random() < 0.45:
                discount_pct = random.choice([5.0, 7.5, 10.0])

            selling_price = round(mrp * (1.0 - (discount_pct / 100.0)), 2)
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
                curr_stock += prod["Restock_Qty"]
            
            # For 3 demo SKUs in late December, simulate low stock to showcase stockout warnings
            if month_num == 6 and current_date.day >= 26 and pid in ["P039", "P097", "P104"]:
                curr_stock = random.randint(8, 18) # Below reorder level!

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

    print("\n--- 6-MONTH MONTHLY DATASET SUMMARY (~6,000 ROWS/MONTH) ---")
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
        print(f"{label:15} ({fname}): {len(rows_m):,} rows | {unique_skus} SKUs | {total_units:,} units | INR {total_rev:,.2f}")

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
    avg_sku_count = sum(sku_counts.values()) / len(sku_counts)

    print("\n--- MASTER 6-MONTH COMBINED DATASET ---")
    print(f"File: {master_fname}")
    print(f"Total Rows: {len(all_rows):,}")
    print(f"Active SKUs: {total_skus} (100% catalog coverage across 12 categories)")
    print(f"Transactions per SKU: Min {min_sku_count} | Avg {avg_sku_count:.1f} | Max {max_sku_count}")
    print(f"Total Units Sold: {total_units_all:,}")
    print(f"Total Revenue: INR {total_rev_all:,.2f}")

if __name__ == "__main__":
    generate_120_sku_6month_datasets()
