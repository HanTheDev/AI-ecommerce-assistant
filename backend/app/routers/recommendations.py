from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx

from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

RECOMMENDER_SERVICE_URL = "http://recommender:8000"  # Docker service name

@router.get("/similar/{product_id}", response_model=List[int])
async def get_similar_products(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get similar products based on collaborative filtering"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECOMMENDER_SERVICE_URL}/recommendations/similar/{product_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Recommender service unavailable")

@router.get("/user/{user_id}", response_model=List[int])
async def get_user_recommendations(
    user_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations for a user"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{RECOMMENDER_SERVICE_URL}/recommendations/user/{user_id}"
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail="Recommender service unavailable")