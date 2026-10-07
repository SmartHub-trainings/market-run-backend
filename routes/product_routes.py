

from schemas.product_schema import ProductCreate
from schemas.vendor_schema import ApplicationStatusUpdate
from schemas.vendor_schema import VendorApplicationSchema,VendorApplicationResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product,VendorApplication
from config import get_db
from routes.utils import get_current_user
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload




product_router = APIRouter(tags=["Products"])

@product_router.post("/")
async def create_product_handler(
    body:ProductCreate, 
    db:AsyncSession=Depends(get_db), 
    current_user=Depends(get_current_user)):
    try:
        store_query = select(VendorApplication).where(VendorApplication.id == body.store_id)
        store = (await db.execute(store_query)).scalar_one_or_none()
        if not store:
            raise HTTPException(
                status_code=404,
                detail="Store not found",
            )
        if store.status != "approved":
            raise HTTPException(
                status_code=403,
                detail="Store is not approved",
            )
        payload= body.model_dump()
        new_product= Product(
            **payload,
            user_id=current_user['user_id']
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


@product_router.get("/")
async def get_all_products_handler(db:AsyncSession=Depends(get_db)): 
    try:
        #load the stores while getting the products
        query= (select(Product)
                .options(selectinload(Product.store))
                .where(Product.status=="published"))
                
        products = (await db.execute(query)).scalars().all()
        return {
            "success": True,
            "status_code": 200,
            "data": products,
            "message" : "Products retrieved successfully"
        }
    except HTTPException as e:
       
        raise HTTPException (
            status_code= e.status_code,
            detail= e.detail
        )
    except Exception as h:
        print(e)
        raise HTTPException (
            status_code= 500,
            detail= "Internal Server Error"
        )
        
    