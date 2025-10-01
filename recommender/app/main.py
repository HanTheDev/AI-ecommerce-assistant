from fastapi import FastAPI, Depends
from typing import List
import torch
import numpy as np
from .models.collaborative import CollaborativeFilter
from .utils.preprocessing import preprocess_data

app = FastAPI()
model = None

@app.on_event("startup")
async def load_model():
    global model
    model = CollaborativeFilter.load_pretrained("./data/model_artifacts/collaborative_model.pt")

@app.get("/recommendations/similar/{product_id}")
async def get_similar_products(product_id: int) -> List[int]:
    """Get similar products based on collaborative filtering"""
    similar_products = model.get_similar_items(product_id)
    return similar_products

@app.get("/recommendations/user/{user_id}")
async def get_user_recommendations(user_id: int) -> List[int]:
    """Get personalized recommendations for a user"""
    recommendations = model.get_user_recommendations(user_id)
    return recommendations