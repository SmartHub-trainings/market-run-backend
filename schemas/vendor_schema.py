
from pydantic import BaseModel,Field
from datetime import datetime
from uuid import UUID
from enum import Enum


"""
Vendors submit an application containing storefront name, category,
 description, bank account details, 
and a business-owner name. Applications enter a pending queue for admin review.
"""


class BankAccountDetails(BaseModel):
    bank_name:str
    bank_account_number:str = Field(...,max_length=10,min_length=10)
    bank_account_name:str

class VendorApplicationSchema(BaseModel):
    store_name: str
    category:str
    description:str
    bank_details:BankAccountDetails

class VendorApplicationWithId(VendorApplicationSchema):
    id: UUID
    user_id: UUID
    status:str
    created_at:datetime
    updated_at:datetime
    

class VendorApplicationResponse(BaseModel):
    success:bool
    status_code:int
    data:VendorApplicationWithId
    message:str

class ApplicationStatusUpdateEnums(str,Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    
    
class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatusUpdateEnums

    
    


    

