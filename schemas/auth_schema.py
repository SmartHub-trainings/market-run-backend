from pydantic import BaseModel, EmailStr,Field
from datetime import datetime

class GenerateOTP(BaseModel):
    otp:str
    expires_at:datetime
     


class ResendOTPSchema(BaseModel):
    email: EmailStr
class RegisterSchema(ResendOTPSchema):
    first_name:str
    last_name:str
    phone:str
    password:str

class LoginSchema(ResendOTPSchema):
    password:str


class VerifyEmailSchema(ResendOTPSchema):
    otp:str = Field(..., min_length=6, max_length=6)

