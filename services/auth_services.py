from fastapi import HTTPException
from models import User,UserOTP
from schemas.auth_schema import RegisterSchema,LoginSchema,VerifyEmailSchema,ResendOTPSchema
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from config import password_context
from utils import generate_otp
from datetime import datetime,timedelta
from secret import JWT_EXP_MINS, JWT_SECRET
import jwt
from uuid import UUID


async def create_user_service(db:AsyncSession, payload:RegisterSchema):
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
        return (new_user, otp)


async def login_user_service(db:AsyncSession, payload:LoginSchema):
    user_query = select(User).where(User.email==payload.email)
    user = (await db.execute(user_query)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401,detail="Invalid credentials")

    if not user.email_is_verified:
        raise HTTPException(status_code=401,detail="Email not verified. Please, verify your email")

    is_password = password_context.verify(payload.password,user.password)
    if not is_password:
        raise HTTPException (status_code= 401, detail= "Invalid credentials")
        
    jwt_payload= {
        "user_id": str(user.user_id),
        #"role": user.role,
        "exp": (datetime.now() + timedelta(minutes= JWT_EXP_MINS)).timestamp()
    }

    token= jwt.encode(jwt_payload, JWT_SECRET, algorithm= 'HS256')
    data= {
        "access_token": token,
        "user": user
    }
    return data


async def verify_email_service(db:AsyncSession, payload:VerifyEmailSchema):
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
    return user



async def resend_otp_service(db:AsyncSession, body:ResendOTPSchema):
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
    return new_otp



async def get_current_user_service(db:AsyncSession, current_user_id:UUID):
    user_query = (select(User)
                        .where(User.user_id == current_user_id)
                        .options(selectinload(User.stores)))

    user = (await db.execute(user_query)).scalar_one_or_none()
    return user
