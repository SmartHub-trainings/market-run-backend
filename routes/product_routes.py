

from schemas.product_schema import ProductCreate
from schemas.vendor_schema import ApplicationStatusUpdate
from schemas.vendor_schema import VendorApplicationSchema,VendorApplicationResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product
from config import get_db
from routes.utils import get_current_user, format_vendor_response
from uuid import UUID
from sqlalchemy import select




product_router = APIRouter(tags=["Products"])

@product_router.post("/")
async def create_product_handler(
    body:ProductCreate, 
    db:AsyncSession=Depends(get_db), 
    user=Depends(get_current_user)):
    try:
        payload= body.model_dump()
        new_product= Product(
            **payload,
            user_id=user['user_id']
        )
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)

        return {
            "success": True,
            "status_code": 201,
            "data": new_product,
            "message" : "Product created successfully"
        }
    except HTTPException as e:
        print (e)
        raise HTTPException (
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong while creating your product"
        )
    except Exception as h:
        print("h:", h)
        raise HTTPException (
            status_code= 500,
            detail= "Internal Server Error"
        )
        
    