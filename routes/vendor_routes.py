

from schemas.vendor_schema import ApplicationStatusUpdate
from schemas.vendor_schema import VendorApplicationSchema,VendorApplicationResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import VendorApplication, Order, OrderItem, Product, User
from config import get_db
from utils import get_current_user, format_vendor_response
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria





vendor_router = APIRouter(tags=["Vendors"])

@vendor_router.post("/applications")
async def create_vendor_application_handler(
    body:VendorApplicationSchema, 
    db:AsyncSession=Depends(get_db), 
    user=Depends(get_current_user)) -> VendorApplicationResponse:
    try:
        payload= body.model_dump()
        payload['bank_account_name']= payload['bank_details']['bank_account_name']
        payload['bank_account_number']= payload['bank_details']['bank_account_number']
        payload['bank_name']= payload['bank_details']['bank_name']
        del payload['bank_details']
        new_application= VendorApplication(
            **payload,
            user_id=user['user_id']
        )
        db.add(new_application)
        await db.commit()
        await db.refresh(new_application)

        return {
            "success": True,
            "status_code": 201,
            "data": format_vendor_response(new_application),
            "message" : "Application submitted successfully"
        }
    except HTTPException as e:
        print (e)
        raise HTTPException (
            status_code= e.status_code or 500,
            detail= e.detail or "Something went wrong while submitting your application"
        )
    except Exception as h:
        print("h:", h)
        raise HTTPException (
            status_code= 500,
            detail= "Internal Server Error"
        )

@vendor_router.patch("/{application_id}/status")
async def update_application_status(
    application_id:UUID,
    data: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VendorApplication).where(VendorApplication.id == application_id)
    )

    application = result.scalar_one_or_none()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    # if application.status != "pending":
    #     raise HTTPException(
    #         status_code=404,
    #         detail=f"Application has already been {application.status}",
    #     )


    application.status = "approved" if data.status=="accept" else "rejected"
    # if data.status== "accept":
    #     application.status = "approved"
    # else:
    #     application.status = "rejected"

    await db.commit()
    await db.refresh(application)

    return {
        "message": f"Application {data.status.value} successfully",
        "success": True,
        "status_code": 200,
        "data": {
            "id": application.id,
            "status": application.status,
        },
    }



@vendor_router.get("/stores")
async def get_vendor_stores(current_user=Depends(get_current_user),db:AsyncSession=Depends(get_db)):
    current_user_id =current_user.get("user_id")

    query= (select(VendorApplication)
            .where(VendorApplication.user_id==current_user_id))

    applications = (await db.execute(query)).scalars().all()
    
    return {
        "message": "Vendor applications retrieved successfully",
        "success": True,
        "status_code": 200,
        "data": applications,
    }
    
@vendor_router.get("/orders")
async def get_vendor_orders(db:AsyncSession=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        query= select(VendorApplication).where(VendorApplication.user_id==current_user["user_id"])
        vendor= (await db.execute(query)).scalar_one_or_none()
        if not vendor:
            raise HTTPException(
                status_code= 403,
                detail= "Only approved vendors can access this endpoint"
            )
        if vendor.status != "approved":
            raise HTTPException(
                status_code= 403,
                detail= "Only approved vendors can access this endpoint"
            )
        vendor_id= current_user["user_id"]
        query= (select(Order)
        .options(selectinload(Order.items)
        .selectinload(OrderItem.product)
        .selectinload(Product.user),
        with_loader_criteria(OrderItem, OrderItem.product.has(Product.user_id==vendor_id),
                include_aliases=True))
        .where(Order.items.any(
        OrderItem.product.has(
            Product.user_id==vendor_id
                )
            )
        )
    )
        orders= (await db.execute(query)).scalars().all()

        return{
        "message": "Vendor orders retrieved successfully",
        "success": True,
        "status_code": 200,
        "data": orders,
        }
    except HTTPException as e:
        print("get_vendor_orders_HTTP_error:", e)
        raise HTTPException(
            status_code= e.status_code or 500,
            detail= e.detail or "An error occured while trying to get vendor orders"
        )
    except Exception as f:
        print("get_vendor_orders_general_error:", f)
        raise HTTPException(
            status_code= 500,
            detail= "Internal Server Error"
        )

        
    



    




