import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CollaborativeFilteringModel:
    """
    Item-based collaborative filtering using cosine similarity
    """
    
    def __init__(self):
        self.user_item_matrix = None
        self.item_similarity_matrix = None
        self.product_ids = []
        self.user_ids = []
        self.last_trained = None
        
    def prepare_data(self, db_session) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Extract user-product interaction data from database
        Returns: (user_item_matrix, product_ids, user_ids)
        """
        from sqlalchemy import text
        
        # Query to get user-product interactions (orders)
        query = text("""
            SELECT DISTINCT
                o.user_id,
                ci.product_id,
                SUM(ci.quantity) as interaction_strength
            FROM orders o
            JOIN cart_items ci ON o.id = ci.order_id
            WHERE o.status = 'completed'
            GROUP BY o.user_id, ci.product_id
            ORDER BY o.user_id, ci.product_id
        """)
        
        results = db_session.execute(query).fetchall()
        
        if not results:
            logger.warning("No order data found for training")
            return np.array([]), [], []
        
        # Extract unique users and products
        user_ids = sorted(list(set(row[0] for row in results)))
        product_ids = sorted(list(set(row[1] for row in results)))
        
        # Create user-item matrix
        user_item_matrix = np.zeros((len(user_ids), len(product_ids)))
        
        user_id_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        product_id_to_idx = {pid: idx for idx, pid in enumerate(product_ids)}
        
        for user_id, product_id, strength in results:
            user_idx = user_id_to_idx[user_id]
            product_idx = product_id_to_idx[product_id]
            user_item_matrix[user_idx, product_idx] = strength
        
        logger.info(f"Prepared matrix: {len(user_ids)} users × {len(product_ids)} products")
        return user_item_matrix, product_ids, user_ids
    
    def fit(self, db_session):
        """Train the collaborative filtering model"""
        logger.info("Training collaborative filtering model...")
        
        # Prepare data
        self.user_item_matrix, self.product_ids, self.user_ids = self.prepare_data(db_session)
        
        if len(self.product_ids) == 0:
            logger.warning("No products to train on")
            return
        
        # Calculate item-item similarity matrix
        # Transpose to get item-user matrix, then calculate cosine similarity
        item_user_matrix = self.user_item_matrix.T
        self.item_similarity_matrix = cosine_similarity(item_user_matrix)
        
        # Set diagonal to 0 (a product is not similar to itself)
        np.fill_diagonal(self.item_similarity_matrix, 0)
        
        self.last_trained = datetime.utcnow()
        logger.info(f"Model trained successfully at {self.last_trained}")
    
    def get_similar_products(self, product_id: int, top_k: int = 5) -> List[Dict]:
        """
        Get K most similar products to a given product
        Returns: List of {product_id, similarity_score}
        """
        if self.item_similarity_matrix is None:
            logger.warning("Model not trained yet")
            return []
        
        try:
            product_idx = self.product_ids.index(product_id)
        except ValueError:
            logger.warning(f"Product {product_id} not found in training data")
            return []
        
        # Get similarity scores for this product
        similarities = self.item_similarity_matrix[product_idx]
        
        # Get top K similar products (excluding itself)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        recommendations = [
            {
                "product_id": self.product_ids[idx],
                "similarity_score": float(similarities[idx])
            }
            for idx in top_indices
            if similarities[idx] > 0  # Only include positive similarities
        ]
        
        return recommendations
    
    def get_user_recommendations(self, user_id: int, top_k: int = 10, exclude_purchased: bool = True) -> List[Dict]:
        """
        Get personalized recommendations for a user
        Based on products similar to what they've already purchased
        """
        if self.user_item_matrix is None:
            logger.warning("Model not trained yet")
            return []
        
        try:
            user_idx = self.user_ids.index(user_id)
        except ValueError:
            logger.warning(f"User {user_id} not found in training data")
            return []
        
        # Get user's purchase history
        user_purchases = self.user_item_matrix[user_idx]
        
        # Calculate scores for all products
        # Score = sum of (similarity to purchased products * purchase strength)
        scores = np.dot(self.item_similarity_matrix, user_purchases)
        
        # Exclude already purchased products if requested
        if exclude_purchased:
            scores = scores * (user_purchases == 0)
        
        # Get top K products
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        recommendations = [
            {
                "product_id": self.product_ids[idx],
                "recommendation_score": float(scores[idx])
            }
            for idx in top_indices
            if scores[idx] > 0
        ]
        
        return recommendations
    
    def needs_retraining(self, max_age_hours: int = 24) -> bool:
        """Check if model needs retraining"""
        if self.last_trained is None:
            return True
        age = datetime.utcnow() - self.last_trained
        return age > timedelta(hours=max_age_hours)

# Global model instance
cf_model = CollaborativeFilteringModel()