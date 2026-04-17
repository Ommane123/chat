import os
import smtplib
import random
from email.message import EmailMessage

def generate_otp():
    """Generates a random 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email, otp):
    """
    Sends an OTP to the given email address. 
    If SMTP variables are not set in the environment, it prints the OTP to the console 
    to prevent blocking development.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    # If not fully configured, fallback to console
    if not (smtp_host and smtp_user and smtp_pass):
        print("\n" + "="*50)
        print("🚨 SMTP Not Configured. Falling back to Console Output 🚨")
        print(f"Forgot Password OTP for {recipient_email}: {otp}")
        print("="*50 + "\n")
        return True
        
    try:
        msg = EmailMessage()
        msg.set_content(f"Your password reset OTP is: {otp}\n\nIt will expire in 15 minutes.")
        msg["Subject"] = "Password Reset OTP"
        msg["From"] = smtp_user
        msg["To"] = recipient_email
        
        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
