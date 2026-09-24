from dotenv import load_dotenv
import os



load_dotenv()

DATABASE_URL = os.getenv("DB_URL")
OTP_EXPIRATION=int(os.getenv("OTP_EXPIRATION"))
JWT_SECRET= os.getenv("JWT_SECRET")
JWT_EXP_MINS= int(os.getenv("JWT_EXP_MINS"))
