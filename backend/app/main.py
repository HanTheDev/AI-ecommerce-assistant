from fastapi import FastAPI
from app.routers import auth, products

app = FastAPI(title="AI E-commerce Assistant API")
app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}