from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models.collaborative_filtering import cf_model
from app.models.content_based import cb_model

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Model training lock
is_training = False

async def train_models_background(db: Session):
    """Background task to train models"""
    global is_training
    
    if is_training:
        logger.info("Training already in progress")
        return
    
    try:
        is_training = True
        logger.info("Starting background model training...")
        
        # Train collaborative filtering
        cf_model.fit(db)
        
        # Train content-based
        cb_model.fit(db)
        
        # Save content-based model
        cb_model.save("/app/models/artifacts")
        
        logger.info("Background training completed")
    except Exception as e:
        logger.error(f"Error training models: {e}")
    finally:
        is_training = False

@router.post("/train")
async def trigger_training(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger model training
    (In production, this would be a scheduled job)
    """
    if is_training:
        return {"status": "training_in_progress"}
    
    background_tasks.add_task(train_models_background, db)
    return {"status": "training_started"}

@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: int,
    top_k: int = 5,
    method: str = "hybrid",  # "collaborative", "content", or "hybrid"
    db: Session = Depends(get_db)
):
    """
    Get products similar to the given product
    """
    # Check if models need training
    if cf_model.needs_retraining():
        logger.info("Models need retraining, training now...")
        cf_model.fit(db)
        cb_model.fit(db)
    
    if method == "collaborative":
        recommendations = cf_model.get_similar_products(product_id, top_k)
    elif method == "content":
        recommendations = cb_model.get_similar_products(product_id, top_k)
    elif method == "hybrid":
        # Combine both methods
        cf_recs = cf_model.get_similar_products(product_id, top_k * 2)
        cb_recs = cb_model.get_similar_products(product_id, top_k * 2)
        
        # Merge and re-rank
        combined = {}
        for rec in cf_recs:
            pid = rec["product_id"]
            combined[pid] = combined.get(pid, 0) + rec.get("similarity_score", 0) * 0.6
        
        for rec in cb_recs:
            pid = rec["product_id"]
            combined[pid] = combined.get(pid, 0) + rec.get("similarity_score", 0) * 0.4
        
        # Sort by combined score
        recommendations = [
            {"product_id": pid, "score": score}
            for pid, score in sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
        ]
    else:
        raise HTTPException(status_code=400, detail="Invalid method")
    
    return {
        "product_id": product_id,
        "recommendations": recommendations,
        "method": method
    }

@router.get("/user/{user_id}")
async def get_user_recommendations(
    user_id: int,
    top_k: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for a user
    """
    # Check if model needs training
    if cf_model.needs_retraining():
        logger.info("Model needs retraining, training now...")
        cf_model.fit(db)
    
    recommendations = cf_model.get_user_recommendations(user_id, top_k)
    
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@router.get("/search")
async def semantic_search(
    query: str,
    top_k: int = 10,
    db: Session = Depends(get_db)
):
    """
    Semantic search for products
    Example: "affordable wireless headphones"
    """
    # Ensure content-based model is trained
    if cb_model.index is None:
        cb_model.fit(db)
    
    results = cb_model.search_products(query, top_k)
    
    return {
        "query": query,
        "results": results
    }

@router.get("/status")
async def get_status():
    """Get model status"""
    return {
        "collaborative_filtering": {
            "trained": cf_model.item_similarity_matrix is not None,
            "num_products": len(cf_model.product_ids),
            "num_users": len(cf_model.user_ids),
            "last_trained": cf_model.last_trained.isoformat() if cf_model.last_trained else None,
            "needs_retraining": cf_model.needs_retraining()
        },
        "content_based": {
            "trained": cb_model.index is not None,
            "num_products": len(cb_model.product_ids)
        },
        "is_training": is_training
    }