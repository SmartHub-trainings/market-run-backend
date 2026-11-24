from dotenv import load_dotenv
import os
from fastapi_mail import ConnectionConfig, FastMail




load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
OTP_EXPIRATION=int(os.getenv("OTP_EXPIRATION"))
JWT_SECRET= os.getenv("JWT_SECRET")
JWT_EXP_MINS= int(os.getenv("JWT_EXP_MINS"))

R2_BUCKET_NAME=os.getenv("R2_BUCKET_NAME")
R2_ACCESS_KEY_ID=os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY=os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME=os.getenv("R2_BUCKET_NAME")
R2_ENDPOINT=os.getenv("R2_ENDPOINT")

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)