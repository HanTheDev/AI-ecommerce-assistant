import pandas as pd
import torch
from sqlalchemy import create_engine
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
    
    # Get user-item interactions from orders
    query = """
    SELECT user_id, product_id, COUNT(*) as interaction_count 
    FROM orders 
    GROUP BY user_id, product_id
    """
    df = pd.read_sql(query, engine)
    
    # Convert to tensors
    users = torch.tensor(df.user_id.values, dtype=torch.long)
    items = torch.tensor(df.product_id.values, dtype=torch.long)
    
    return users, items