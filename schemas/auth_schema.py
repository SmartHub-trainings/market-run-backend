from pydantic import BaseModel, EmailStr

class RegisterSchema(BaseModel):
    username: str
    email:EmailStr
    full_name:str |None = None
    password:str

class LoginSchema(BaseModel):
    username:str
    password:str