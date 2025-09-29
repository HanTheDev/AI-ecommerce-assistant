import os
from sqlalchemy.orm import Session
from app import models
from app.auth import hash_password

def seed_admin(db: Session):
    """Ensure at least one admin user exists (from ENV)."""
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        print("⚠️ ERROR: ADMIN_EMAIL and ADMIN_PASSWORD environment variables must be set")
        return

    try:
        existing_admin = db.query(models.User).filter_by(email=admin_email).first()
        if not existing_admin:
            new_admin = models.User(
                email=admin_email,
                hashed_password=hash_password(admin_password),
                is_admin=1  # Explicitly set to 1
            )
            db.add(new_admin)
            db.commit()
            print(f"✅ Admin user created successfully: {admin_email}")
        else:
            # Ensure existing user is admin
            if not existing_admin.is_admin:
                existing_admin.is_admin = 1
                db.commit()
                print(f"✅ Existing user {admin_email} upgraded to admin")
            else:
                print(f"ℹ️ Admin user already exists: {admin_email}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")