from fastapi import APIRouter

auth_router = APIRouter(tags=["Authentication"])



@auth_router.post("/register")
def register():
    return {"message": "Register"}



@auth_router.post("/login")
def login():
    return {"message": "Login"}