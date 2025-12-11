"""
Training script for Owner Recommendation Model.
"""
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from models.owner_recommender import OwnerRecommender
from utils.config import settings


def main():
    """Train and save the owner recommendation model."""
    print("=" * 60)
    print("TRAINING OWNER RECOMMENDATION MODEL")
    print("=" * 60)
    
    # Load data
    print("\nLoading datasets...")
    data_dir = settings.data_dir
    
    purchase_history_df = pd.read_csv(data_dir / "owner_purchase_history.csv")
    production_df = pd.read_csv(data_dir / "production_data.csv")
    materials_df = pd.read_csv(data_dir / "raw_materials.csv")
    owners_df = pd.read_csv(data_dir / "brand_owners.csv")
    
    print(f"Loaded {len(purchase_history_df)} purchase records")
    print(f"Loaded {len(production_df)} production records")
    print(f"Loaded {len(materials_df)} materials")
    print(f"Loaded {len(owners_df)} brand owners")
    
    # Initialize and train model
    print("\nInitializing model...")
    model = OwnerRecommender()
    
    model.train(
        purchase_history_df=purchase_history_df,
        production_df=production_df,
        materials_df=materials_df,
        owners_df=owners_df
    )
    
    # Test the model
    print("\nTesting model with sample predictions...")
    sample_owner_ids = owners_df['owner_id'].sample(3).tolist()
    
    for owner_id in sample_owner_ids:
        print(f"\nRecommendations for Owner {owner_id}:")
        recommendations = model.predict(owner_id, top_k=5)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec['name']} ({rec['category']}) - Score: {rec['score']:.4f}")
            print(f"     Reason: {rec['reason']}")
    
    # Save model
    print("\nSaving model...")
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    model.save(settings.owner_model_path)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
