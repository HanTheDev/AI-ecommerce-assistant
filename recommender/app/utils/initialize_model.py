import torch
from models.collaborative import CollaborativeFilter
from utils.data_preprocess import preprocess_data
import os

def initialize_models():
    """Initialize and save models if they don't exist"""
    model_path = "./data/model_artifacts/collaborative_model.pt"
    
    # Skip if model already exists
    if os.path.exists(model_path):
        return
        
    # Create model artifacts directory
    os.makedirs("./data/model_artifacts", exist_ok=True)
    
    # Get data dimensions
    users, items = preprocess_data()
    n_users = users.max().item() + 1
    n_items = items.max().item() + 1
    
    # Initialize model
    model = CollaborativeFilter(n_users, n_items)
    
    # Save initial model
    torch.save(model.state_dict(), model_path)

if __name__ == "__main__":
    initialize_models()