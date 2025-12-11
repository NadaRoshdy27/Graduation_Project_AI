"""
Brand Owner Raw Material Recommendation Model.
Combines time-series forecasting with item-based similarity.
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict


class OwnerRecommender:
    """Recommendation system for brand owner raw material recommendations."""
    
    def __init__(self):
        """Initialize the recommender."""
        self.material_similarity = None
        self.owner_material_history = defaultdict(list)
        self.materials_df = None
        self.owners_df = None
        self.purchase_history_df = None
        self.production_df = None
        self.is_trained = False
    
    def train(
        self,
        purchase_history_df: pd.DataFrame,
        production_df: pd.DataFrame,
        materials_df: pd.DataFrame,
        owners_df: pd.DataFrame
    ):
        """
        Train the recommendation model.
        
        Args:
            purchase_history_df: Historical raw material purchases
            production_df: Production volume data
            materials_df: Raw materials catalog
            owners_df: Brand owner information
        """
        print("Training Owner Recommendation Model...")
        
        self.materials_df = materials_df.copy()
        self.owners_df = owners_df.copy()
        self.purchase_history_df = purchase_history_df.copy()
        self.production_df = production_df.copy()
        
        # Build owner purchase history
        print("Building purchase history...")
        self._build_purchase_history(purchase_history_df)
        
        # Calculate material similarity
        print("Calculating material similarity...")
        self._calculate_material_similarity(purchase_history_df, materials_df)
        
        self.is_trained = True
        print("Training complete!")
    
    def _build_purchase_history(self, purchase_history_df: pd.DataFrame):
        """Build a mapping of owner to their purchased materials."""
        for _, row in purchase_history_df.iterrows():
            owner_id = row['owner_id']
            material_id = row['material_id']
            quantity = row['quantity']
            
            self.owner_material_history[owner_id].append({
                'material_id': material_id,
                'quantity': quantity,
                'date': row['date']
            })
    
    def _calculate_material_similarity(
        self,
        purchase_history_df: pd.DataFrame,
        materials_df: pd.DataFrame
    ):
        """Calculate material-to-material similarity based on co-purchase patterns."""
        # Create owner-material matrix
        n_materials = len(materials_df)
        material_ids = materials_df['material_id'].tolist()
        material_idx_map = {mid: idx for idx, mid in enumerate(material_ids)}
        
        # Count co-purchases
        owner_groups = purchase_history_df.groupby('owner_id')['material_id'].apply(list)
        
        # Build co-occurrence matrix
        co_occurrence = np.zeros((n_materials, n_materials))
        
        for materials in owner_groups:
            unique_materials = list(set(materials))
            for i, mat1 in enumerate(unique_materials):
                for mat2 in unique_materials[i:]:
                    if mat1 in material_idx_map and mat2 in material_idx_map:
                        idx1 = material_idx_map[mat1]
                        idx2 = material_idx_map[mat2]
                        co_occurrence[idx1, idx2] += 1
                        if idx1 != idx2:
                            co_occurrence[idx2, idx1] += 1
        
        # Calculate cosine similarity
        # Add small epsilon to avoid division by zero
        row_sums = co_occurrence.sum(axis=1, keepdims=True) + 1e-10
        normalized = co_occurrence / row_sums
        
        self.material_similarity = cosine_similarity(normalized)
        self.material_idx_map = material_idx_map
        self.reverse_material_map = {idx: mid for mid, idx in material_idx_map.items()}
    
    def predict(
        self,
        owner_id: int,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Generate raw material recommendations for a brand owner.
        
        Args:
            owner_id: Brand owner ID
            top_k: Number of recommendations to return
        
        Returns:
            List of recommended materials with scores and reasons
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get owner's purchase history
        owner_history = self.owner_material_history.get(owner_id, [])
        
        if not owner_history:
            # Cold start: recommend popular materials
            return self._get_popular_materials(top_k)
        
        # Get materials the owner has purchased
        purchased_material_ids = [item['material_id'] for item in owner_history]
        
        # Calculate scores for all materials
        material_scores = defaultdict(float)
        material_reasons = {}
        
        for material_id in purchased_material_ids:
            if material_id not in self.material_idx_map:
                continue
            
            mat_idx = self.material_idx_map[material_id]
            
            # Get similar materials
            similarities = self.material_similarity[mat_idx]
            
            for other_idx, similarity in enumerate(similarities):
                other_material_id = self.reverse_material_map.get(other_idx)
                
                if other_material_id and other_material_id not in purchased_material_ids:
                    material_scores[other_material_id] += similarity
                    
                    # Track reason
                    if other_material_id not in material_reasons:
                        source_material = self.materials_df[
                            self.materials_df['material_id'] == material_id
                        ].iloc[0]
                        material_reasons[other_material_id] = (
                            f"Similar to {source_material['name']}"
                        )
        
        # Also consider seasonal/production trends
        production_scores = self._get_production_based_scores(owner_id)
        
        # Combine scores
        for material_id, score in production_scores.items():
            material_scores[material_id] += score * 0.5  # Weight production trends
            if material_id not in material_reasons:
                material_reasons[material_id] = "Based on production trends"
        
        # Sort and get top-k
        sorted_materials = sorted(
            material_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Format recommendations
        recommendations = []
        for material_id, score in sorted_materials:
            material = self.materials_df[
                self.materials_df['material_id'] == material_id
            ].iloc[0]
            
            recommendations.append({
                'material_id': int(material_id),
                'name': material['name'],
                'category': material['category'],
                'unit_cost': float(material['unit_cost']),
                'score': float(score),
                'reason': material_reasons.get(material_id, "Recommended for you")
            })
        
        return recommendations
    
    def _get_production_based_scores(self, owner_id: int) -> Dict[int, float]:
        """Get material scores based on production trends."""
        scores = defaultdict(float)
        
        # Get owner's industry
        owner = self.owners_df[self.owners_df['owner_id'] == owner_id]
        if len(owner) == 0:
            return scores
        
        industry = owner.iloc[0]['industry']
        
        # Map industries to material categories (simplified)
        industry_material_map = {
            "Textiles": ["Textiles", "Packaging"],
            "Electronics": ["Electronics Components", "Metals", "Packaging"],
            "Cosmetics": ["Chemicals", "Packaging"],
            "Food & Beverage": ["Chemicals", "Packaging"],
            "Furniture": ["Metals", "Textiles", "Packaging"],
        }
        
        relevant_categories = industry_material_map.get(industry, [])
        
        # Give higher scores to materials in relevant categories
        for _, material in self.materials_df.iterrows():
            if material['category'] in relevant_categories:
                scores[material['material_id']] = 0.5
        
        return scores
    
    def _get_popular_materials(self, top_k: int) -> List[Dict]:
        """Get popular materials for cold start."""
        # Count purchases for each material
        material_counts = self.purchase_history_df['material_id'].value_counts()
        top_materials = material_counts.head(top_k).index.tolist()
        
        recommendations = []
        for material_id in top_materials:
            material = self.materials_df[
                self.materials_df['material_id'] == material_id
            ].iloc[0]
            
            recommendations.append({
                'material_id': int(material_id),
                'name': material['name'],
                'category': material['category'],
                'unit_cost': float(material['unit_cost']),
                'score': 1.0,
                'reason': "Popular material"
            })
        
        return recommendations
    
    def save(self, filepath: Path):
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        model_data = {
            'material_similarity': self.material_similarity,
            'owner_material_history': dict(self.owner_material_history),
            'materials_df': self.materials_df,
            'owners_df': self.owners_df,
            'purchase_history_df': self.purchase_history_df,
            'production_df': self.production_df,
            'material_idx_map': self.material_idx_map,
            'reverse_material_map': self.reverse_material_map,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: Path):
        """Load a trained model from disk."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        model = cls()
        model.material_similarity = model_data['material_similarity']
        model.owner_material_history = defaultdict(list, model_data['owner_material_history'])
        model.materials_df = model_data['materials_df']
        model.owners_df = model_data['owners_df']
        model.purchase_history_df = model_data['purchase_history_df']
        model.production_df = model_data['production_df']
        model.material_idx_map = model_data['material_idx_map']
        model.reverse_material_map = model_data['reverse_material_map']
        model.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
        return model
