from fastapi import FastAPI
from app.routers import auth, products
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI E-commerce Assistant API")

# Allow your frontend origin
origins = [
    "http://localhost:5174",  # React dev server
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}