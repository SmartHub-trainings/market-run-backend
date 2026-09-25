

from datetime import datetime
from fastapi import HTTPException
from fastapi import APIRouter,Depends
from models import User,UserOTP
from schemas.auth_schema import RegisterSchema,LoginSchema,VerifyEmailSchema,ResendOTPSchema
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from config import password_context, get_db
from routes.utils import generate_otp

auth_router = APIRouter(tags=["Authentication"])


@auth_router.post("/register")
async def register(payload: RegisterSchema, db:AsyncSession=Depends(get_db)):
    try:
        # async with db.begin():

        user_query = select(User).where(User.email==payload.email)
        user_exists = (await db.execute(user_query)).scalar_one_or_none()
            
        if user_exists:
            raise HTTPException(status_code=409,
            detail="User with this detail already Exist")

        # new_user = User(
        #     email=payload.email,
        #     first_name=payload.first_name,
        #     last_name=payload.last_name,
        #     password=payload.password
        # )
        new_user = User(**payload.model_dump(exclude={"password"}),
                        password= password_context.hash(payload.password)
        )
        db.add(new_user)
        await db.flush()
        otp_result=generate_otp()

        new_otp = otp_result.otp
        expires_at = otp_result.expires_at

        otp = UserOTP(
            user_id=new_user.user_id,
            otp=new_otp,
            expires_at=expires_at

        )

        db.add(otp)
        await db.commit()
        await db.refresh(new_user)
        await db.refresh(otp)
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

    user_query = select(User).where(User.email==payload.email)
    user = (await db.execute(user_query)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401,detail="Invalid credientail")

    if not user.email_is_verified:
        raise HTTPException(status_code=401,detail="Email not verified. Please, verify your email")
    return {
        "message": "Login successful",
        "username": user
    }

@auth_router.post("/verify-email")
async def verify_user_otp(
    payload: VerifyEmailSchema,
    db: AsyncSession = Depends(get_db)
):
    try:
        otp = payload.otp

        otp_query = select(UserOTP).where(UserOTP.otp == otp)
        result = await db.execute(otp_query)
        otp_exists = result.scalar_one_or_none()

        if not otp_exists:
            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        if otp_exists.expires_at < datetime.now():
            raise HTTPException(
                status_code=400,
                detail="OTP has expired"
            )

        user_query = select(User).where(User.user_id == otp_exists.user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )


        user.email_is_verified = True

        await db.commit()

        ## send  welcome email

        return {
            "message": "Email verified successfully",
            "statusCode":200,
            "data": user,
            "susccess":True
        }

    except HTTPException as e:
         raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.detail or "An error occurred while verifying email"
        )




@auth_router.post("/resend-otp")
async def resend_otp(body:ResendOTPSchema, db:AsyncSession=Depends(get_db)):
    try:
        user_query = select(User).where(User.email==body.email)
        user = (await db.execute(user_query)).scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404,detail="Your account does not exist. Please, register again.")
            
        otp_query= select(UserOTP).where(UserOTP.user_id==user.user_id)
        otp_exists= (await db.execute(otp_query)).scalar_one_or_none()
        if otp_exists:
            await db.execute(delete(UserOTP).where(UserOTP.user_id==user.user_id))

        otp_result = generate_otp()
       
        new_otp = UserOTP(
            otp=otp_result.otp,
            user_id=user.user_id,
            expires_at = otp_result.expires_at)

        db.add(new_otp)

        await db.commit()
        await db.refresh(new_otp)

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