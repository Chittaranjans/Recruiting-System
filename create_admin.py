from app.core.database import SessionLocal
from app.models.base import User
from app.core.auth import get_password_hash
from datetime import datetime

def create_admin_user(username, email, password):
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            print(f"User {username} already exists with role: {existing_user.role}")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role="admin",  # Set role directly as admin
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        print(f"Admin user '{username}' created successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Replace with your desired admin credentials
    create_admin_user(
        username="admin", 
        email="admin@example.com", 
        password="adminpassword"
    )