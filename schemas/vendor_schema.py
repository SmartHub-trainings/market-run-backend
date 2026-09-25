
from pydantic import BaseModel,Field
from datetime import datetime


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
    id: str
    user_id: str
    created_at:datetime
    updated_at:datetime
    

class VendorApplicationResponse(BaseModel):
    success:bool
    status_code:int
    data:VendorApplicationWithId
    message:str
    


    

