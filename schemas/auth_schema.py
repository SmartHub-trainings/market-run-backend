from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    email:EmailStr
    first_name:str
    last_name:str
    phone:str
    password:str

class LoginSchema(BaseModel):
    email:EmailStr
    password:str