import smtplib
from email.mime.text import MIMEText
import os
import random
from datetime import datetime, timedelta

def generate_otp():
    return str(random.randint(100000,999999))

def send_otp_email(to_email, otp_code):
    sender_email = os.getenv('EMAIL_ADDRESS')
    sender_password = os.getenv('EMAIL_APP_PASSWORD')

    subject = "Your Expense Tracker Verification Code"
    body = f"Your verification code is: {otp_code}\n\nThis code expires in 10 minutes."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email,sender_password)
        server.send_message(msg)