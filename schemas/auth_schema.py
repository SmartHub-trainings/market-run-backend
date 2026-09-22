from pydantic import BaseModel, EmailStr,Field

class RegisterSchema(BaseModel):
    email:EmailStr
    first_name:str
    last_name:str
    phone:str
    password:str

class LoginSchema(BaseModel):
    email:EmailStr
    password:str


class VerifyEmailSchema(BaseModel):
    email:EmailStr
    otp:str = Field(..., min_length=6, max_length=6)