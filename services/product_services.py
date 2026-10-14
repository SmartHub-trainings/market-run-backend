from fastapi import HTTPException
from models import VendorApplication
from schemas.product_schema import ProductCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from models import Product


async def get_product_by_id(db:AsyncSession,product_id:UUID):
    product_query = select(Product).where(Product.id == product_id)
    product = (await db.execute(product_query)).scalar_one_or_none()
    return product



async def create_product_service(db:AsyncSession,body:ProductCreate,current_user_id:UUID):
    store_query = select(VendorApplication).where(VendorApplication.id == body.store_id)
    store = (await db.execute(store_query)).scalar_one_or_none()
    if not store:
        raise HTTPException(
            status_code=404,
            detail="Store not found",
        )
    if store.status != "approved":
        raise HTTPException(
            status_code=403,
            detail="Store is not approved",
        )
    payload= body.model_dump()
    new_product= Product(
        **payload,
        user_id=current_user_id
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product