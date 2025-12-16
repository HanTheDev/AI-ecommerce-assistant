from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_admin: bool  # Changed from int
    created_at: datetime

    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: Optional[str] = None
    image_url: Optional[str] = None
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('stock')
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stock must be non-negative')
        return v

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
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Product
    price_at_purchase: Optional[float] = None

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
    status: str
    total_amount: float
    created_at: datetime
    items: List[CartItemResponse]

    class Config:
        orm_mode = True

# Update forward references
CartItemResponse.update_forward_refs()
CartResponse.update_forward_refs()
OrderResponse.update_forward_refs()