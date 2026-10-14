

from services.product_services import create_product_service
from services.product_services import get_product_by_id
from uuid import UUID
from schemas.product_schema import ProductCreate,ProductUpdateStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product,VendorApplication
from config import get_db
from routes.utils import get_current_user
from sqlalchemy import select
from sqlalchemy.orm import selectinload




product_router = APIRouter(tags=["Products"])

@product_router.post("/")
async def create_product_handler(
    body:ProductCreate, 
    db:AsyncSession=Depends(get_db), 
    current_user=Depends(get_current_user)):
    try:
        new_product=await create_product_service(db,body,current_user['user_id'])

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
                .options(selectinload(Product.store),selectinload(Product.user))
                # .where(Product.status=="published")
                )
                
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

        
@product_router.patch("/{product_id}/status")
async def update_product_status(body:ProductUpdateStatus,
                            product_id:UUID,
                            db:AsyncSession=Depends(get_db), 
                            current_user=Depends(get_current_user)):
    try:
        product =await get_product_by_id(db,product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        if product.user_id !=current_user['user_id']:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to update this product",
            )
        product.status = body.status
        await db.commit()
        await db.refresh(product)
        return {
            "success": True,
            "status_code": 200,
            "data": product,
            "message" : "Product status updated successfully"
        }
    except HTTPException as e:
        print (e)
        raise HTTPException (
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong while updating your product status"
        )
    except Exception as h:
        print("h:", h)
        raise HTTPException (
            status_code= 500,
            detail= "Internal Server Error"
        )



@product_router.get("/{product_id}")
async def get_product_handler(product_id:UUID,db:AsyncSession=Depends(get_db)):
    try:
        product = await get_product_by_id(db,product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )
        return {
            "success": True,
            "status_code": 200,
            "data": product,
            "message" : "Product retrieved successfully"
        }
    except HTTPException as e:
        print (e)
        raise HTTPException (
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong while retrieving your product"
        )
    except Exception as h:
        print("h:", h)
        raise HTTPException (
            status_code= 500,
            detail= "Internal Server Error"
        )
    