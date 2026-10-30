

from datetime import datetime,timedelta
from fastapi import HTTPException
from fastapi import APIRouter,Depends
from models import User,UserOTP,VendorApplication
from schemas.auth_schema import RegisterSchema,LoginSchema,VerifyEmailSchema,ResendOTPSchema
from schemas.vendor_schema import ApplicationStatusUpdate
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from config import password_context, get_db
from secret import OTP_EXPIRATION, JWT_EXP_MINS, JWT_SECRET
from sqlalchemy.orm import selectinload
import jwt
from utils import generate_otp,get_current_user
from services.auth_services import (create_user_service,login_user_service,verify_email_service,
resend_otp_service,get_current_user_service)

auth_router = APIRouter(tags=["Authentication"])


@auth_router.post("/register")
async def register(payload: RegisterSchema, db:AsyncSession=Depends(get_db)):
    try:

        new_user,otp = await create_user_service(db,payload)
        ## send email to the user
        return {
            "message":"User created successfully",
            "data":{"user":new_user,"otp":otp}
        }
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=e.status_code or 500,
        detail =e.detail or "Internal Server Error")
        
    except Exception as e:
        await db.rollback()
        print (e) 
        raise HTTPException(status_code= 500, detail= "Something went wrong")



@auth_router.post("/login")
async def login(payload: LoginSchema,db:AsyncSession=Depends(get_db)):
    try:

        data= await login_user_service(db,payload)

        return {
            "message": "Login successful",
            "data": data
        }

    except HTTPException as e:
        print (e)
        raise HTTPException (
            status_code= e.status_code or 500, 
            detail= e.detail or "Internal server error"
        )
    except Exception as f:
        print (f)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )


@auth_router.post("/verify-email")
async def verify_user_otp(
    payload: VerifyEmailSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        user= await verify_email_service(db,payload)
        ## send  welcome email
        return {
            "message": "Email verified successfully",
            "statusCode":200,
            "data": user,
            "success":True
        }

    except HTTPException as e:
         raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.detail or "An error occurred while verifying email"
        )




@auth_router.post("/resend-otp")
async def resend_otp(body:ResendOTPSchema, db:AsyncSession=Depends(get_db)):
    try:
        new_otp= await resend_otp_service(db,body)
        ## send email to the user

        return {
            "message": "OTP resent",
            "data": new_otp,
            "statusCode":200,
            "success":True
        }

    
    except HTTPException as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.detail or "An error occurred while resend OTP"
        )

@auth_router.get("/me")
async def get_current_user_handler(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    try:
        user= await get_current_user_service(db,current_user["user_id"])

        # store_query = select(VendorApplication).where(VendorApplication.user_id==user.user_id)
        # stores = (await db.execute(store_query)).scalars().all()
        
        
        return {
            "message":"Profile fetched successfully",
            "data":user,
            "success":True,
            "status_code":200
        }
    except HTTPException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )  

    