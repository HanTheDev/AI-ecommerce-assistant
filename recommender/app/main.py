from fastapi import FastAPI, HTTPException
from typing import List
import torch
import os
from dotenv import load_dotenv
from .models.collaborative import CollaborativeFilter
from .utils.initialize_model import initialize_models

load_dotenv()

app = FastAPI()
model = None

@app.on_event("startup")
async def load_model():
    global model
    try:
        initialize_models()
        
        model_path = os.getenv("MODEL_PATH", "./data/model_artifacts/collaborative_model.pt")
        model = CollaborativeFilter.load_pretrained(model_path)
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise RuntimeError("Failed to load recommendation model")

@app.get("/recommendations/similar/{product_id}")
async def get_similar_products(product_id: int) -> List[int]:
    """Get similar products based on collaborative filtering"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    try:
        similar_products = model.get_similar_items(product_id)
        return similar_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/user/{user_id}")
async def get_user_recommendations(user_id: int) -> List[int]:
    """Get personalized recommendations for a user"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    try:
        recommendations = model.get_user_recommendations(user_id)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))