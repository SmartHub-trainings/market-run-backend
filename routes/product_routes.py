

from services.product_services import create_product_service,get_product_by_id,get_all_products_service
from uuid import UUID
from schemas.product_schema import ProductCreate,ProductUpdateStatus
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product,VendorApplication
from config import get_db
from utils import get_current_user
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Literal



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




#Buyers can filter by category, price range, vendor, and in-stock status. 
#Buyers can sort by newest, price ascending, price descending, and popularity.
#Buyers can search the catalog with free-text queries. Search matches product name, description, and 
#vendor storefront name, ranked by relevance.

@product_router.get("/")
async def get_all_products_handler(
    page:int|None=1,
    pageSize:int|None=5,
    db:AsyncSession=Depends(get_db),
    category:str|None=None,
    min_price:float|None=None,
    max_price:float|None=None,
    vendor:UUID|None=None,
    in_stock:Literal["true", "false"]|None=None,
    sort_by:Literal["newest", "price_ascending", "price_descending"]|None="newest",
    search:str|None=None
    ): 
    try:
        #load the stores while getting the products
                
        products,no_of_pages,page_size =await get_all_products_service(
            db,page,pageSize,category,min_price,max_price,vendor,in_stock,sort_by,search)
        return {
            "success": True,
            "status_code": 200,
            "data": products,
            "message" : "Products retrieved successfully",
            "no_of_pages" : no_of_pages
        }
    except HTTPException as e:
       
        raise HTTPException (
            status_code= e.status_code,
            detail= e.detail
        )
    except Exception as h:
        print(h)
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
    