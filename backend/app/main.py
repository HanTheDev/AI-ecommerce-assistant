from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, products, orders, recommendations
from app.database import SessionLocal, engine, Base
from app.startup import seed_admin
from dotenv import load_dotenv
import os

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI E-commerce Assistant API",
    description="Backend API for AI-powered e-commerce platform",
    version="1.0.0"
)

# CORS configuration from environment
origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if not origins or origins == [""]:
    # Default for development
    origins = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(recommendations.router)

@app.on_event("startup")
def run_seed():
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "message": "AI E-commerce API is running 🚀",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "backend"}