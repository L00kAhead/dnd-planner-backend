from app.auth import get_password_hash
from app.database import SessionLocal
from app.models import User
import os

def seed_admin_user():
    """
    Seed an admin user in the database.

    This function retrieves the admin credentials (email and password) from environment variables.
    It checks if an admin user already exists in the database. If not, it creates one with the given
    credentials.

    Side Effects:
        - Adds a new admin user to the database if one does not exist.
        - Prints messages indicating the status of the operation.

    Raises:
        Exception: If a database error occurs during the operation.

    Returns:
        None
    """
    db = SessionLocal()
    admin_email = os.getenv("ADMIN")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        print("Error: ADMIN and ADMIN_PASSWORD environment variables must be set.")
        return

    try:
        # Check if the admin user already exists
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
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin_user()