from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, auth
from app.database import get_db
from app.schedular import PartyScheduler
from app.email_service import EmailService
from app.models import InviteStatus, party_invites, party_attendees

router = APIRouter()
email_service = EmailService()
party_scheduler = PartyScheduler()

@router.post("/", response_model=schemas.Party)
def create_party(
    party: schemas.PartyCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_party = models.Party(**party.dict(exclude={'invite_emails'}), creator_id=current_user.id)
    db.add(db_party)
    db.commit()
    db.refresh(db_party)
    
    # Schedule party reminder
    party_scheduler.schedule_party_reminder(db_party.id, db_party.date_time)
    
    # Send invites
    unique_emails = set(party.invite_emails)
    for email in unique_emails:
        invited_user = db.query(models.User).filter(models.User.email == email).first()
        if invited_user:
            db.execute(
                party_invites.insert().values(
                    user_id=invited_user.id,
                    party_id=db_party.id,
                    status=InviteStatus.PENDING
                )
            )
            background_tasks.add_task(
                email_service.send_email,
                email,
                f"Invitation to D&D Party: {party.title}",
                f"You've been invited to join {current_user.username}'s D&D party!"
            )
    
    db.commit()
    return db_party

@router.put("/{party_id}/respond-invite")
def respond_to_invite(
    party_id: int,
    accept: bool,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        # Retrieve the party
        party = db.query(models.Party).filter(models.Party.id == party_id).first()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")
        
        # Check for an invite
        invite = db.execute(
            party_invites.select()
            .where(party_invites.c.user_id == current_user.id)
            .where(party_invites.c.party_id == party_id)
        ).first()
        
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")
        
        # Update the invite status
        status = InviteStatus.ACCEPTED if accept else InviteStatus.DECLINED
        db.execute(
            party_invites.update()
            .where(party_invites.c.user_id == current_user.id)
            .where(party_invites.c.party_id == party_id)
            .values(status=status)
        )
        
        # Add user to attendees if accepted
        if accept:
            db.execute(
                party_attendees.insert().values(
                    user_id=current_user.id,
                    party_id=party_id
                )
            )
        
        # Notify the party creator
        try:
            background_tasks.add_task(
                email_service.send_email,
                party.creator.email,
                f"Response to Party Invitation",
                f"{current_user.username} has {status.name} your party invitation!"
            )
        except Exception as e:
            print(f"Failed to send email: {e}")
        
        db.commit()  # Commit only once at the end
        return {"message": f"Successfully {status.name} invitation"}
    
    except Exception as e:
        db.rollback()  # Rollback if any error occurs
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{party_id}")
def update_party(
    party_id: int,
    party_update: schemas.PartyUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    party = db.query(models.Party).filter(models.Party.id == party_id).first()
    if not party or party.creator_id != current_user.id:
        raise HTTPException(status_code=404, detail="Party not found or unauthorized")
    
    old_date_time = party.date_time
    
    # only update the changed fields
    for field, value in party_update.dict(exclude_unset=True).items():
        setattr(party, field, value)
    
    # If date_time was updated, reschedule the reminder
    if party_update.date_time and party_update.date_time != old_date_time:
        try:
            party_scheduler.remove_party_reminder(party_id)
            party_scheduler.schedule_party_reminder(party_id, party_update.date_time)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reschedule reminder: {e}")
    
    db.commit()
    db.refresh(party)
    return party


@router.delete("/{party_id}")
def delete_party(
    party_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Delete a party and all related data.

    This includes:
    - Removing all invites and attendees for the party.
    """
    party = db.query(models.Party).filter(models.Party.id == party_id, models.Party.creator_id == current_user.id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found or unauthorized")

    # Delete related data
    db.execute(party_invites.delete().where(party_invites.c.party_id == party_id))
    db.execute(party_attendees.delete().where(party_attendees.c.party_id == party_id))
    db.delete(party)

    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    return {"message": "Party and all related data deleted successfully"}


@router.get("/", response_model=List[schemas.Party])
def list_parties(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Party).all()



@router.post("/{party_id}/join-request")
def request_to_join(
    party_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    party = db.query(models.Party).filter(models.Party.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    
    db.execute(
        party_invites.insert().values(
            user_id=current_user.id,
            party_id=party_id,
            status=InviteStatus.PENDING
        )
    )

    # Check if the user has already requested to join
    existing_request = db.execute(
        party_invites.select()
        .where(party_invites.c.user_id == current_user.id)
        .where(party_invites.c.party_id == party_id)
    ).first()

    if existing_request:
        raise HTTPException(status_code=400, detail="You have already requested to join this party")
        
    # Notify party creator
    background_tasks.add_task(
        email_service.send_email,
        party.creator.email,
        f"New Join Request",
        f"{current_user.username} has requested to join your party!"
    )
    
    db.commit()
    return {"message": "Join request sent successfully"}

@router.delete("/{party_id}/attendees/{user_id}")
def remove_attendee(
    party_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    party = db.query(models.Party).filter(models.Party.id == party_id).first()
    if not party or party.creator_id != current_user.id:
        raise HTTPException(status_code=404, detail="Party not found or unauthorized")
    
    db.execute(
        party_attendees.delete()
        .where(party_attendees.c.user_id == user_id)
        .where(party_attendees.c.party_id == party_id)
    )
    db.commit()
    return {"message": "Attendee removed successfully"}