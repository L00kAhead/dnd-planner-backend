from http.client import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, auth
from app.database import get_db
from app.models import party_invites, party_attendees

router = APIRouter()

@router.put("/me", response_model=schemas.User)
def update_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Update the authenticated user's profile.

    This endpoint allows the currently authenticated user to update their
    profile details, such as username, email, or password.

    Args:
        user_update (schemas.UserUpdate): The fields to update in the user's profile.
        db (Session): The database session dependency for querying and updating data.
        current_user (models.User): The currently authenticated user making the request.

    Returns:
        schemas.User: The updated user profile with the latest details.

    Raises:
        HTTPException: Raised if there are any issues with the update process or authentication.
    """
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = auth.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me", response_model=schemas.User)
def get_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Retrieve the details of the currently authenticated user.

    This endpoint provides the profile information of the user currently
    authenticated via the bearer token.

    Args:
        db (Session): The database session dependency.
        current_user (models.User): The currently authenticated user making the request.

    Returns:
        schemas.User: The details of the authenticated user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Retrieve user details by user ID.

    This endpoint allows the retrieval of user details based on their ID.
    It is accessible to admins or the user themselves.

    Args:
        user_id (int): The ID of the user whose details are being retrieved.
        db (Session): The database session dependency.
        current_user (models.User): The currently authenticated user making the request.

    Returns:
        schemas.User: The details of the requested user.

    Raises:
        HTTPException:
            - 404: If the user with the specified ID does not exist.
            - 403: If the authenticated user is not authorized to view the details.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the current user is the requested user or an admin
    if current_user.id != user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Unauthorized to view this user's details")
    
    return user


@router.delete("/me")
def delete_user_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Deactivate or delete the authenticated user's account.

    This endpoint allows the currently authenticated user to delete their account
    from the system. The operation is irreversible.

    Args:
        db (Session): The database session dependency for querying and deleting data.
        current_user (models.User): The currently authenticated user making the request.

    Returns:
        dict: A confirmation message indicating that the account was successfully deleted.
    """
    # Delete related party data
    db.execute(party_invites.delete().where(party_invites.c.user_id == current_user.id))
    db.execute(party_attendees.delete().where(party_attendees.c.user_id == current_user.id))
    db.execute(models.Party.__table__.delete().where(models.Party.creator_id == current_user.id))

    # Delete the user
    db.delete(current_user)
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return {"message": "Account and all related data deleted successfully"}

# Invites 

@router.get("/me/invites", response_model=List[schemas.Invite])
def list_user_invites(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Retrieve all invites for the currently authenticated user.
    
    Args:
        db (Session): The database session dependency.
        current_user (models.User): The currently authenticated user.

    Returns:
        List[schemas.Invite]: A list of invites with their statuses.
    """
    invites = db.execute(
        party_invites.select().where(party_invites.c.user_id == current_user.id)
    ).fetchall()
    return [
        {"party_id": invite.party_id, "status": invite.status}
        for invite in invites
    ]