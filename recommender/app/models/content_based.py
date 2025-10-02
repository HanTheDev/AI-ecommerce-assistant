from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import pickle
import os

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.similarity_matrix = None
        self.product_indices = None
        
    def fit(self, products_df):
        """Train the recommender on product descriptions"""
        # Combine relevant text fields
        text_data = products_df['description'].fillna('') + ' ' + products_df['name'].fillna('')
        
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(text_data)
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        self.product_indices = products_df.index
        
    def get_recommendations(self, product_id, n_recommendations=5):
        """Get n similar products for a given product ID"""
        try:
            idx = self.product_indices.get_loc(product_id)
            sim_scores = list(enumerate(self.similarity_matrix[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:n_recommendations+1]  # Exclude the product itself
            product_indices = [i[0] for i in sim_scores]
            return [self.product_indices[i] for i in product_indices]
        except:
            return []
            
    def save_model(self, filepath):
        """Save model artifacts"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'vectorizer': self.vectorizer,
                'similarity_matrix': self.similarity_matrix,
                'product_indices': self.product_indices
            }, f)
            
    def load_model(self, filepath):
        """Load model artifacts"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.similarity_matrix = data['similarity_matrix']
            self.product_indices = data['product_indices']