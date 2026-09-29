

from schemas.vendor_schema import ApplicationStatusUpdate
from schemas.vendor_schema import VendorApplicationSchema,VendorApplicationResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import VendorApplication
from config import get_db
from routes.utils import get_current_user, format_vendor_response
from uuid import UUID
from sqlalchemy import select




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



    




