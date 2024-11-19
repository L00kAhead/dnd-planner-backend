import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class EmailService:
    """
    A service for sending emails using Gmail's SMTP server.

    Attributes:
        sender_email (str): The Gmail address used for sending emails.
        password (str): The application-specific password for the Gmail account.
    """
    def __init__(self):
        """
        Initialize the EmailService.

        Loads the sender's email and password from environment variables.
        """
        self.sender_email = os.getenv("EMAIL_USER")  # Your Gmail address
        self.password = os.getenv("EMAIL_PASSWORD") # Your App Password

    def send_email(self, recipient_email: str, subject: str, body: str):
        """
        Send an email to the specified recipient.

        Args:
            recipient_email (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body of the email.

        Raises:
            smtplib.SMTPException: If an error occurs during the email sending process.
        """
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
    # print(email_service.sender_email, email_service.password)
    # email_service.send_email("lorexo2907@evasud.com", "Test Subject", "Test Body")