from dotenv import load_dotenv
load_dotenv()

from email_utils import generate_otp, send_otp_email

test_email = "wadikarsaniya@gmail.com"

code = generate_otp()
print(f"Generated code: {code}")
print(f"Sending to: {test_email}")

try:
    send_otp_email(test_email, code)
    print("Email sent successfully! Check your inbox (and spam folder).")
except Exception as e:
    print(f"Failed to send email: {e}")