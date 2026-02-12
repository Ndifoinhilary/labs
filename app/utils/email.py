# app/utils/email.py
import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

async def send_email(to: str, subject: str, body: str):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD):
        # In dev, you can print instead of sending for now
        print(f"[DEV EMAIL] To: {to}\nSubject: {subject}\n{body}")
        return

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
    )