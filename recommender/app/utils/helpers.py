import pandas as pd
from sqlalchemy import create_engine
import os

def get_db_connection():
    """Get SQLAlchemy database connection"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    return create_engine(DATABASE_URL)

def load_product_data():
    """Load product data from database"""
    engine = get_db_connection()
    query = "SELECT * FROM products"
    return pd.read_sql(query, engine)

def load_user_interactions():
    """Load user interaction data from database"""
    engine = get_db_connection()
    query = """
    SELECT user_id, product_id, 
           COUNT(*) as interaction_count 
    FROM orders 
    GROUP BY user_id, product_id
    """
    return pd.read_sql(query, engine)