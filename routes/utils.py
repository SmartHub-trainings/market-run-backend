from schemas.auth_schema import GenerateOTP
from datetime import datetime,timedelta
from random import choices
from secret import OTP_EXPIRATION


def generate_otp()->GenerateOTP:
    otp = "".join(choices("0123456789",k=6))
    expires_at = datetime.now()+ timedelta(minutes=OTP_EXPIRATION)
    return GenerateOTP(
        otp=otp,
        expires_at=expires_at
    )

