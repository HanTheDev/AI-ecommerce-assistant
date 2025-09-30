from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, products, orders
from app.database import SessionLocal, engine, Base
from app.startup import seed_admin   # 👈 import seeder
from dotenv import load_dotenv

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI E-commerce Assistant API")

# Allow your frontend origin
origins = [
    "http://localhost:5174",  # React dev server
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.on_event("startup")   # 👈 run when container starts
def run_seed():
    db = SessionLocal()
    seed_admin(db)
    db.close()

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}