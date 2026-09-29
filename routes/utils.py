from schemas.vendor_schema import VendorApplicationSchema
from schemas.auth_schema import GenerateOTP
from datetime import datetime,timedelta
from random import choices
from secret import OTP_EXPIRATION, JWT_SECRET
import jwt
from config import bearer_scheme
from fastapi import HTTPException, Depends


def generate_otp()->GenerateOTP:
    otp = "".join(choices("0123456789",k=6))
    expires_at = datetime.now()+ timedelta(minutes=OTP_EXPIRATION)
    return GenerateOTP(
        otp=otp,
        expires_at=expires_at
    )

def verify_token(token:str):
    try:
        print("tokens:", token )
        payload= jwt.decode(token, JWT_SECRET, algorithms= ['HS256'])
        return payload
    except jwt.ExpiredSignatureError as e:
        print("f:", e)
        raise HTTPException (
            status_code= 401,
            detail= "Session has expired, please Login to continue"
        )
    except jwt.InvalidTokenError as e:
        print ("g:", e)
        raise HTTPException (
            status_code= 401,
            detail= "Invalid token, try again"
        )

def get_current_user(cred= Depends(bearer_scheme)):
    try:
        token=cred.credentials
        print("token:",token)
        result= verify_token(token)
        print("result:", result)
        if not result:
            raise HTTPException (
                status_code= 401,
                detail= "Invalid Token, Logout and try again"
            )
        return result
    except HTTPException as f:
        print(f)
        raise HTTPException (
            status_code= f.status_code or 500,
            detail= f.detail or "Something went wrong"
        )
    except Exception:
        raise HTTPException (
            status_code= 500,
            detail= "Internal Server Error"
        )


def format_vendor_response(application:VendorApplicationSchema):
    return {
            "store_name": application.store_name,
            "category": application.category,
            "description": application.description,
            "status": application.status,
            "bank_details": {
                "bank_name": application.bank_name,
                "bank_account_number": application.bank_account_number,
                "bank_account_name": application.bank_account_name
            },
        "id": application.id,
        "user_id": application.user_id,
        "created_at": application.created_at,
        "updated_at": application.updated_at
    }