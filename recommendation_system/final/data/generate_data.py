"""
Generate synthetic datasets for the recommendation system.
Creates realistic data with intentional patterns for model training.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Output directory
OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_customers(n_customers=1000):
    """Generate customer dataset with demographics."""
    print(f"Generating {n_customers} customers...")
    
    categories = ["Electronics", "Fashion", "Home & Garden", "Beauty & Health", "Sports & Outdoors"]
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
                 "San Antonio", "San Diego", "Dallas", "San Jose"]
    
    customers = pd.DataFrame({
        "customer_id": range(1, n_customers + 1),
        "age": np.random.randint(18, 70, n_customers),
        "gender": np.random.choice(["Male", "Female", "Other"], n_customers, p=[0.48, 0.48, 0.04]),
        "location": np.random.choice(locations, n_customers),
        "preferred_category": np.random.choice(categories, n_customers),
    })
    
    return customers


def generate_products(n_products=500):
    """Generate product dataset with categories and prices."""
    print(f"Generating {n_products} products...")
    
    categories_subcategories = {
        "Electronics": ["Smartphones", "Laptops", "Tablets", "Headphones", "Cameras"],
        "Fashion": ["Men's Clothing", "Women's Clothing", "Shoes", "Accessories", "Jewelry"],
        "Home & Garden": ["Furniture", "Kitchen", "Bedding", "Decor", "Tools"],
        "Beauty & Health": ["Skincare", "Makeup", "Haircare", "Supplements", "Fitness"],
        "Sports & Outdoors": ["Exercise Equipment", "Camping", "Cycling", "Team Sports", "Water Sports"],
    }
    
    products = []
    product_id = 1
    
    for category, subcategories in categories_subcategories.items():
        n_per_category = n_products // len(categories_subcategories)
        
        for _ in range(n_per_category):
            subcategory = np.random.choice(subcategories)
            
            # Price ranges based on category
            if category == "Electronics":
                price = np.random.uniform(50, 2000)
            elif category == "Fashion":
                price = np.random.uniform(20, 500)
            elif category == "Home & Garden":
                price = np.random.uniform(30, 1000)
            elif category == "Beauty & Health":
                price = np.random.uniform(10, 200)
            else:  # Sports & Outdoors
                price = np.random.uniform(25, 800)
            
            products.append({
                "product_id": product_id,
                "name": f"{subcategory} Product {product_id}",
                "category": category,
                "subcategory": subcategory,
                "price": round(price, 2),
            })
            product_id += 1
    
    return pd.DataFrame(products)


def generate_customer_transactions(customers, products, n_transactions=20000):
    """Generate customer transactions with realistic patterns."""
    print(f"Generating {n_transactions} customer transactions...")
    
    transactions = []
    
    # Generate transactions over the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    for _ in range(n_transactions):
        customer = customers.sample(1).iloc[0]
        
        # 70% chance customer buys from preferred category
        if np.random.random() < 0.7:
            available_products = products[products["category"] == customer["preferred_category"]]
        else:
            available_products = products
        
        if len(available_products) == 0:
            available_products = products
        
        product = available_products.sample(1).iloc[0]
        
        # Generate timestamp with some seasonality
        days_offset = np.random.randint(0, 365)
        timestamp = start_date + timedelta(days=days_offset)
        
        # Quantity (most buy 1-2 items)
        quantity = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.3, 0.1, 0.05, 0.05])
        
        transactions.append({
            "transaction_id": len(transactions) + 1,
            "customer_id": customer["customer_id"],
            "product_id": product["product_id"],
            "quantity": quantity,
            "timestamp": timestamp,
        })
    
    df = pd.DataFrame(transactions)
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["transaction_id"] = range(1, len(df) + 1)
    
    return df


def generate_brand_owners(n_owners=100):
    """Generate brand owner dataset."""
    print(f"Generating {n_owners} brand owners...")
    
    industries = ["Textiles", "Electronics", "Cosmetics", "Food & Beverage", "Furniture"]
    regions = ["North America", "Europe", "Asia", "South America", "Africa"]
    
    owners = pd.DataFrame({
        "owner_id": range(1, n_owners + 1),
        "industry": np.random.choice(industries, n_owners),
        "region": np.random.choice(regions, n_owners),
    })
    
    return owners


def generate_raw_materials(n_materials=200):
    """Generate raw materials dataset."""
    print(f"Generating {n_materials} raw materials...")
    
    categories_materials = {
        "Textiles": ["Cotton", "Polyester", "Silk", "Wool", "Nylon"],
        "Electronics Components": ["Microchips", "Resistors", "Capacitors", "LED", "Batteries"],
        "Chemicals": ["Preservatives", "Fragrances", "Emulsifiers", "Colorants", "Solvents"],
        "Packaging": ["Cardboard", "Plastic Film", "Glass Bottles", "Metal Cans", "Labels"],
        "Metals": ["Aluminum", "Steel", "Copper", "Brass", "Titanium"],
    }
    
    materials = []
    material_id = 1
    
    for category, material_types in categories_materials.items():
        n_per_category = n_materials // len(categories_materials)
        
        for _ in range(n_per_category):
            material_type = np.random.choice(material_types)
            
            # Unit cost based on category
            if category == "Electronics Components":
                unit_cost = np.random.uniform(0.5, 50)
            elif category == "Textiles":
                unit_cost = np.random.uniform(2, 30)
            elif category == "Chemicals":
                unit_cost = np.random.uniform(5, 100)
            elif category == "Packaging":
                unit_cost = np.random.uniform(0.1, 10)
            else:  # Metals
                unit_cost = np.random.uniform(10, 200)
            
            materials.append({
                "material_id": material_id,
                "name": f"{material_type} Grade {material_id}",
                "category": category,
                "supplier_id": np.random.randint(1, 21),  # 20 suppliers
                "unit_cost": round(unit_cost, 2),
            })
            material_id += 1
    
    return pd.DataFrame(materials)


def generate_owner_purchase_history(owners, materials, n_purchases=5000):
    """Generate brand owner purchase history with patterns."""
    print(f"Generating {n_purchases} owner purchase records...")
    
    # Map industries to material categories
    industry_material_map = {
        "Textiles": ["Textiles", "Packaging"],
        "Electronics": ["Electronics Components", "Metals", "Packaging"],
        "Cosmetics": ["Chemicals", "Packaging"],
        "Food & Beverage": ["Chemicals", "Packaging"],
        "Furniture": ["Metals", "Textiles", "Packaging"],
    }
    
    purchases = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    
    for _ in range(n_purchases):
        owner = owners.sample(1).iloc[0]
        
        # Select materials relevant to owner's industry
        relevant_categories = industry_material_map.get(owner["industry"], materials["category"].unique())
        available_materials = materials[materials["category"].isin(relevant_categories)]
        
        if len(available_materials) == 0:
            available_materials = materials
        
        material = available_materials.sample(1).iloc[0]
        
        # Generate date
        days_offset = np.random.randint(0, 730)
        purchase_date = start_date + timedelta(days=days_offset)
        
        # Quantity (larger orders)
        quantity = np.random.randint(100, 10000)
        
        purchases.append({
            "purchase_id": len(purchases) + 1,
            "owner_id": owner["owner_id"],
            "material_id": material["material_id"],
            "quantity": quantity,
            "date": purchase_date,
        })
    
    df = pd.DataFrame(purchases)
    df = df.sort_values("date").reset_index(drop=True)
    df["purchase_id"] = range(1, len(df) + 1)
    
    return df


def generate_production_data(owners, n_months=24):
    """Generate monthly production data with seasonal patterns."""
    print(f"Generating production data for {n_months} months...")
    
    product_categories = ["Category A", "Category B", "Category C", "Category D"]
    
    production = []
    end_date = datetime.now()
    
    for owner_id in owners["owner_id"]:
        # Each owner produces 1-3 categories
        n_categories = np.random.randint(1, 4)
        owner_categories = np.random.choice(product_categories, n_categories, replace=False)
        
        for month_offset in range(n_months):
            month_date = end_date - timedelta(days=30 * month_offset)
            month_str = month_date.strftime("%Y-%m")
            
            for category in owner_categories:
                # Base production with seasonal variation
                base_volume = np.random.randint(1000, 10000)
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * month_offset / 12)  # Annual cycle
                volume = int(base_volume * seasonal_factor)
                
                production.append({
                    "owner_id": owner_id,
                    "product_category": category,
                    "production_volume": volume,
                    "month": month_str,
                })
    
    return pd.DataFrame(production)


def main():
    """Generate all datasets and save to CSV."""
    print("=" * 60)
    print("GENERATING SYNTHETIC DATASETS FOR RECOMMENDATION SYSTEM")
    print("=" * 60)
    
    # Generate datasets
    customers = generate_customers(1000)
    products = generate_products(500)
    transactions = generate_customer_transactions(customers, products, 20000)
    owners = generate_brand_owners(100)
    materials = generate_raw_materials(200)
    purchase_history = generate_owner_purchase_history(owners, materials, 5000)
    production = generate_production_data(owners, 24)
    
    # Save to CSV
    print("\nSaving datasets to CSV files...")
    customers.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    products.to_csv(OUTPUT_DIR / "products.csv", index=False)
    transactions.to_csv(OUTPUT_DIR / "customer_transactions.csv", index=False)
    owners.to_csv(OUTPUT_DIR / "brand_owners.csv", index=False)
    materials.to_csv(OUTPUT_DIR / "raw_materials.csv", index=False)
    purchase_history.to_csv(OUTPUT_DIR / "owner_purchase_history.csv", index=False)
    production.to_csv(OUTPUT_DIR / "production_data.csv", index=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETE")
    print("=" * 60)
    print(f"Customers: {len(customers)} rows")
    print(f"Products: {len(products)} rows")
    print(f"Customer Transactions: {len(transactions)} rows")
    print(f"Brand Owners: {len(owners)} rows")
    print(f"Raw Materials: {len(materials)} rows")
    print(f"Owner Purchase History: {len(purchase_history)} rows")
    print(f"Production Data: {len(production)} rows")
    print(f"\nAll files saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
