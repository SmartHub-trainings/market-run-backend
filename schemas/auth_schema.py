from pydantic import BaseModel, EmailStr,Field, field_validator, model_validator
from datetime import datetime
import re
import phonenumbers


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
    confirm_password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        return value


    @model_validator(mode="after")
    def confirm_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("phone")
    @classmethod
    def validate_phoneno(cls, value):
        try:
            phone_no= phonenumbers.parse(value, "NG")
            if not phonenumbers.is_valid_number(phone_no):
                raise ValueError("Enter a valid phone number.")
            return phonenumbers.format_number(
                phone_no,
                phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Enter a valid phone number")

class LoginSchema(ResendOTPSchema):
    password:str


class VerifyEmailSchema(BaseModel):
    otp:str = Field(..., min_length=6, max_length=6)


