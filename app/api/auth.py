from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas
from app.core.database import get_db
from app.core.auth import get_password_hash, verify_password, create_access_token, get_current_user, is_admin
from datetime import timedelta, datetime
from typing import List, Optional
from app.models.base import UserRole  # Import the UserRole enum
from sqlalchemy import text  # Add this import at the top

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with proper error handling."""
    try:
        # Check if user already exists
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Get password hash
        hashed_password = get_password_hash(user.password)
        
        # Check if the role is valid
        if user.role not in [role.value for role in models.UserRole]:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        # Special handling for recruiter and admin roles
        is_approved = True  # Default is approved
        if user.role in ["recruiter", "admin", "interviewer"]:
            # For special roles, require admin approval
            is_approved = False

        # Create user with role
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
            is_active=True,
            is_approved=is_approved
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate user
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token - role is now a string, not an enum
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},  # Use the string value directly
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=List[schemas.User])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    role: Optional[str] = None,  # Add role parameter
    current_user: schemas.User = Depends(is_admin), 
    db: Session = Depends(get_db)
):
    # Only admin can list all users
    query = db.query(models.User)
    
    # Filter by role if provided
    if role:
        query = query.filter(models.User.role == role)
        
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    return users

@router.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, current_user: schemas.User = Depends(is_admin), db: Session = Depends(get_db)):
    # Only admin can create users with special roles
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}/approve", response_model=schemas.User)
def approve_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(is_admin)):
    """Approve a user (admin only)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_approved = True
    db.commit()
    db.refresh(user)
    return user