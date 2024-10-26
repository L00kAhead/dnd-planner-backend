import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.sender_email = ""  # Your Gmail address
        self.password = ""   # Your App Password

    def send_email(self, recipient_email: str, subject: str, body: str):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        # Using Gmail's SMTP settings
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.sender_email, self.password)
            server.send_message(message)

# Example usage
# if __name__ == "__main__":
#     email_service = EmailService()
#     email_service.send_email("lorexo2907@evasud.com", "Test Subject", "Test Body")