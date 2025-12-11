"""
Customer Product Recommendation Model.
Hybrid approach combining collaborative filtering (NearestNeighbors) and content-based filtering (TF-IDF).
"""
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Tuple, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix


class CustomerRecommender:
    """Hybrid recommendation system for customer product recommendations."""
    
    def __init__(self):
        """Initialize the recommender."""
        self.knn_model = None
        self.user_item_matrix = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.products_df = None
        self.customers_df = None
        self.transactions_df = None
        self.user_ids = []
        self.product_ids = []
        self.is_trained = False
    
    def train(
        self,
        transactions_df: pd.DataFrame,
        products_df: pd.DataFrame,
        customers_df: pd.DataFrame,
        epochs: int = 30,
        num_threads: int = 4
    ):
        """
        Train the hybrid recommendation model.
        
        Args:
            transactions_df: Customer transactions data
            products_df: Product catalog
            customers_df: Customer information
            epochs: Number of training epochs for LightFM
            num_threads: Number of threads for training
        """
        print("Training Customer Recommendation Model...")
        
        self.products_df = products_df.copy()
        self.customers_df = customers_df.copy()
        
        # Train collaborative filtering model (LightFM)
        print("Training collaborative filtering model...")
        self._train_collaborative(transactions_df, epochs, num_threads)
        
        # Train content-based model (TF-IDF)
        print("Training content-based model...")
        self._train_content_based(products_df)
        
        self.is_trained = True
        print("Training complete!")
    
    def _train_collaborative(self, transactions_df: pd.DataFrame, epochs: int, num_threads: int):
        """Train KNN collaborative filtering model."""
        # Store transactions for later use
        self.transactions_df = transactions_df.copy()
        
        # Get unique users and products
        self.user_ids = sorted(transactions_df['customer_id'].unique())
        self.product_ids = sorted(transactions_df['product_id'].unique())
        
        # Create user-item interaction matrix
        user_idx_map = {uid: idx for idx, uid in enumerate(self.user_ids)}
        product_idx_map = {pid: idx for idx, pid in enumerate(self.product_ids)}
        
        n_users = len(self.user_ids)
        n_products = len(self.product_ids)
        
        # Build sparse matrix
        user_item_data = np.zeros((n_users, n_products))
        
        for _, row in transactions_df.iterrows():
            user_idx = user_idx_map[row['customer_id']]
            product_idx = product_idx_map[row['product_id']]
            user_item_data[user_idx, product_idx] += row['quantity']
        
        self.user_item_matrix = csr_matrix(user_item_data)
        
        # Train KNN model on item-item similarity
        # Transpose to get item-user matrix for item-based CF
        item_user_matrix = self.user_item_matrix.T
        
        self.knn_model = NearestNeighbors(
            metric='cosine',
            algorithm='brute',
            n_neighbors=min(20, n_products),
            n_jobs=num_threads if num_threads > 0 else -1
        )
        
        self.knn_model.fit(item_user_matrix)
        
        print(f"Trained KNN model with {n_users} users and {n_products} products")
    
    def _train_content_based(self, products_df: pd.DataFrame):
        """Train TF-IDF content-based model."""
        # Create product descriptions from metadata
        products_df['description'] = (
            products_df['name'] + ' ' +
            products_df['category'] + ' ' +
            products_df['subcategory']
        )
        
        # Train TF-IDF vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            products_df['description']
        )
    
    def predict(
        self,
        customer_id: int,
        top_k: int = 5,
        collaborative_weight: float = 0.7,
        content_weight: float = 0.3
    ) -> List[Dict]:
        """
        Generate product recommendations for a customer.
        
        Args:
            customer_id: Customer ID
            top_k: Number of recommendations to return
            collaborative_weight: Weight for collaborative filtering score
            content_weight: Weight for content-based score
        
        Returns:
            List of recommended products with scores
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Get collaborative filtering scores
        collab_scores = self._get_collaborative_scores(customer_id)
        
        # Get content-based scores (based on customer's preferred category)
        content_scores = self._get_content_scores(customer_id)
        
        # Combine scores
        combined_scores = {}
        all_products = set(collab_scores.keys()) | set(content_scores.keys())
        
        for product_id in all_products:
            collab_score = collab_scores.get(product_id, 0.0)
            content_score = content_scores.get(product_id, 0.0)
            combined_scores[product_id] = (
                collaborative_weight * collab_score +
                content_weight * content_score
            )
        
        # Sort and get top-k
        sorted_products = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Format recommendations
        recommendations = []
        for product_id, score in sorted_products:
            product = self.products_df[
                self.products_df['product_id'] == product_id
            ].iloc[0]
            
            recommendations.append({
                'product_id': int(product_id),
                'name': product['name'],
                'category': product['category'],
                'subcategory': product['subcategory'],
                'price': float(product['price']),
                'score': float(score)
            })
        
        return recommendations
    
    def _get_collaborative_scores(self, customer_id: int) -> Dict[int, float]:
        """Get collaborative filtering scores for all products using KNN."""
        scores = {}
        
        # Check if customer exists in training data
        if customer_id not in self.user_ids:
            # Cold start: return empty scores
            return scores
        
        user_idx = self.user_ids.index(customer_id)
        user_interactions = self.user_item_matrix[user_idx].toarray().flatten()
        
        # Get products the user has interacted with
        interacted_product_indices = np.where(user_interactions > 0)[0]
        
        if len(interacted_product_indices) == 0:
            return scores
        
        # For each product the user interacted with, find similar products
        all_scores = np.zeros(len(self.product_ids))
        
        for product_idx in interacted_product_indices:
            # Get similar products
            distances, indices = self.knn_model.kneighbors(
                self.user_item_matrix.T[product_idx],
                n_neighbors=min(20, len(self.product_ids))
            )
            
            # Add similarity scores (convert distance to similarity)
            for dist, idx in zip(distances[0], indices[0]):
                if idx != product_idx:  # Don't recommend same product
                    similarity = 1 - dist  # Convert distance to similarity
                    all_scores[idx] += similarity * user_interactions[product_idx]
        
        # Normalize scores
        if all_scores.max() > 0:
            all_scores = all_scores / all_scores.max()
        
        # Convert to dictionary
        for idx, score in enumerate(all_scores):
            if score > 0:
                product_id = self.product_ids[idx]
                scores[product_id] = float(score)
        
        return scores
    
    def _get_content_scores(self, customer_id: int) -> Dict[int, float]:
        """Get content-based scores based on customer preferences."""
        scores = {}
        
        # Get customer's preferred category
        customer = self.customers_df[
            self.customers_df['customer_id'] == customer_id
        ]
        
        if len(customer) == 0:
            return scores
        
        preferred_category = customer.iloc[0]['preferred_category']
        
        # Give higher scores to products in preferred category
        for _, product in self.products_df.iterrows():
            if product['category'] == preferred_category:
                scores[product['product_id']] = 1.0
            else:
                scores[product['product_id']] = 0.3
        
        return scores
    
    def save(self, filepath: Path):
        """Save the trained model to disk."""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        model_data = {
            'knn_model': self.knn_model,
            'user_item_matrix': self.user_item_matrix,
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'products_df': self.products_df,
            'customers_df': self.customers_df,
            'transactions_df': self.transactions_df,
            'user_ids': self.user_ids,
            'product_ids': self.product_ids,
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
        model.knn_model = model_data['knn_model']
        model.user_item_matrix = model_data['user_item_matrix']
        model.tfidf_vectorizer = model_data['tfidf_vectorizer']
        model.tfidf_matrix = model_data['tfidf_matrix']
        model.products_df = model_data['products_df']
        model.customers_df = model_data['customers_df']
        model.transactions_df = model_data['transactions_df']
        model.user_ids = model_data['user_ids']
        model.product_ids = model_data['product_ids']
        model.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
        return model
