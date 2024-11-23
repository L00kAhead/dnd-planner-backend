from app.models import Party
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from app.email_service import EmailService
from app.database import SessionLocal


class PartyScheduler:
    """
    A class to manage scheduling of reminders for D&D parties.

    Attributes:
        scheduler (BackgroundScheduler): The APScheduler instance for managing scheduled jobs.
        email_service (EmailService): The email service used to send reminder emails.
    """

    def __init__(self):
        """
        Initialize the PartyScheduler.

        Starts the background scheduler and sets up the email service for sending reminders.
        """
        self.scheduler = BackgroundScheduler()
        self.email_service = EmailService()
        self.scheduler.start()

    def schedule_party_reminder(self, party_id: int, party_time: datetime):
        """
        Schedule a reminder email for a D&D party.

        Args:
            party_id (int): The unique ID of the party.
            party_time (datetime): The date and time of the party.

        Side Effects:
            - Adds a job to the scheduler to send a reminder email 1 hour before the party.

        Notes:
            - A reminder is scheduled only if the reminder time is in the future.
        """
        reminder_time = party_time - timedelta(hours=1)
        if reminder_time > datetime.now():
            self.scheduler.add_job(
                self._send_party_reminder,
                trigger=DateTrigger(run_date=reminder_time),
                args=[party_id],
                id=f"party_reminder_{party_id}",
                replace_existing=True
            )

    def _send_party_reminder(self, party_id: int):
        """
        Internal method to send reminder emails to all attendees of a party.

        Args:
            party_id (int): The unique ID of the party.

        Side Effects:
            - Sends an email reminder to each attendee of the party.

        Notes:
            - Uses the database to fetch party details and attendees.
        """
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
        """
        Remove a scheduled reminder for a specific party.

        Args:
            party_id (int): The unique ID of the party.

        Side Effects:
            - Removes the scheduled job from the scheduler if it exists.
        """
        job_id = f"party_reminder_{party_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
