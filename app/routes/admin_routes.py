from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[schemas.User])
def list_users(
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_admin_user)  # Admin access required
):
    """
    Admin-only route to list all users.
    """
    return db.query(models.User).all()

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(auth.get_admin_user)  # Admin access required
):
    """
    Admin-only route to delete a user by ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}