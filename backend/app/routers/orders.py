from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

# Cart endpoints
@router.post("/cart", response_model=schemas.CartResponse)
def add_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if product exists and has enough stock
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    # Check if there's an existing cart (unfulfilled order)
    cart = db.query(models.Order)\
        .filter(
            and_(
                models.Order.user_id == current_user.id,
                models.Order.status == "cart"
            )
        ).first()

    if not cart:
        # Create new cart
        cart = models.Order(user_id=current_user.id, status="cart")
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Check if product already in cart
    existing_item = db.query(models.CartItem)\
        .filter(
            and_(
                models.CartItem.order_id == cart.id,
                models.CartItem.product_id == item.product_id
            )
        ).first()

    if existing_item:
        existing_item.quantity += item.quantity
        cart_item = existing_item
    else:
        cart_item = models.CartItem(
            order_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart)

    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart.items)
    return {"items": cart.items, "total": total}

@router.get("/cart", response_model=schemas.CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cart = db.query(models.Order)\
        .filter(
            and_(
                models.Order.user_id == current_user.id,
                models.Order.status == "cart"
            )
        ).first()

    if not cart:
        return {"items": [], "total": 0.0}

    total = sum(item.product.price * item.quantity for item in cart.items)
    return {"items": cart.items, "total": total}

@router.delete("/cart/{item_id}")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cart = db.query(models.Order)\
        .filter(
            and_(
                models.Order.user_id == current_user.id,
                models.Order.status == "cart"
            )
        ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_item = db.query(models.CartItem)\
        .filter(
            and_(
                models.CartItem.order_id == cart.id,
                models.CartItem.id == item_id
            )
        ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    db.delete(cart_item)
    db.commit()
    return {"detail": "Item removed from cart"}

@router.post("/checkout", response_model=schemas.OrderResponse)
def checkout(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Get current cart
    cart = db.query(models.Order)\
        .filter(
            and_(
                models.Order.user_id == current_user.id,
                models.Order.status == "cart"
            )
        ).first()

    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Check stock availability and update stock
    for item in cart.items:
        product = item.product
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.name}"
            )
        product.stock -= item.quantity

    # Convert cart to order
    cart.status = "completed"
    db.commit()
    db.refresh(cart)
    return cart


@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    orders = db.query(models.Order).filter(models.Order.user_id == current_user.id).all()
    return orders
