import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

load_dotenv()  # ← загружает .env файл

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)


async def send_verification_email(email: str, code: str) -> None:
    message = MessageSchema(
        subject="Your Verification Code — Dwelve",
        recipients=[email],
        body=f"Your verification code is: {code}\n\nCode expires in 10 minutes.",
        subtype=MessageType.plain
    )
    fm = FastMail(conf)
    await fm.send_message(message)