

from schemas.vendor_schema import VendorApplicationSchema,VendorApplicationResponse
from fastapi import APIRouter



vendor_router = APIRouter(tags=["Vendors"])

@vendor_router.post("/applications")
async def create_vendor_application_handler(body:VendorApplicationSchema) -> VendorApplicationResponse:
    return body

    




