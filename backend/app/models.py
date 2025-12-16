from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)  # Changed from Integer
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("Order", back_populates="user")
    product_views = relationship("ProductView", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String, index=True)  # NEW: Add category
    image_url = Column(String)  # NEW: Add image URL
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    views = relationship("ProductView", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

    # Add index for full-text search (PostgreSQL specific)
    __table_args__ = (
        Index('ix_products_name_description', 'name', 'description', postgresql_using='gin',
              postgresql_ops={'name': 'gin_trgm_ops', 'description': 'gin_trgm_ops'}),
    )

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(String, default="cart", index=True)  # Values: "cart", "pending", "completed", "cancelled"
    total_amount = Column(Float, default=0.0)  # NEW: Store total
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("CartItem", back_populates="order", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    quantity = Column(Integer, default=1)
    price_at_purchase = Column(Float)  # NEW: Store price at time of purchase

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

class ProductView(Base):
    __tablename__ = "product_views"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    viewed_at = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String, index=True)  # NEW: Track anonymous users

    product = relationship("Product", back_populates="views")
    user = relationship("User", back_populates="product_views")

class UserPreference(Base):
    """NEW: Store user preferences for personalization"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    preferred_categories = Column(Text)  # JSON string of categories
    price_range_min = Column(Float)
    price_range_max = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)