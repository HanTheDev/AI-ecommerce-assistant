from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app import models, schemas
from app.database import get_db
from app.auth import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.deps import get_current_user
from app.utils import validate_password, validate_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Validate email
    email_valid, email_error = validate_email(user.email)
    if not email_valid:
        raise HTTPException(status_code=400, detail=email_error)
    
    # Validate password
    password_valid, password_error = validate_password(user.password)
    if not password_valid:
        raise HTTPException(status_code=400, detail=password_error)
    
    # Check if user exists
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        hashed = hash_password(user.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    new_user = models.User(email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "is_admin": db_user.is_admin
        }
    }

@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user