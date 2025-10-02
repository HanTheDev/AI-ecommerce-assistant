import torch
from torch import optim
import os
from models.collaborative import CollaborativeFilter
from .data_preprocess import preprocess_data

def train_model():
    # Get data
    users, items = preprocess_data()
    
    # Initialize model
    n_users = users.max() + 1
    n_items = items.max() + 1
    model = CollaborativeFilter(n_users, n_items)
    
    # Training parameters
    criterion = torch.nn.MSELoss()
    optimizer = optim.Adam(model.parameters())
    
    # Training loop
    n_epochs = 10
    for epoch in range(n_epochs):
        optimizer.zero_grad()
        outputs = model(users, items)
        loss = criterion(outputs, torch.ones_like(outputs))  # Assuming positive interactions
        loss.backward()
        optimizer.step()
        print(f'Epoch {epoch}: loss = {loss.item():.4f}')
    
    # Save model
    os.makedirs("./data/model_artifacts", exist_ok=True)
    torch.save(model.state_dict(), "./data/model_artifacts/collaborative_model.pt")

if __name__ == "__main__":
    train_model()