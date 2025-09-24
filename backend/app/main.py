from fastapi import FastAPI

app = FastAPI(title="AI E-commerce Assistant API")

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}