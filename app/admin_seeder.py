from app.models import User
from app.auth import get_password_hash
from app.database import SessionLocal
import os
from dotenv import load_dotenv

load_dotenv()

def seed_admin_user():
    try:
        db = SessionLocal()
        admin_email = os.getenv("ADMIN")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_email or not admin_password:
            raise ValueError("ADMIN and ADMIN_PASSWORD environment variables must be set.")

        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            hashed_password = get_password_hash(admin_password)
            admin_user = User(
                email=admin_email,
                username="admin",
                hashed_password=hashed_password,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Error seeding admin user: {e}")
    finally:
        db.close()