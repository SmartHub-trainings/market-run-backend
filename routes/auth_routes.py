from fastapi import APIRouter
from schemas.auth_schema import RegisterSchema,LoginSchema

auth_router = APIRouter(tags=["Authentication"])



@auth_router.post("/register")
def register(user: RegisterSchema):
    return {
    "message": "Register",
    "username": user.username,
    "email": user.email
    }



@auth_router.post("/login")
def login(user: LoginSchema):
    return {
        "message": "Login successful",
        "username": user.username
    }