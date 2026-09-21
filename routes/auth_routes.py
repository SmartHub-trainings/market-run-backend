

from datetime import datetime,timedelta
from fastapi import HTTPException
from fastapi import APIRouter,Depends
from schemas.auth_schema import RegisterSchema,LoginSchema,VerifyEmailSchema
from models import User,get_db,UserOTP
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from random import choices

auth_router = APIRouter(tags=["Authentication"])



@auth_router.post("/register")
async def register(payload: RegisterSchema, db:AsyncSession=Depends(get_db)):
    try:
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
        new_user = User(**payload.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh()
        new_otp = "".join(choices("0123456789",k=6))
        expires_at = datetime.now()+ timedelta(minutes=1)

        otp = UserOTP(
            user_id=new_user.user_id,
            otp=new_otp,
            expires_at=expires_at

        )

        db.add(otp)
        await db.commit()
        await db.refresh()

        return {
            "message":"User created successfully",
            "data":{"user":new_user,"otp":otp}
        }
    except HTTPException as e:
        print(e)
        raise HTTPException(status_code=e.status_code or 500,
        detail =e.detail or "Internal Server Error")
        
    



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

        user_query = select(User).where(User.id == otp_exists.user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.is_verified = True

        await db.commit()

        return {
            "message": "Email verified successfully"
        }

    except HTTPException:
        raise

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail="An error occurred while verifying email"
        )