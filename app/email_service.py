import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os 


class EmailService:
    def __init__(self):
        self.sender_email = os.getenv('EMAIL_USER')
        self.password = os.getenv('EMAIL_PASSWORD')
        
    def send_email(self, recipient_email: str, subject: str, body: str):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.office365.com", 465) as server:
            server.login(self.sender_email, self.password)
            server.send_message(message)
