from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import recommendations
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Recommender Service",
    description="ML-powered product recommendation engine",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendations.router)

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("Starting Recommender Service...")
    # Models will be loaded lazily on first request

@app.get("/")
def root():
    return {
        "service": "Recommender Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "recommender"}