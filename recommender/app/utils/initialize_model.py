import torch
from app.models.collaborative import CollaborativeFilter
from app.utils.data_preprocess import preprocess_data
import os
import time
from sqlalchemy.exc import OperationalError

def initialize_models():
    """Initialize and save models if they don't exist"""
    model_path = "./data/model_artifacts/collaborative_model.pt"
    
    # Skip if model already exists
    if os.path.exists(model_path):
        return
        
    # Create model artifacts directory
    os.makedirs("./data/model_artifacts", exist_ok=True)

    # Retry connection
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Get data dimensions
            users, items = preprocess_data()
            n_users = users.max().item() + 1
            n_items = items.max().item() + 1
            
            # Initialize model
            model = CollaborativeFilter(n_users, n_items)
            
            # Save initial model
            torch.save(model.state_dict(), model_path)
        except OperationalError:
            if attempt == max_retries - 1:
                raise
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    initialize_models()