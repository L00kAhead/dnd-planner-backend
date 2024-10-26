from app.models import Party
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from app.email_service import EmailService
from app.database import SessionLocal


class PartyScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
        self.scheduler.start()

    def schedule_party_reminder(self, party_id: int, party_time: datetime):
        reminder_time = party_time - timedelta(hours=1)
        if reminder_time > datetime.now():
            self.scheduler.add_job(
                self._send_party_reminder,
                trigger=DateTrigger(run_date=reminder_time),
                args=[party_id],
                id=f"party_reminder_{party_id}"
            )

    def _send_party_reminder(self, party_id: int):
        db = SessionLocal()
        try:
            party = db.query(Party).filter(Party.id == party_id).first()
            if party:
                # Send reminder to all attendees
                for attendee in party.attendees:
                    self.email_service.send_email(
                        recipient_email=attendee.email,
                        subject=f"Reminder: D&D Party '{party.title}' starts in 1 hour!",
                        body=f"""
                        Hello {attendee.username}!

                        This is a reminder that the D&D party '{party.title}' starts in 1 hour!
                        
                        Details:
                        Time: {party.date_time}
                        Platform: {party.platform}
                        Description: {party.description}
                        
                        Don't forget to join on time!
                        """
                    )
        finally:
            db.close()

    def remove_party_reminder(self, party_id: int):
        job_id = f"party_reminder_{party_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
