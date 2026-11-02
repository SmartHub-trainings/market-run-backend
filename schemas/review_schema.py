from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

class ReviewCreate(BaseModel):
    product_id: UUID
    rating: int= Field(..., ge=1, le=5)
    text: str | None = None
    
    
class ReviewStatusUpdate(BaseModel):   
    status: Literal["public", "archive"] = "public"

class ReviewReplyHandler(BaseModel):
    review_id: UUID
    reply: str = Field(..., min_length=2, max_length=2000)
