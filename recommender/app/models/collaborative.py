import torch
import torch.nn as nn

class CollaborativeFilter(nn.Module):
    def __init__(self, n_users, n_items, n_factors=50):
        super().__init__()
        self.user_factors = nn.Embedding(n_users, n_factors)
        self.item_factors = nn.Embedding(n_items, n_factors)
        
    def forward(self, user, item):
        return (self.user_factors(user) * self.item_factors(item)).sum(1)
    
    def get_similar_items(self, item_id, n=5):
        with torch.no_grad():
            item_embedding = self.item_factors.weight[item_id]
            similarities = torch.cosine_similarity(
                item_embedding.unsqueeze(0),
                self.item_factors.weight
            )
            _, indices = similarities.topk(n + 1)
            return indices[1:].tolist()  # Exclude the item itself