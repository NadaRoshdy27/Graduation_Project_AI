"""
Training script for Customer Recommendation Model.
"""
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.customer_recommender import CustomerRecommender
from utils.config import settings


def main():
    """Train and save the customer recommendation model."""
    print("=" * 60)
    print("TRAINING CUSTOMER RECOMMENDATION MODEL")
    print("=" * 60)
    
    # Load data
    print("\nLoading datasets...")
    data_dir = settings.data_dir
    
    transactions_df = pd.read_csv(data_dir / "customer_transactions.csv")
    products_df = pd.read_csv(data_dir / "products.csv")
    customers_df = pd.read_csv(data_dir / "customers.csv")
    
    print(f"Loaded {len(transactions_df)} transactions")
    print(f"Loaded {len(products_df)} products")
    print(f"Loaded {len(customers_df)} customers")
    
    # Initialize and train model
    print("\nInitializing model...")
    model = CustomerRecommender()
    
    model.train(
        transactions_df=transactions_df,
        products_df=products_df,
        customers_df=customers_df,
        epochs=settings.lightfm_epochs,
        num_threads=settings.lightfm_num_threads
    )
    
    # Test the model
    print("\nTesting model with sample predictions...")
    sample_customer_ids = customers_df['customer_id'].sample(3).tolist()
    
    for customer_id in sample_customer_ids:
        print(f"\nRecommendations for Customer {customer_id}:")
        recommendations = model.predict(customer_id, top_k=5)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['name']} ({rec['category']}) - Score: {rec['score']:.4f}")
    
    # Save model
    print("\nSaving model...")
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    model.save(settings.customer_model_path)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
