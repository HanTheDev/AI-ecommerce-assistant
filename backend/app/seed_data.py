from sqlalchemy.orm import Session
from app import models
from app.auth import hash_password
from faker import Faker
import random

fake = Faker()

def seed_products(db: Session):
    """Create realistic product data"""
    
    categories = {
        "Electronics": [
            ("Laptop Pro 15\"", "High-performance laptop with 16GB RAM and 512GB SSD", 1299.99, 15),
            ("Wireless Mouse", "Ergonomic wireless mouse with precision tracking", 29.99, 100),
            ("Mechanical Keyboard", "RGB backlit mechanical gaming keyboard", 89.99, 50),
            ("USB-C Hub", "7-in-1 USB-C adapter with HDMI and ethernet", 49.99, 75),
            ("Wireless Headphones", "Noise-cancelling over-ear headphones", 199.99, 40),
            ("4K Webcam", "Professional webcam with auto-focus", 129.99, 30),
            ("External SSD 1TB", "Portable solid-state drive with USB 3.2", 149.99, 60),
            ("Smart Watch", "Fitness tracking smartwatch with heart rate monitor", 249.99, 25),
            ("Bluetooth Speaker", "Waterproof portable speaker with 12-hour battery", 79.99, 80),
            ("Phone Case", "Shockproof case with card holder", 19.99, 200),
        ],
        "Furniture": [
            ("Standing Desk", "Adjustable height electric standing desk", 399.99, 20),
            ("Office Chair", "Ergonomic mesh office chair with lumbar support", 299.99, 30),
            ("Desk Lamp", "LED desk lamp with touch control and USB port", 39.99, 50),
            ("Monitor Stand", "Wooden monitor riser with storage space", 34.99, 40),
            ("Bookshelf", "5-tier modern bookshelf", 89.99, 15),
            ("File Cabinet", "3-drawer lockable file cabinet", 149.99, 10),
            ("Desk Organizer", "Bamboo desk organizer set", 24.99, 60),
        ],
        "Home & Kitchen": [
            ("Coffee Maker", "Programmable coffee maker with thermal carafe", 79.99, 35),
            ("Blender", "High-power blender for smoothies", 59.99, 45),
            ("Air Fryer", "5-quart digital air fryer", 119.99, 25),
            ("Water Bottle", "Insulated stainless steel water bottle 32oz", 24.99, 150),
            ("Kitchen Knife Set", "Professional 8-piece knife set", 89.99, 30),
            ("Cutting Board", "Large bamboo cutting board", 29.99, 70),
        ],
        "Books": [
            ("Python Programming", "Complete guide to Python programming", 49.99, 50),
            ("Machine Learning Basics", "Introduction to ML algorithms", 59.99, 40),
            ("Web Development", "Modern web development with React", 44.99, 45),
            ("System Design", "Designing scalable systems", 54.99, 35),
        ],
        "Sports & Outdoors": [
            ("Yoga Mat", "Non-slip exercise yoga mat with carrying strap", 34.99, 80),
            ("Dumbbells Set", "Adjustable dumbbells 5-25 lbs", 149.99, 20),
            ("Resistance Bands", "Set of 5 resistance bands", 19.99, 100),
            ("Water Resistant Backpack", "35L hiking backpack", 69.99, 40),
            ("Camping Tent", "4-person waterproof tent", 199.99, 15),
        ]
    }
    
    products = []
    for category, items in categories.items():
        for name, desc, price, stock in items:
            product = models.Product(
                name=name,
                description=desc,
                price=price,
                stock=stock,
                category=category,
                image_url=f"https://via.placeholder.com/300x300?text={name.replace(' ', '+')}"
            )
            products.append(product)
            db.add(product)
    
    db.commit()
    print(f"✅ Created {len(products)} products")
    return products

def seed_users(db: Session, num_users=20):
    """Create demo users"""
    users = []
    for i in range(num_users):
        user = models.User(
            email=fake.email(),
            hashed_password=hash_password("DemoPassword123!"),
            is_admin=False
        )
        users.append(user)
        db.add(user)
    
    db.commit()
    print(f"✅ Created {num_users} demo users")
    return users

def seed_orders(db: Session, users, products, num_orders=50):
    """Create realistic order history"""
    for _ in range(num_orders):
        user = random.choice(users)
        order = models.Order(
            user_id=user.id,
            status="completed"
        )
        db.add(order)
        db.flush()
        
        # Add 1-5 random products to order
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)
        total = 0
        for product in selected_products:
            quantity = random.randint(1, 3)
            cart_item = models.CartItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price
            )
            db.add(cart_item)
            total += product.price * quantity
        
        order.total_amount = total
    
    db.commit()
    print(f"✅ Created {num_orders} demo orders")

def seed_product_views(db: Session, users, products, num_views=200):
    """Create product view history for recommendations"""
    for _ in range(num_views):
        user = random.choice(users)
        product = random.choice(products)
        
        view = models.ProductView(
            user_id=user.id,
            product_id=product.id
        )
        db.add(view)
    
    db.commit()
    print(f"✅ Created {num_views} product views")

def run_seed():
    """Run all seeders"""
    from app.database import SessionLocal
    db = SessionLocal()

    try:
        print("🌱 Starting database seeding...")
        
        # Create products
        products = seed_products(db)
        
        # Create users
        users = seed_users(db, num_users=20)
        
        # Create orders
        seed_orders(db, users, products, num_orders=50)
        
        # Create product views
        seed_product_views(db, users, products, num_views=200)
        
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()