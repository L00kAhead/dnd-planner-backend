from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas, auth
from app.database import get_db

router = APIRouter()

@router.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint for user registration (signup).
    
    Args:
        user (schemas.UserCreate): The user details for creating an account, including email, username, and password.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        schemas.User: The newly created user object with details such as email and username.

    Raises:
        HTTPException: If the email is already registered, raises a 400 status error.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint for user login.
    
    Args:
        email (str): The email of the user attempting to log in.
        password (str): The password of the user attempting to log in.
        db (Session, optional): SQLAlchemy database session dependency.

    Returns:
        dict: A dictionary containing the access token and its type.

    Raises:
        HTTPException: 
            - If the user does not exist, raises a 401 status error.
            - If the password is incorrect, raises a 401 status error.
    """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not auth.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}