import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Optional
import logging
import pickle
import os

logger = logging.getLogger(__name__)

class ContentBasedModel:
    """
    Content-based filtering using sentence transformers and FAISS
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.product_ids = []
        self.embeddings = None
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
    def prepare_product_texts(self, db_session) -> List[tuple]:
        """
        Extract product information from database
        Returns: List of (product_id, text)
        """
        from sqlalchemy import text
        
        query = text("""
            SELECT id, name, description, category
            FROM products
            WHERE stock > 0
            ORDER BY id
        """)
        
        results = db_session.execute(query).fetchall()
        
        if not results:
            logger.warning("No products found")
            return []
        
        # Combine name, description, and category into searchable text
        product_texts = []
        for product_id, name, description, category in results:
            text_parts = [name]
            if description:
                text_parts.append(description)
            if category:
                text_parts.append(f"Category: {category}")
            
            combined_text = " ".join(text_parts)
            product_texts.append((product_id, combined_text))
        
        logger.info(f"Prepared {len(product_texts)} product texts")
        return product_texts
    
    def fit(self, db_session):
        """Train the content-based model"""
        logger.info("Training content-based model...")
        
        # Get product texts
        product_data = self.prepare_product_texts(db_session)
        
        if not product_data:
            logger.warning("No products to encode")
            return
        
        self.product_ids = [pid for pid, _ in product_data]
        texts = [text for _, text in product_data]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        self.embeddings = self.encoder.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Build FAISS index for fast similarity search
        logger.info("Building FAISS index...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        logger.info(f"Model trained with {len(self.product_ids)} products")
    
    def get_similar_products(self, product_id: int, top_k: int = 5) -> List[Dict]:
        """
        Find similar products using FAISS
        """
        if self.index is None or not self.product_ids:
            logger.warning("Model not trained yet")
            return []
        
        try:
            product_idx = self.product_ids.index(product_id)
        except ValueError:
            logger.warning(f"Product {product_id} not in index")
            return []
        
        # Get embedding for this product
        query_embedding = self.embeddings[product_idx:product_idx+1].astype('float32')
        
        # Search FAISS index (k+1 because first result is the query itself)
        distances, indices = self.index.search(query_embedding, top_k + 1)
        
        # Skip first result (the query product itself)
        recommendations = []
        for idx, distance in zip(indices[0][1:], distances[0][1:]):
            if idx < len(self.product_ids):  # Safety check
                recommendations.append({
                    "product_id": self.product_ids[idx],
                    "similarity_score": float(1 / (1 + distance))  # Convert distance to similarity
                })
        
        return recommendations
    
    def search_products(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Semantic search for products matching a text query
        """
        if self.index is None:
            logger.warning("Model not trained yet")
            return []
        
        # Encode query
        query_embedding = self.encoder.encode([query], convert_to_numpy=True).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.product_ids):
                results.append({
                    "product_id": self.product_ids[idx],
                    "relevance_score": float(1 / (1 + distance))
                })
        
        return results
    
    def save(self, path: str):
        """Save model to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        if self.index:
            faiss.write_index(self.index, os.path.join(path, "faiss.index"))
        
        # Save metadata
        with open(os.path.join(path, "metadata.pkl"), 'wb') as f:
            pickle.dump({
                'product_ids': self.product_ids,
                'embeddings': self.embeddings,
                'dimension': self.dimension
            }, f)
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk"""
        # Load FAISS index
        index_path = os.path.join(path, "faiss.index")
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
        
        # Load metadata
        metadata_path = os.path.join(path, "metadata.pkl")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.product_ids = data['product_ids']
                self.embeddings = data['embeddings']
                self.dimension = data['dimension']
        
        logger.info(f"Model loaded from {path}")

# Global model instance
cb_model = ContentBasedModel()