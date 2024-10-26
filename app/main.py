from app import models, schemas, auth
from app.schedular import PartyScheduler
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import engine
from datetime import timedelta
from app.email_service import EmailService
from app.models import party_invites, party_attendees
from app.database import get_db  

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
email_service = EmailService()
party_scheduler = PartyScheduler()

@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
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

@app.post("/login", response_model=schemas.Token)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.put("/users/me", response_model=schemas.User)
def update_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    if user_update.password:
        current_user.hashed_password = auth.get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/parties", response_model=schemas.Party)
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
    for email in party.invite_emails:
        invited_user = db.query(models.User).filter(models.User.email == email).first()
        if invited_user:
            db.execute(
                party_invites.insert().values(
                    user_id=invited_user.id,
                    party_id=db_party.id,
                    status='pending'
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

@app.put("/parties/{party_id}/respond-invite")
def respond_to_invite(
    party_id: int,
    accept: bool,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    party = db.query(models.Party).filter(models.Party.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    
    invite = db.execute(
        party_invites.select()
        .where(party_invites.c.user_id == current_user.id)
        .where(party_invites.c.party_id == party_id)
    ).first()
    
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    status = 'accepted' if accept else 'declined'
    db.execute(
        party_invites.update()
        .where(party_invites.c.user_id == current_user.id)
        .where(party_invites.c.party_id == party_id)
        .values(status=status)
    )
    
    if accept:
        db.execute(
            party_attendees.insert().values(
                user_id=current_user.id,
                party_id=party_id
            )
        )
    
    # Notify party creator
    background_tasks.add_task(
        email_service.send_email,
        party.creator.email,
        f"Response to Party Invitation",
        f"{current_user.username} has {status} your party invitation!"
    )
    
    db.commit()
    return {"message": f"Successfully {status} invitation"}

@app.put("/parties/{party_id}")
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
    
    for field, value in party_update.dict(exclude_unset=True).items():
        setattr(party, field, value)
    
    # If date_time was updated, reschedule the reminder
    if party_update.date_time and party_update.date_time != old_date_time:
        party_scheduler.remove_party_reminder(party_id)
        party_scheduler.schedule_party_reminder(party_id, party_update.date_time)
    
    db.commit()
    db.refresh(party)
    return party

@app.delete("/parties/{party_id}/attendees/{user_id}")
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

@app.get("/parties", response_model=List[schemas.Party])
def list_parties(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Party).all()

@app.post("/parties/{party_id}/join-request")
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
            status='pending'
        )
    )
    
    # Notify party creator
    background_tasks.add_task(
        email_service.send_email,
        party.creator.email,
        f"New Join Request",
        f"{current_user.username} has requested to join your party!"
    )
    
    db.commit()
    return {"message": "Join request sent successfully"}