"""add category and preferences

Revision ID: xxxxx
Revises: 0731d723e3ea
Create Date: 2025-xx-xx

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'xxxxx'
down_revision: Union[str, None] = '0731d723e3ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add new columns to existing tables
    op.add_column('products', sa.Column('category', sa.String(), nullable=True))
    op.add_column('products', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('products', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    op.add_column('orders', sa.Column('total_amount', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('orders', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    op.add_column('cart_items', sa.Column('price_at_purchase', sa.Float(), nullable=True))
    
    op.add_column('product_views', sa.Column('session_id', sa.String(), nullable=True))
    
    # Create indexes
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])
    op.create_index('ix_cart_items_order_id', 'cart_items', ['order_id'])
    op.create_index('ix_cart_items_product_id', 'cart_items', ['product_id'])
    op.create_index('ix_product_views_user_id', 'product_views', ['user_id'])
    op.create_index('ix_product_views_product_id', 'product_views', ['product_id'])
    op.create_index('ix_product_views_viewed_at', 'product_views', ['viewed_at'])
    op.create_index('ix_product_views_session_id', 'product_views', ['session_id'])
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('preferred_categories', sa.Text(), nullable=True),
        sa.Column('price_range_min', sa.Float(), nullable=True),
        sa.Column('price_range_max', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)
    
    # Enable pg_trgm extension for full-text search (PostgreSQL)
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

def downgrade() -> None:
    op.drop_index('ix_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences')
    
    op.drop_index('ix_product_views_session_id', table_name='product_views')
    op.drop_index('ix_product_views_viewed_at', table_name='product_views')
    op.drop_index('ix_product_views_product_id', table_name='product_views')
    op.drop_index('ix_product_views_user_id', table_name='product_views')
    op.drop_index('ix_cart_items_product_id', table_name='cart_items')
    op.drop_index('ix_cart_items_order_id', table_name='cart_items')
    op.drop_index('ix_orders_status', table_name='orders')
    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_index('ix_products_category', table_name='products')
    
    op.drop_column('product_views', 'session_id')
    op.drop_column('cart_items', 'price_at_purchase')
    op.drop_column('orders', 'updated_at')
    op.drop_column('orders', 'total_amount')
    op.drop_column('users', 'updated_at')
    op.drop_column('products', 'updated_at')
    op.drop_column('products', 'image_url')
    op.drop_column('products', 'category')
    
    op.execute('DROP EXTENSION IF EXISTS pg_trgm')