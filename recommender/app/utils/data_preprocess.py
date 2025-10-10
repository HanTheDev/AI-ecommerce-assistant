import pandas as pd
import torch
from sqlalchemy import create_engine, text
from typing import Tuple

def preprocess_data() -> Tuple[torch.tensor, torch.tensor]:
    """
    Load and preprocess data from database for the collaborative filter
    Returns:
        Tuple of (user_tensor, item_tensor)
    """
    # Load data from database
    DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"
    engine = create_engine(DATABASE_URL)
    
    # Query to get user-item interactions from orders and cart_items
    query = text("""
        SELECT o.user_id, ci.product_id, COUNT(*) as interaction_count 
        FROM orders o
        JOIN cart_items ci ON o.id = ci.order_id
        WHERE o.status = 'completed'  -- Only consider completed orders
        GROUP BY o.user_id, ci.product_id
    """)
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            
            if df.empty:
                print("Warning: No interactions found in database")
                # Return minimal tensors to allow model initialization
                return torch.tensor([0]), torch.tensor([0])
            
            # Convert to tensors
            users = torch.tensor(df.user_id.values, dtype=torch.long)
            items = torch.tensor(df.product_id.values, dtype=torch.long)
            
            print(f"Loaded {len(df)} interactions for {len(df.user_id.unique())} users and {len(df.product_id.unique())} products")
            
            return users, items
            
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        # Return minimal tensors in case of error
        return torch.tensor([0]), torch.tensor([0])