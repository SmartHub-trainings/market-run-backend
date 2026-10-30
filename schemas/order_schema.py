
from pydantic import BaseModel,Field
from uuid import UUID


class CartItemCreate(BaseModel):
    product_id:UUID
    qty:int= Field(1,ge=1)
