
from pydantic import BaseModel,Field
from datetime import datetime
from uuid import UUID
from enum import Enum




class ProductCreate(BaseModel):
    name:str
    description:str
    price:float
    category:str
    images:list[str]
    stock:int
