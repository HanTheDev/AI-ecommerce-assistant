from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[schemas.Product])
def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=schemas.Product, responses={404: {"description": "Product not found"}})
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=schemas.Product, responses={403: {"description": "Not authorized"}})
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.put("/{product_id}", response_model=schemas.Product, responses={403: {"description": "Not authorized"}, 404: {"description": "Product not found"}})
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", responses={403: {"description": "Not authorized"}, 404: {"description": "Product not found"}})
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"detail": "Product deleted"}