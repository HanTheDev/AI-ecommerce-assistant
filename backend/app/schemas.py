from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: int
    created_at: datetime

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: 'ProductInCart'

    class Config:
        orm_mode = True

class ProductInCart(Product):
    quantity: int = 0

    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    items: List[CartItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    items: List[CartItemResponse]

    class Config:
        orm_mode = True

CartItemResponse.update_forward_refs()
CartResponse.update_forward_refs()
OrderResponse.update_forward_refs()